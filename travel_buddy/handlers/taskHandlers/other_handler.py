"""Handler for queries that don't match specialized handlers."""

from travel_buddy.handlers.base_handler import BaseHandler
from travel_buddy.general_types import HandlerType


class OtherHandler(BaseHandler):
    """Handles queries that don't match any specialized handlers."""
    
    def __init__(self):
        super().__init__(
            task_type=HandlerType.OTHER.value,
            description="Handles general queries and provides guidance for specialized travel assistance"
        )
    
    @property
    def prompt_template(self) -> str:
        return """You are a travel assistant specialized in destinations, attractions, and packing.

The user's question doesn't fit your expertise areas. Respond politely and guide them to ask about:
- Destination recommendations
- Attractions and activities  
- Packing and preparation

Be helpful but honest about your limitations."""