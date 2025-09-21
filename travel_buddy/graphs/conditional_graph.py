"""Conditional graph with API capabilities for weather and web search."""

from typing import Dict, Any, Optional
from langgraph.graph import StateGraph, START, END

from travel_buddy.handlers import TaskRouter
from travel_buddy.handlers.taskHandlers.other_handler import OtherHandler
from travel_buddy.handlers.taskHandlers.summary_handler import SummaryHandler
from travel_buddy.handlers.registry import registry
from travel_buddy.handlers.api_handlers import weather_handler, web_search_handler
from travel_buddy.memory import ConversationManager
from travel_buddy.settings import settings
from travel_buddy.models.response_models import HandlerTypeEnum, ChatContext


def create_task_router() -> TaskRouter:
    """Create a task router with all available handlers."""
    handlers = registry.create_all_handlers()
    return TaskRouter(handlers)


def classify_intent(state: Dict[str, Any]) -> Dict[str, Any]:
    """Classify user intent and determine API needs."""
    user_input = state.get("question", "")
    session_id = state.get("session_id", "default")
    conversation_manager = state.get("conversation_manager")
    # Get or create conversation context from conversation manager
    conversation_context = None
    if conversation_manager:
        conversation_context = conversation_manager.get_conversation_context(session_id)
    
    if conversation_manager and not conversation_manager.get_session(session_id):
        conversation_manager.start_session(session_id)
    
    # Use centralized context building from ConversationManager
    if conversation_manager:
        chat_context = conversation_manager.build_chat_context(session_id, user_input)
    else:
        # Fallback for when no conversation manager is available
        chat_context = ChatContext(messages=[])
        chat_context.add_message("system", "You are a helpful travel assistant.")
        chat_context.add_message("user", user_input)
    
    task_router = create_task_router()
    classification = task_router.route(user_input, chat_context)

    if classification.tags.location and conversation_context:
        conversation_context.current_topic = classification.tags.location
    
    state.update({
        "handler_state": classification.category,
        "routing_confidence": classification.confidence,
        "classification": classification,
        "conversation_context": conversation_context,
        "needs_weather_api": classification.tags.needs_weather_api,
        "needs_web_search": classification.tags.needs_web_search
    })
    
    return state


def fetch_weather_data(state: Dict[str, Any]) -> Dict[str, Any]:
    """Fetch weather data if needed."""
    classification = state.get("classification")
    conversation_context = state.get("conversation_context")
    
    location = classification.tags.location if classification else None
    if not location and conversation_context:
        location = conversation_context.current_topic
    
    if location:
        weather_data = weather_handler.get_weather(location)
        state["weather_data"] = weather_data
    else:
        state["weather_data"] = {"error": "No location available for weather data"}
    
    return state


def fetch_web_data(state: Dict[str, Any]) -> Dict[str, Any]:
    """Fetch web search data if needed."""
    user_input = state.get("question", "")
    classification = state.get("classification")
    conversation_context = state.get("conversation_context")
    
    # Build search query
    search_query = user_input
    location = classification.tags.location if classification else None
    if location:
        search_query = f"{user_input} {location}"
    
    web_data = web_search_handler.search(search_query, num_results=3)
    state["web_data"] = web_data
    
    return state


def process_with_handler(state: Dict[str, Any]) -> Dict[str, Any]:
    """Process the request with the appropriate handler."""
    handler_state = state.get("handler_state", HandlerTypeEnum.OTHER)
    user_input = state.get("question", "")
    classification = state.get("classification")
    conversation_context = state.get("conversation_context")
    conversation_manager = state.get("conversation_manager")
    session_id = state.get("session_id", "default")
    
    # Use centralized context building from ConversationManager
    if conversation_manager:
        chat_context = conversation_manager.build_chat_context(session_id, user_input)
    else:
        # Fallback for when no conversation manager is available
        chat_context = ChatContext(messages=[])
        chat_context.add_message("system", "You are a helpful travel assistant.")
        chat_context.add_message("user", user_input)
    
    # Get task router
    task_router = create_task_router()
    
    # Get handler based on classification
    handler = None
    if task_router and classification.confidence >= 0.3:
        handler = task_router.handlers.get(classification.category.value)
    
    if not handler:
        handler = OtherHandler()
        classification.category = HandlerTypeEnum.OTHER
    
    # Add API data to context if available
    enhanced_context = chat_context
    if state.get("weather_data"):
        weather_info = f"Weather data: {state['weather_data']}\n"
        enhanced_context.add_message("system", weather_info)
    
    if state.get("web_data"):
        web_info = f"Web search results: {state['web_data']}\n"
        enhanced_context.add_message("system", web_info)
    
    try:
        task_result = handler.process(user_input, enhanced_context, classification.tags)
        
        state.update({
            "answer": task_result.response,
            "task_result": task_result,
            "handler_used": classification.category.value,
            "success": task_result.success,
            "confidence": task_result.confidence
        })
        
    except Exception as e:
        # Fallback to general handler on error
        fallback_handler = OtherHandler()
        task_result = fallback_handler.process(user_input, enhanced_context, classification.tags)
        state.update({
            "answer": task_result.response,
            "task_result": task_result,
            "handler_used": HandlerTypeEnum.OTHER.value,
            "success": task_result.success,
            "confidence": task_result.confidence
        })
    
    return state


