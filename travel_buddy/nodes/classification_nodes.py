"""Classification and intent detection nodes."""

from typing import Dict, Any
from travel_buddy.handlers import TaskRouter
from travel_buddy.models.response_models import ChatContext


def create_task_router() -> TaskRouter:
    """Create a task router with all available handlers."""
    from travel_buddy.handlers.registry import registry
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
