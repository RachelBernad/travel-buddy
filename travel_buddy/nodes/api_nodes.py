"""API integration nodes for weather and web search."""

from typing import Dict, Any
from travel_buddy.handlers.api_handlers import weather_handler, web_search_handler
from travel_buddy.settings import settings


def fetch_weather_data(state: Dict[str, Any]) -> Dict[str, Any]:
    """Fetch weather data if needed."""
    classification = state.get("classification")
    conversation_context = state.get("conversation_context")
    
    location = classification.tags.location if classification else None
    if not location and conversation_context:
        location = conversation_context.current_topic
    
    if location:
        weather_data = weather_handler.get_weather(location)
        state["weather_data"] = weather_data
    else:
        state["weather_data"] = {"error": "No location available for weather data"}
    
    return state


def fetch_web_data(state: Dict[str, Any]) -> Dict[str, Any]:
    """Fetch web search data if needed."""
    user_input = state.get("question", "")
    classification = state.get("classification")
    conversation_context = state.get("conversation_context")
    
    # Build search query
    search_query = user_input
    location = classification.tags.location if classification else None
    if location:
        search_query = f"{user_input} {location}"
    
    web_data = web_search_handler.search(search_query, num_results=3)
    state["web_data"] = web_data
    
    return state


def should_fetch_additional_data(state: Dict[str, Any]) -> str:
    """Determine if weather data should be fetched."""
    if state.get("needs_weather_api", False) and settings.enable_weather_api:
        return "fetch_weather"
    elif state.get("needs_web_search", False) and settings.enable_web_search_api:
        return "fetch_web"
    else:
        return "process_handler"
