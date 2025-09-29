"""API handlers for external services like weather and web search."""

import requests
from typing import Dict, Any, Optional
from ..logger import logger
from ..settings import settings


class WeatherAPIHandler:
    """Handler for weather API calls."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or getattr(settings, 'weather_api_key', None)
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"
    
    def get_weather(self, location: str) -> Dict[str, Any]:
        """Get weather information for a location."""
        if not self.api_key:
            logger.warning("Weather API key not configured")
            return {"error": "Weather API not configured"}
        
        try:
            params = {
                'q': location,
                'appid': self.api_key,
                'units': 'metric'
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            return {
                "temperature": data['main']['temp'],
                "description": data['weather'][0]['description'],
                "humidity": data['main']['humidity'],
                "wind_speed": data['wind']['speed'],
                "location": data['name'],
                "country": data['sys']['country']
            }
            
        except requests.RequestException as e:
            logger.error("Weather API request failed", error=str(e))
            return {"error": f"Weather API request failed: {str(e)}"}
        except Exception as e:
            logger.error("Weather API parsing failed", error=str(e))
            return {"error": f"Weather data parsing failed: {str(e)}"}


class WebSearchHandler:
    """Handler for web search API calls."""
    
    def __init__(self, api_key: Optional[str] = None, search_engine_id: Optional[str] = None):
        self.api_key = api_key or getattr(settings, 'google_search_api_key', None)
        self.search_engine_id = search_engine_id or getattr(settings, 'google_search_engine_id', None)
        self.base_url = "https://www.googleapis.com/customsearch/v1"
    
    def search(self, query: str, num_results: int = 5) -> Dict[str, Any]:
        """Search the web for information."""
        if not self.api_key or not self.search_engine_id:
            logger.warning("Web search API credentials not configured")
            return {"error": "Web search API not configured"}
        
        try:
            params = {
                'key': self.api_key,
                'cx': self.search_engine_id,
                'q': query,
                'num': num_results
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            results = []
            for item in data.get('items', []):
                results.append({
                    "title": item.get('title', ''),
                    "snippet": item.get('snippet', ''),
                    "url": item.get('link', '')
                })
            
            return {
                "results": results,
                "total_results": data.get('searchInformation', {}).get('totalResults', '0')
            }
            
        except requests.RequestException as e:
            logger.error("Web search API request failed", error=str(e))
            return {"error": f"Web search API request failed: {str(e)}"}
        except Exception as e:
            logger.error("Web search API parsing failed", error=str(e))
            return {"error": f"Web search data parsing failed: {str(e)}"}


# Global instances
weather_handler = WeatherAPIHandler()
web_search_handler = WebSearchHandler()
