"""Simple tests for routing functionality."""

import pytest
from unittest.mock import patch
from travel_buddy.graphs.task_router import TaskRouter
from travel_buddy.handlers.task_classifier import TravelTaskClassifier, _build_classification_prompt
from travel_buddy.handlers.base_handler import BaseHandler, TaskResult
from travel_buddy.types import HandlerType


class MockHandler(BaseHandler):
    """Mock handler for testing."""
    
    def __init__(self, task_type: str, confidence_score: float = 0.8):
        super().__init__(task_type, f"Mock {task_type} handler")
        self.confidence_score = confidence_score
    
    @property
    def prompt_template(self) -> str:
        return f"Mock template for {self.task_type}"
    
    def can_handle(self, user_input: str, context: dict) -> float:
        """Return confidence score based on input for testing."""
        user_input_lower = user_input.lower()
        
        # Simple keyword matching for testing
        if self.task_type == "destination" and any(word in user_input_lower for word in ["where", "destination", "country", "city"]):
            return self.confidence_score
        elif self.task_type == "attractions" and any(word in user_input_lower for word in ["attractions", "activities", "sightseeing", "museum"]):
            return self.confidence_score
        elif self.task_type == "packing" and any(word in user_input_lower for word in ["pack", "bring", "clothes", "luggage"]):
            return self.confidence_score
        else:
            return 0.1  # Low confidence for non-matching queries
    
    def process(self, user_input: str, context: dict, **kwargs) -> TaskResult:
        """Mock processing."""
        return TaskResult(
            success=True,
            response=f"Mock response for {self.task_type}",
            task_type=self.task_type,
            confidence=self.confidence_score
        )


def test_ollama_classifier_initialization():
    """Test OllamaTaskClassifier initialization."""
    classifier = TravelTaskClassifier()
    assert classifier.model is not None
    assert len(classifier.handler_types) == 4
    assert "destination" in classifier.handler_types
    assert "attractions" in classifier.handler_types
    assert "packing" in classifier.handler_types
    assert "other" in classifier.handler_types


def test_ollama_classifier_prompt_building():
    """Test prompt building for classification."""
    classifier = TravelTaskClassifier()
    user_input = "What are the best attractions in Paris?"
    context = {"conversation_context": "Previous travel discussion"}
    
    prompt = _build_classification_prompt(user_input, context)
    
    assert user_input in prompt
    assert "Previous travel discussion" in prompt
    assert "destination" in prompt
    assert "attractions" in prompt
    assert "packing" in prompt
    assert "other" in prompt
    assert "category:" in prompt
    assert "confidence:" in prompt


def test_ollama_classifier_response_parsing():
    """Test parsing of classification responses."""
    classifier = TravelTaskClassifier()
    
    # Test valid response
    response = "category: attractions\nconfidence: 0.9\nhas_weather_mentioned: false\nlocation: paris, france\nis_question: true\nis_comparison: false\nis_recommendation_request: true"
    handler_type, confidence, tags = classifier._parse_classification_response(response)
    assert handler_type == HandlerType.ATTRACTIONS
    assert confidence == 0.9
    assert tags['has_weather_mentioned'] == False
    assert tags['location'] == "paris, france"
    
    # Test invalid category
    response = "category: invalid\nconfidence: 0.8\nhas_weather_mentioned: true\nlocation: none\nis_question: false\nis_comparison: false\nis_recommendation_request: false"
    handler_type, confidence, tags = classifier._parse_classification_response(response)
    assert handler_type == HandlerType.OTHER
    assert confidence == 0.8
    assert tags['has_weather_mentioned'] == True
    assert tags['location'] == None
    
    # Test malformed response
    response = "random text without proper format"
    handler_type, confidence, tags = classifier._parse_classification_response(response)
    assert handler_type == HandlerType.OTHER
    assert confidence == 0.5
    assert tags == {}


