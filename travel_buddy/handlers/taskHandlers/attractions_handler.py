"""Handler for attractions and activities-related travel queries."""

from travel_buddy.handlers.base_handler import BaseHandler
from travel_buddy.general_types import HandlerType


class AttractionsHandler(BaseHandler):
    """Handles attractions, activities, and things to do queries."""
    
    def __init__(self):
        super().__init__(
            task_type=HandlerType.ATTRACTIONS.value,
            description="Handles attractions, activities, and things to do queries"
        )
    
    @property
    def prompt_template(self) -> str:
        return """You are a travel attractions expert. Help with:
- Attraction recommendations
- Activity suggestions
- Sightseeing itineraries
- Practical info (hours, prices)

Be specific and helpful."""
