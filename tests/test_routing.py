"""Tests for task routing functionality."""

import pytest
from unittest.mock import patch
from travel_buddy.graphs.task_router import TaskRouter
from travel_buddy.handlers.task_classifier import TravelTaskClassifier
from travel_buddy.handlers.base_handler import BaseHandler, TaskResult
from travel_buddy.general_types import HandlerType


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

        # Simple keyword matching for testing - be more specific to avoid conflicts
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


class TestTaskRouter:
    """Test cases for TaskRouter."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.handlers = [
            MockHandler(HandlerType.DESTINATION.value, 0.9),
            MockHandler(HandlerType.ATTRACTIONS.value, 0.8),
            MockHandler(HandlerType.PACKING.value, 0.7),
            MockHandler(HandlerType.OTHER.value, 0.5)
        ]
        # Mock the settings to use HuggingFace backend for keyword-based testing
        with patch('travel_buddy.handlers.task_router.settings') as mock_settings:
            mock_settings.llm_backend = "huggingface"
            self.router = TaskRouter(self.handlers)
    
    def test_router_initialization(self):
        """Test router initialization."""
        assert len(self.router.handlers) == 4
        assert len(self.router.handler_list) == 4
        assert HandlerType.DESTINATION.value in self.router.handlers
        assert HandlerType.ATTRACTIONS.value in self.router.handlers
        assert HandlerType.PACKING.value in self.router.handlers
        assert HandlerType.OTHER.value in self.router.handlers
    
    def test_route_with_keyword_based_routing(self):
        """Test routing using keyword-based logic."""
        # Test with a query that should match destination handler
        handler, confidence = self.router.route("Where should I go?", {})
        # The mock handlers return their predefined confidence scores
        # Destination handler should be selected as it has the highest confidence (0.9)
        assert handler.task_type == HandlerType.DESTINATION.value
        assert confidence == 0.9
    
    def test_route_fallback_to_other_handler(self):
        """Test fallback to other handler when confidence is low."""
        # Create handlers with low confidence
        low_confidence_handlers = [
            MockHandler(HandlerType.DESTINATION.value, 0.2),
            MockHandler(HandlerType.ATTRACTIONS.value, 0.1),
            MockHandler(HandlerType.PACKING.value, 0.15),
            MockHandler(HandlerType.OTHER.value, 0.5)
        ]
        # Mock settings to use HuggingFace backend
        with patch('travel_buddy.handlers.task_router.settings') as mock_settings:
            mock_settings.llm_backend = "huggingface"
            router = TaskRouter(low_confidence_handlers)
        
        # Use a query that doesn't match any keywords to trigger low confidence
        handler, confidence = router.route("Random query", {})
        assert handler.task_type == HandlerType.OTHER.value
        assert confidence == 0.3  # Fallback confidence
    
    def test_route_empty_handlers(self):
        """Test error when no handlers are registered."""
        empty_router = TaskRouter([])
        with pytest.raises(ValueError, match="No handlers registered"):
            empty_router.route("test query", {})
    
    def test_get_handler(self):
        """Test getting specific handler by type."""
        handler = self.router.get_handler(HandlerType.ATTRACTIONS.value)
        assert handler.task_type == HandlerType.ATTRACTIONS.value
    
    def test_get_handler_not_found(self):
        """Test error when handler type not found."""
        with pytest.raises(ValueError, match="No handler found for task type"):
            self.router.get_handler("nonexistent")
    
    def test_list_handlers(self):
        """Test listing all handler types."""
        handler_types = self.router.list_handlers()
        assert len(handler_types) == 4
        assert HandlerType.DESTINATION.value in handler_types
        assert HandlerType.ATTRACTIONS.value in handler_types
        assert HandlerType.PACKING.value in handler_types
        assert HandlerType.OTHER.value in handler_types
    
    def test_add_handler(self):
        """Test adding a new handler."""
        new_handler = MockHandler("custom", 0.6)
        self.router.add_handler(new_handler)
        
        assert "custom" in self.router.handlers
        assert len(self.router.handler_list) == 5
        assert self.router.get_handler("custom") == new_handler
    
    def test_remove_handler(self):
        """Test removing a handler."""
        self.router.remove_handler(HandlerType.PACKING.value)
        
        assert HandlerType.PACKING.value not in self.router.handlers
        assert len(self.router.handler_list) == 3
        with pytest.raises(ValueError):
            self.router.get_handler(HandlerType.PACKING.value)


class TestOllamaTaskClassifier:
    """Test cases for OllamaTaskClassifier."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.classifier = TravelTaskClassifier()
    
    def test_classifier_initialization(self):
        """Test classifier initialization."""
        assert self.classifier.model is not None
        assert len(self.classifier.handler_types) == 4
        assert "destination" in self.classifier.handler_types
        assert "attractions" in self.classifier.handler_types
        assert "packing" in self.classifier.handler_types
        assert "other" in self.classifier.handler_types
    
    def test_build_classification_prompt(self):
        """Test prompt building."""
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
    
    def test_parse_classification_response_valid(self):
        """Test parsing valid classification response."""
        response = "category: attractions\nconfidence: 0.9"
        handler_type, confidence = self.classifier._parse_classification_response(response)
        
        assert handler_type == HandlerType.ATTRACTIONS
        assert confidence == 0.9
    
    def test_parse_classification_response_invalid_category(self):
        """Test parsing response with invalid category."""
        response = "category: invalid\nconfidence: 0.8"
        handler_type, confidence = self.classifier._parse_classification_response(response)
        
        assert handler_type == HandlerType.OTHER  # Should fallback to other
        assert confidence == 0.8
    
    def test_parse_classification_response_invalid_confidence(self):
        """Test parsing response with invalid confidence."""
        response = "category: attractions\nconfidence: invalid"
        handler_type, confidence = self.classifier._parse_classification_response(response)
        
        assert handler_type == HandlerType.ATTRACTIONS
        assert confidence == 0.5  # Should fallback to default
    
    def test_parse_classification_response_malformed(self):
        """Test parsing malformed response."""
        response = "random text without proper format"
        handler_type, confidence = self.classifier._parse_classification_response(response)
        
        assert handler_type == HandlerType.OTHER
        assert confidence == 0.5
    
    @patch('travel_buddy.handlers.ollama_classifier.ollama.generate')
    def test_classify_task_success(self, mock_generate):
        """Test successful task classification."""
        mock_generate.return_value = {"response": "category: attractions\nconfidence: 0.9"}
        
        handler_type, confidence = self.classifier.classify("What to do in Paris?", {})
        
        assert handler_type == HandlerType.ATTRACTIONS
        assert confidence == 0.9
        mock_generate.assert_called_once()
    
    @patch('travel_buddy.handlers.ollama_classifier.ollama.generate')
    def test_classify_task_failure(self, mock_generate):
        """Test classification failure fallback."""
        mock_generate.side_effect = Exception("Ollama error")
        
        handler_type, confidence = self.classifier.classify("Test query", {})
        
        assert handler_type == HandlerType.OTHER
        assert confidence == 0.5


