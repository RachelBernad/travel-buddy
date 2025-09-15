from typing import Dict, Any, List, Tuple
from travel_buddy.handlers.base_handler import BaseHandler
from travel_buddy.handlers.taskHandlers.other_handler import OtherHandler
from travel_buddy.handlers.task_classifier import TravelTaskClassifier


class TaskRouter:
    
    def __init__(self, handlers: List[BaseHandler]):
        self.handlers = {handler.task_type: handler for handler in handlers}
        self.handler_list = handlers
        self.task_classifier = TravelTaskClassifier()
    
    def route(self, user_input: str, context: Dict[str, Any]) -> Tuple[BaseHandler, float, Dict[str, Any]]:
        if not self.handlers:
            raise ValueError("No handlers registered")

        try:
            handler_type, confidence, tags = self.task_classifier.classify(user_input, context)
            handler = self.handlers.get(handler_type.value)
            if handler and confidence > 0.3:
                return handler, confidence, tags
        except Exception:
            return OtherHandler(), 0.5, {}

        return OtherHandler(), 0.5, {}

