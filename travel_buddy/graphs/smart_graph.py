"""Smart graph with task routing and specialized handlers."""

from typing import Dict, Any, Optional

from langgraph.graph import StateGraph, START, END

from ..handlers import TaskRouter
from travel_buddy.handlers.taskHandlers.other_handler import OtherHandler
from ..handlers.registry import registry
from ..memory import ConversationManager
from ..settings import settings
from ..types import HandlerType


def create_task_router() -> TaskRouter:
    """Create a task router with all available handlers."""
    handlers = registry.create_all_handlers()
    return TaskRouter(handlers)


def route_task(state: Dict[str, Any]) -> Dict[str, Any]:
    user_input = state.get("question", "")
    session_id = state.get("session_id", "default")
    conversation_manager = state.get("conversation_manager")
    
    if conversation_manager and not conversation_manager.get_session(session_id):
        conversation_manager.start_session(session_id)
    
    context = {}
    if conversation_manager:
        context = {
            "conversation_context": conversation_manager.build_context_prompt(session_id, user_input),
            "relevant_memories": conversation_manager.get_conversation_context(session_id).relevant_memories if conversation_manager.get_conversation_context(session_id) else [],
            "session_id": session_id
        }
    
    task_router = state.get("task_router", create_task_router())
    handler, confidence, classification_tags = task_router.route(user_input, context)
    
    state.update({
        "selected_handler": handler,
        "routing_confidence": confidence,
        "classification_tags": classification_tags,
        "context": context,
        "task_router": task_router
    })
    
    return state


def process_handler(state: Dict[str, Any]) -> Dict[str, Any]:
    handler = state.get("selected_handler")
    user_input = state.get("question", "")
    context = state.get("context", {})
    classification_tags = state.get("classification_tags", {})
    routing_confidence = state.get("routing_confidence", 0)
    
    if not handler or routing_confidence < 0.3:
        response = OtherHandler.process(user_input)
        state.update({
            "answer": response,
            "handler_used": HandlerType.OTHER.value,
            "confidence": 0.3
        })
        return state
    
    try:
        task_result = handler.process(user_input, context, classification_tags)
        
        state.update({
            "answer": task_result.response,
            "task_result": task_result,
            "handler_used": handler.task_type,
            "success": task_result.success,
            "confidence": task_result.confidence
        })
        
    except Exception as e:
        response = OtherHandler.process(user_input)
        state.update({
            "answer": response,
            "handler_used": HandlerType.OTHER.value,
            "confidence": 0.3
        })
        return state
    
    return state


def update_conversation_memory(state: Dict[str, Any]) -> Dict[str, Any]:
    conversation_manager = state.get("conversation_manager")
    session_id = state.get("session_id", "default")
    user_input = state.get("question", "")
    answer = state.get("answer", "")
    
    if conversation_manager and settings.enable_memory:
        try:
            metadata = {
                "handler_used": state.get("handler_used", HandlerType.OTHER.value),
                "routing_confidence": state.get("routing_confidence", 0.0),
                "confidence": state.get("confidence", 0.0),
                "classification_tags": state.get("classification_tags", {}),
                "success": state.get("success", True)
            }
            
            conversation_manager.add_turn(session_id, user_input, answer, metadata)
            
        except Exception as e:
            print(f"Warning: Could not update conversation memory: {e}")
    
    return state


def build_smart_graph() -> StateGraph:
    graph = StateGraph(dict)
    
    # Add nodes
    graph.add_node("route_task", route_task)
    graph.add_node("process_with_handler", process_handler)
    graph.add_node("update_memory", update_conversation_memory)
    
    # Add edges
    graph.add_edge(START, "route_task")
    graph.add_edge("route_task", "process_with_handler")
    graph.add_edge("process_with_handler", "update_memory")
    graph.add_edge("update_memory", END)
    
    return graph.compile()


def run_smart_graph(question: str, session_id: str = "default", 
                   conversation_manager: Optional[ConversationManager] = None) -> Dict[str, Any]:
    app = build_smart_graph()

    initial_state = {
        "question": question,
        "session_id": session_id,
        "conversation_manager": conversation_manager,
        "task_router": create_task_router()
    }
    
    return app.invoke(initial_state)