class TestTaskRouterWithOllama:
    """Test cases for TaskRouter with Ollama integration."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.handlers = [
            MockHandler(HandlerType.DESTINATION.value, 0.9),
            MockHandler(HandlerType.ATTRACTIONS.value, 0.8),
            MockHandler(HandlerType.PACKING.value, 0.7),
            MockHandler(HandlerType.OTHER.value, 0.5)
        ]
    
    @patch('travel_buddy.handlers.task_router.settings')
    def test_router_with_ollama_backend(self, mock_settings):
        """Test router with Ollama backend enabled."""
        mock_settings.llm_backend = "ollama"
        
        router = TaskRouter(self.handlers)
        assert router.task_classifier is not None
    
    @patch('travel_buddy.handlers.task_router.settings')
    def test_router_with_huggingface_backend(self, mock_settings):
        """Test router with HuggingFace backend (no Ollama classifier)."""
        mock_settings.llm_backend = "huggingface"
        
        router = TaskRouter(self.handlers)
        assert router.task_classifier is None
    
    @patch('travel_buddy.handlers.task_router.settings')
    @patch('travel_buddy.handlers.ollama_classifier.OllamaTaskClassifier.classify_task')
    def test_route_with_ollama_success(self, mock_classify, mock_settings):
        """Test routing with successful Ollama classification."""
        mock_settings.llm_backend = "ollama"
        mock_classify.return_value = (HandlerType.ATTRACTIONS, 0.9)
        
        router = TaskRouter(self.handlers)
        handler, confidence = router.route("What to do in Paris?", {})
        
        assert handler.task_type == HandlerType.ATTRACTIONS.value
        assert confidence == 0.9
        mock_classify.assert_called_once()
    
    @patch('travel_buddy.handlers.task_router.settings')
    @patch('travel_buddy.handlers.ollama_classifier.OllamaTaskClassifier.classify_task')
    def test_route_with_ollama_low_confidence_fallback(self, mock_classify, mock_settings):
        """Test routing with low Ollama confidence falls back to keyword-based."""
        mock_settings.llm_backend = "ollama"
        mock_classify.return_value = (HandlerType.ATTRACTIONS, 0.2)  # Low confidence
        
        router = TaskRouter(self.handlers)
        # Use a query that matches destination keywords for fallback
        handler, confidence = router.route("Where should I go?", {})
        
        # Should fall back to keyword-based routing (destination handler has highest confidence)
        assert handler.task_type == HandlerType.DESTINATION.value
        assert confidence == 0.9
        mock_classify.assert_called_once()
    
    @patch('travel_buddy.handlers.task_router.settings')
    @patch('travel_buddy.handlers.ollama_classifier.OllamaTaskClassifier.classify_task')
    def test_route_with_ollama_failure_fallback(self, mock_classify, mock_settings):
        """Test routing with Ollama failure falls back to keyword-based."""
        mock_settings.llm_backend = "ollama"
        mock_classify.side_effect = Exception("Ollama error")
        
        router = TaskRouter(self.handlers)
        # Use a query that matches destination keywords for fallback
        handler, confidence = router.route("Where should I go?", {})
        
        # Should fall back to keyword-based routing
        assert handler.task_type == HandlerType.DESTINATION.value
        assert confidence == 0.9
        mock_classify.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__])
