"""Basic tests for routing functionality."""

import pytest
from travel_buddy.handlers.task_classifier import TravelTaskClassifier, _build_classification_prompt
from travel_buddy.types import HandlerType


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
    assert tags['is_question'] == True
    assert tags['is_comparison'] == False
    assert tags['is_recommendation_request'] == True
    
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


def test_ollama_classifier_error_handling():
    """Test error handling in classification."""
    classifier = TravelTaskClassifier()
    
    # Test with empty input
    handler_type, confidence, tags = classifier._parse_classification_response("")
    assert handler_type == HandlerType.OTHER
    assert confidence == 0.5
    assert tags == {}
    
    # Test with None input
    handler_type, confidence, tags = classifier._parse_classification_response(None)
    assert handler_type == HandlerType.OTHER
    assert confidence == 0.5
    assert tags == {}


if __name__ == "__main__":
    pytest.main([__file__])
