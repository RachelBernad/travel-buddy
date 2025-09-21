"""Handler for attractions and activities-related travel queries."""

from travel_buddy.handlers.base_handler import BaseHandler
from travel_buddy.models.response_models import HandlerTypeEnum


class AttractionsHandler(BaseHandler):
    """Handles attractions, activities, and things to do queries."""
    
    def __init__(self):
        super().__init__(
            task_type=HandlerTypeEnum.ATTRACTIONS.value,
            description="Handles attractions, activities, and things to do queries"
        )
    
    @property
    def prompt_template(self) -> str:
        return """You are an enthusiastic travel attractions and activities expert! Help travelers discover amazing places to visit, exciting activities to try, and create memorable sightseeing experiences.

Share insider tips, hidden gems, and practical details like hours and prices. Be passionate about travel and help people create unforgettable experiences. Use an engaging, friendly tone that gets people excited about exploring new places."""