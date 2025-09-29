"""Handler for packing and preparation-related travel queries."""

from travel_buddy.handlers.base_handler import BaseHandler
from travel_buddy.models.response_models import HandlerTypeEnum


class PackingHandler(BaseHandler):
    """Handles packing, preparation, and travel essentials queries with weather API capability."""
    
    def __init__(self):
        super().__init__(
            task_type=HandlerTypeEnum.PACKING.value,
            description="Handles packing, preparation, and travel essentials queries with weather API"
        )
    
    @property
    def prompt_template(self) -> str:
        return """You are a practical and experienced travel packing expert! Help travelers pack smartly for their adventures with personalized packing lists, weather-appropriate clothing advice, and essential travel items.

Share pro tips for efficient packing, must-have travel documents, and clever space-saving tricks. Be thorough but organized, helping people feel prepared and confident for their journey. Use a helpful, reassuring tone that makes packing feel manageable and even fun."""