def generate_summary(state: Dict[str, Any]) -> Dict[str, Any]:
    """Generate conversation summary before saving to memory."""
    try:
        conversation_context = state.get("conversation_context")
        conversation_manager = state.get("conversation_manager")
        session_id = state.get("session_id", "default")
        answwer = state.get("answer", "")
        
        if not conversation_manager:
            return state

        # Build chat context for summary generation using recent conversation history
        chat_context = ChatContext(messages=[])
        chat_context.add_message("system", "this is the assistant answers to the user questions.")
        
        # Add conversation history for summary (use recent turns, not full history)
        conv_context = conversation_manager.get_conversation_context(session_id)
        if conv_context and conv_context.conversation_turns:
            for turn in conv_context.conversation_turns[-6:]:  # Last 6 turns for summary
                chat_context.add_message("assistant", turn.assistant_response)
        chat_context.add_message("assistant", answwer)


        summary_handler = SummaryHandler()
        summary_result = summary_handler.process("", chat_context, None)

        if summary_result.success and conversation_context:
            conversation_context.summary = summary_result.response
            state["conversation_context"] = conversation_context
        
        return state
        
    except Exception as e:
        from travel_buddy.logger import logger
        logger.error("Summary generation failed", error=str(e))
        return state


def update_conversation_memory(state: Dict[str, Any]) -> Dict[str, Any]:
    """Update conversation memory with the results."""
    conversation_manager = state.get("conversation_manager")
    session_id = state.get("session_id", "default")
    user_input = state.get("question", "")
    answer = state.get("answer", "")
    conversation_context = state.get("conversation_context")
    
    if conversation_manager and settings.enable_memory:
        try:
            metadata = {
                "handler_used": state.get("handler_used", HandlerTypeEnum.OTHER.value),
                "routing_confidence": state.get("routing_confidence", 0.0),
                "confidence": state.get("confidence", 0.0),
                "classification": state.get("classification"),
                "success": state.get("success", True),
                "current_location": conversation_context.current_topic if conversation_context else None,
                "used_weather_api": state.get("needs_weather_api", False),
                "used_web_search": state.get("needs_web_search", False),
                "summary" : conversation_context.summary if conversation_context.summary else None
            }
            
            # Let conversation manager handle everything
            conversation_manager.add_turn(session_id, user_input, answer, metadata)
            
            # Update conversation summary if available
            if conversation_context and conversation_context.summary:
                conversation_manager.update_session_summary(session_id, conversation_context.summary)
            
        except Exception as e:
            from travel_buddy.logger import logger
            logger.warning("Could not update conversation memory", error=str(e))
    
    return state


def should_fetch_additional_data(state: Dict[str, Any]) -> str:
    """Determine if weather data should be fetched."""
    if state.get("needs_weather_api", False) and settings.enable_weather_api:
        return "fetch_weather"
    elif state.get("needs_web_search", False) and settings.enable_web_search_api:
        return "fetch_web"
    else:
        return "process_handler"


def build_conditional_graph() -> StateGraph:
    """Build the conditional graph with API capabilities."""
    graph = StateGraph(dict)
    
    # Add nodes
    graph.add_node("classify_intent", classify_intent)
    graph.add_node("fetch_weather", fetch_weather_data)
    graph.add_node("fetch_web", fetch_web_data)
    graph.add_node("process_handler", process_with_handler)
    graph.add_node("generate_summary", generate_summary)
    graph.add_node("update_memory", update_conversation_memory)
    
    # Add edges with conditional routing
    graph.add_edge(START, "classify_intent")
    
    # Conditional routing from classification
    graph.add_conditional_edges(
        "classify_intent",
        should_fetch_additional_data,
        {
            "fetch_weather": "fetch_weather",
            "fetch_web": "fetch_web", 
            "process_handler": "process_handler"
        }
    )

    
    # From web fetch, go to processing
    graph.add_edge("fetch_web", "process_handler")
    graph.add_edge("fetch_weather", "process_handler")
    
    # From processing, go to summary generation
    graph.add_edge("process_handler", "generate_summary")
    
    # From summary, go to memory update
    graph.add_edge("generate_summary", "update_memory")
    
    # From memory update, end
    graph.add_edge("update_memory", END)
    
    return graph.compile()


def run_conditional_graph(question: str, session_id: str = "default", 
                         conversation_manager: Optional[ConversationManager] = None) -> Dict[str, Any]:
    """Run the conditional graph with API capabilities."""
    app = build_conditional_graph()

    initial_state = {
        "question": question,
        "session_id": session_id,
        "conversation_manager": conversation_manager,
    }
    
    return app.invoke(initial_state)
 