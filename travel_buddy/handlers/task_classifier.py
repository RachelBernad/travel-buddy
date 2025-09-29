"""Ollama-based text classification for task routing."""

from typing import Dict, Any, Tuple, List
import json
from pydantic import ValidationError

from ..settings import settings
from ..models.response_models import ClassificationResponse, HandlerTypeEnum, ChatContext, ClassificationTags


def _build_classification_prompt(user_input: str, context: ChatContext, options) -> str:
    """Build structured prompt for classification."""
    system_message = context.get_system_message() or "You are a travel assistant intent classifier."

    prompt = f"""
    {system_message}

    Your task is to analyze the user input and classify it for a travel assistant system.

    Rules:
    1. Choose exactly one category from: {options}
    2. Respond ONLY in valid JSON with this exact structure:
    {{
        "category": "<one of the categories>",
        "confidence": <number between 0.0 and 1.0>,
        "tags": {{
            "needs_weather_api": <true/false>,
            "needs_web_search": <true/false>,
            "location": "<extracted location or null>",
            "is_question": <true/false>,
            "is_comparison": <true/false>,
            "is_recommendation_request": <true/false>
        }}
    }}

    User input: "{user_input}"

    Examples:

    Example 1:
    User input: "What should I pack for Tokyo in April?"
    Response:
    {{
        "category": "packing",
        "confidence": 0.95,
        "tags": {{
            "needs_weather_api": true,
            "needs_web_search": false,
            "location": "Tokyo, Japan",
            "is_question": true,
            "is_comparison": false,
            "is_recommendation_request": true
        }}
    }}

    Example 2:
    User input: "Which temples should I visit in Kyoto?"
    Response:
    {{
        "category": "attractions",
        "confidence": 0.9,
        "tags": {{
            "needs_weather_api": false,
            "needs_web_search": false,
            "location": "Kyoto, Japan",
            "is_question": true,
            "is_comparison": false,
            "is_recommendation_request": true
        }}
    }}

    Now classify the user input above. Respond ONLY with valid JSON.
    """

    return prompt


class TravelTaskClassifier:
    
    def __init__(self):
        self.model = settings.classification_model
    
    def classify(self, user_input: str, context: ChatContext, options: List[str]) -> ClassificationResponse:
        """Classify user input and return handler type, confidence, and tags."""
        try:
            prompt = _build_classification_prompt(user_input, context, options)

            from travel_buddy.models.llm_loader import generate
            response = generate(
                custom_model=self.model,
                prompt=prompt,
                temperature=0,
                top_p=1.0,
                top_k=0
            )
            
            classification = self._parse_classification_response(response)
            return classification
            
        except Exception as e:
            from ..logger import logger
            logger.error("Classification failed", error=str(e))
            return ClassificationResponse(
                category=HandlerTypeEnum.OTHER,
                confidence=0.5,
                tags=ClassificationTags()
            )

    @staticmethod
    def _parse_classification_response(response: str) -> ClassificationResponse:
        try:
            data = json.loads(response)
            return ClassificationResponse.model_validate(data)
        except (json.JSONDecodeError, ValidationError):
            return ClassificationResponse(
                category=HandlerTypeEnum.OTHER,
                confidence=0.5,
                tags= ClassificationTags()
            )
