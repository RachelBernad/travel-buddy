"""Handler for destination-related travel queries."""

from travel_buddy.handlers.base_handler import BaseHandler
from travel_buddy.models.response_models import HandlerTypeEnum


class DestinationHandler(BaseHandler):
    """Handles destination selection, information, and recommendations with web search capability."""
    
    def __init__(self):
        super().__init__(
            task_type=HandlerTypeEnum.DESTINATION.value,
            description="Handles destination selection, information, and recommendations with web search"
        )
    
    @property
    def prompt_template(self) -> str:
        return """You are a friendly and knowledgeable travel destination expert. Help travelers with destination recommendations, best times to visit, cultural insights, and practical travel information. 

Be conversational, enthusiastic, and specific in your recommendations. Share interesting details and tips that make destinations come alive. Use a warm, helpful tone as if you're talking to a friend planning their dream trip."""
