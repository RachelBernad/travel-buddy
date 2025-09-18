"""Ollama-based text classification for task routing."""

from typing import Dict, Any, Tuple

from ..settings import settings
from ..general_types import HandlerType


def _build_classification_prompt(user_input: str, context: Dict[str, Any]) -> str:
    context_info = ""
    if context.get("conversation_context"):
        context_info = f"\nConversation context: {context['conversation_context'][:200]}..."

    prompt = f"""You are a travel assistant task classifier. Analyze the user's input and provide:

1. Category classification (destination, attractions, packing, other) those are the categories you can handle
2. Confidence score (0.0-1.0)
3. Tags and extracted information

User input: "{user_input}"{context_info}

Respond in this exact format:
category: [category_name]
confidence: [score]
has_weather_mentioned: [true/false]
location: [extracted location or "none"]
is_question: [true/false]
is_comparison: [true/false]
is_recommendation_request: [true/false]

Examples:
category: attractions
confidence: 0.9
has_weather_mentioned: false
location: paris, france
is_question: true
is_comparison: false
is_recommendation_request: true

category: packing
confidence: 0.8
has_weather_mentioned: true
location: london, britain
is_question: true
is_comparison: false
is_recommendation_request: true"""

    return prompt


class TravelTaskClassifier:
    
    def __init__(self):
        self.model = settings.ollama_model
        self.handler_types = [handler_type.value for handler_type in HandlerType]
    
    def classify(self, user_input: str, context: Dict[str, Any]) -> Tuple[HandlerType, float, Dict[str, Any]]:
        try:
            prompt = _build_classification_prompt(user_input, context)

            from travel_buddy.models.llm_loader import generate
            response = generate(
                model=self.model,
                prompt=prompt,
                temperature=0.1,
            )
            
            handler_type, confidence, tags = self._parse_classification_response(response)
            
            return handler_type, confidence, tags
            
        except Exception as e:
            return HandlerType.OTHER, 0.5, {}

    def _parse_classification_response(self, response: str) -> Tuple[HandlerType, float, Dict[str, Any]]:
        try:
            lines = response.strip().split('\n')
            category = "other"
            confidence = 0.5
            tags = {}
            
            for line in lines:
                line = line.strip().lower()
                if line.startswith('category:'):
                    category = line.split(':', 1)[1].strip()
                elif line.startswith('confidence:'):
                    try:
                        confidence = float(line.split(':', 1)[1].strip())
                        confidence = max(0.0, min(1.0, confidence))
                    except ValueError:
                        confidence = 0.5
                elif line.startswith('has_weather_mentioned:'):
                    tags['has_weather_mentioned'] = line.split(':', 1)[1].strip() == 'true'
                elif line.startswith('location:'):
                    location = line.split(':', 1)[1].strip()
                    tags['location'] = location if location != 'none' else None
                elif line.startswith('is_question:'):
                    tags['is_question'] = line.split(':', 1)[1].strip() == 'true'
                elif line.startswith('is_comparison:'):
                    tags['is_comparison'] = line.split(':', 1)[1].strip() == 'true'
                elif line.startswith('is_recommendation_request:'):
                    tags['is_recommendation_request'] = line.split(':', 1)[1].strip() == 'true'
            
            try:
                handler_type = HandlerType(category)
            except ValueError:
                handler_type = HandlerType.OTHER
            
            return handler_type, confidence, tags
            
        except Exception:
            return HandlerType.OTHER, 0.5, {}
