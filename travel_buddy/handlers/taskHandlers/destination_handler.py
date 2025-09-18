"""Handler for destination-related travel queries."""

from travel_buddy.handlers.base_handler import BaseHandler
from travel_buddy.general_types import HandlerType


class DestinationHandler(BaseHandler):
    """Handles destination selection, information, and recommendations."""
    
    def __init__(self):
        super().__init__(
            task_type=HandlerType.DESTINATION.value,
            description="Handles destination selection, information, and recommendations"
        )
    
    @property
    def prompt_template(self) -> str:
        return """You are a travel destination expert. Help with:
- Destination recommendations
- Best times to visit
- Cultural insights
- Practical travel info

Be specific and helpful."""
