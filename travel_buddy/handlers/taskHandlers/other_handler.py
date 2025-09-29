"""Handler for queries that don't match specialized handlers."""

from travel_buddy.handlers.base_handler import BaseHandler
from travel_buddy.models.response_models import HandlerTypeEnum


class OtherHandler(BaseHandler):
    """Handles queries that don't match any specialized handlers."""
    
    def __init__(self):
        super().__init__(
            task_type=HandlerTypeEnum.OTHER.value,
            description="Handles general queries and provides guidance for specialized travel assistance"
        )
    
    @property
    def prompt_template(self) -> str:
        return """You are a knowledgeable travel assistant who helps with general travel planning questions that don't require real-time data or external APIs.

I can help you with:
- General travel advice and tips
- Travel planning strategies
- Budget planning guidance
- Travel safety tips
- General destination information
- Travel document requirements
- Transportation options overview

I provide helpful, practical advice based on general travel knowledge. For specific, up-to-date information about destinations or weather-dependent packing advice, I'll guide you to ask more specific questions."""