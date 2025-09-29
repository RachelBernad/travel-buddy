"""Processing nodes for handler execution and summary generation."""

from typing import Dict, Any
from travel_buddy.handlers import TaskRouter
from travel_buddy.handlers.taskHandlers.other_handler import OtherHandler
from travel_buddy.handlers.taskHandlers.summary_handler import SummaryHandler
from travel_buddy.handlers.registry import registry
from travel_buddy.models.response_models import HandlerTypeEnum, ChatContext
from travel_buddy.settings import settings


def create_task_router() -> TaskRouter:
    """Create a task router with all available handlers."""
    handlers = registry.create_all_handlers()
    return TaskRouter(handlers)


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
            "confidence": task_result.confidence,
            "validation_passed": False if settings.enable_validation else True
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
        answer = state.get("answer", "")
        
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
        chat_context.add_message("assistant", answer)

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
