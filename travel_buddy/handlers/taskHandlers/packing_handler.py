"""Handler for packing and preparation-related travel queries."""

from travel_buddy.handlers.base_handler import BaseHandler
from travel_buddy.general_types import HandlerType


class PackingHandler(BaseHandler):
    """Handles packing, preparation, and travel essentials queries."""
    
    def __init__(self):
        super().__init__(
            task_type=HandlerType.PACKING.value,
            description="Handles packing, preparation, and travel essentials queries"
        )
    
    @property
    def prompt_template(self) -> str:
        return """You are a travel packing expert. Help with:
- Packing lists and essentials
- What to bring for different trips
- Weather-appropriate clothing
- Travel documents and requirements

Be practical and specific."""