from typing import List, Tuple
from travel_buddy.handlers.base_handler import BaseHandler
from travel_buddy.handlers.task_classifier import TravelTaskClassifier
from travel_buddy.models.response_models import ChatContext, HandlerTypeEnum, ClassificationResponse, ClassificationTags


class TaskRouter:
    
    def __init__(self, handlers: List[BaseHandler]):
        self.handlers = {handler.task_type: handler for handler in handlers}
        self.task_classifier = TravelTaskClassifier()
    
    def route(self, user_input: str, context: ChatContext) -> ClassificationResponse:
        if not self.handlers:
            raise ValueError("No handlers registered")

        try:
            classification = self.task_classifier.classify(user_input, context, [handler for handler in self.handlers.keys()])
            if classification.confidence > 0.2:
                return classification
        except Exception:
            from travel_buddy.handlers.taskHandlers.other_handler import OtherHandler
            return ClassificationResponse(
                category=HandlerTypeEnum.OTHER,
                confidence=0.5,
                tags=ClassificationTags()
            )

        return ClassificationResponse(
            category=HandlerTypeEnum.OTHER,
            confidence=0.5,
            tags=ClassificationTags()
        )

