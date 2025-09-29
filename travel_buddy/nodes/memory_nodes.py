"""Memory management nodes for conversation history."""

from typing import Dict, Any
from travel_buddy.settings import settings
from travel_buddy.models.response_models import HandlerTypeEnum


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
                "summary": conversation_context.summary if conversation_context and conversation_context.summary else None,
                "was_corrected": state.get("was_corrected", False),
                "validation_passed": state.get("validation_passed", True)
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