@patch('travel_buddy.handlers.task_classifier.ollama.generate')
def test_ollama_classifier_success(mock_generate):
    """Test successful task classification."""
    mock_generate.return_value = {"response": "category: attractions\nconfidence: 0.9\nhas_weather_mentioned: false\nlocation: paris, france\nis_question: true\nis_comparison: false\nis_recommendation_request: true"}
    
    classifier = TravelTaskClassifier()
    handler_type, confidence, tags = classifier.classify("What to do in Paris?", {})
    
    assert handler_type == HandlerType.ATTRACTIONS
    assert confidence == 0.9
    assert tags['location'] == "paris, france"
    mock_generate.assert_called_once()


@patch('travel_buddy.handlers.task_classifier.ollama.generate')
def test_ollama_classifier_failure(mock_generate):
    """Test classification failure fallback."""
    mock_generate.side_effect = Exception("Ollama error")
    
    classifier = TravelTaskClassifier()
    handler_type, confidence, tags = classifier.classify("Test query", {})
    
    assert handler_type == HandlerType.OTHER
    assert confidence == 0.5
    assert tags == {}


def test_task_router_basic_functionality():
    """Test basic TaskRouter functionality."""
    handlers = [
        MockHandler(HandlerType.DESTINATION.value, 0.9),
        MockHandler(HandlerType.ATTRACTIONS.value, 0.8),
        MockHandler(HandlerType.PACKING.value, 0.7),
        MockHandler(HandlerType.OTHER.value, 0.5)
    ]
    
    router = TaskRouter(handlers)
    
    # Should have classifier
    assert router.task_classifier is not None


def test_task_router_with_ollama():
    """Test TaskRouter with Ollama integration."""
    handlers = [
        MockHandler(HandlerType.DESTINATION.value, 0.9),
        MockHandler(HandlerType.ATTRACTIONS.value, 0.8),
        MockHandler(HandlerType.PACKING.value, 0.7),
        MockHandler(HandlerType.OTHER.value, 0.5)
    ]
    
    router = TaskRouter(handlers)
    
    # Should have Ollama classifier
    assert router.task_classifier is not None


@patch('travel_buddy.handlers.task_classifier.TravelTaskClassifier.classify_task')
def test_task_router_ollama_success(mock_classify):
    """Test routing with successful Ollama classification."""
    mock_classify.return_value = (HandlerType.ATTRACTIONS, 0.9, {"location": "paris, france"})
    
    handlers = [
        MockHandler(HandlerType.DESTINATION.value, 0.9),
        MockHandler(HandlerType.ATTRACTIONS.value, 0.8),
        MockHandler(HandlerType.PACKING.value, 0.7),
        MockHandler(HandlerType.OTHER.value, 0.5)
    ]
    
    router = TaskRouter(handlers)
    handler, confidence, tags = router.route("What to do in Paris?", {})
    
    assert handler.task_type == HandlerType.ATTRACTIONS.value
    assert confidence == 0.9
    assert tags["location"] == "paris, france"
    mock_classify.assert_called_once()


@patch('travel_buddy.handlers.task_classifier.TravelTaskClassifier.classify_task')
def test_task_router_ollama_fallback(mock_classify):
    """Test routing with Ollama failure falls back to other handler."""
    mock_classify.side_effect = Exception("Ollama error")
    
    handlers = [
        MockHandler(HandlerType.DESTINATION.value, 0.9),
        MockHandler(HandlerType.ATTRACTIONS.value, 0.8),
        MockHandler(HandlerType.PACKING.value, 0.7),
        MockHandler(HandlerType.OTHER.value, 0.5)
    ]
    
    router = TaskRouter(handlers)
    handler, confidence, tags = router.route("Where should I go?", {})
    
    # Should fall back to other handler
    assert handler.task_type == HandlerType.OTHER.value
    assert confidence == 0.5
    assert tags == {}
    mock_classify.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__])
