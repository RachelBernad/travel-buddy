"""Base handler class for all task handlers."""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any, List

from ..logger import logger, log_handler_operation
from ..models.response_models import TaskResult, ChatContext


class BaseHandler(ABC):
    """Base class for all task handlers."""
    
    def __init__(self, task_type: str, description: str):
        self.task_type = task_type
        self.description = description
    
    @property
    @abstractmethod
    def prompt_template(self) -> str:
        """Return the prompt template for this handler."""
        pass


    def _process_impl(self, user_input: str, context: ChatContext, handler_type: str, classification_tags: Dict[str, Any] = None) -> TaskResult:
        try:
            prompt = self.build_prompt(user_input, context, classification_tags)
            from travel_buddy.models.llm_loader import generate
            response = generate(prompt)

            metadata = self.extract_metadata(user_input, context, classification_tags)
            metadata.update({"handler_type": handler_type})

            return TaskResult(
                success=True,
                response=response,
                task_type=self.task_type,
                confidence=0.9,
                metadata=metadata
            )

        except Exception as e:
            return TaskResult(
                success=False,
                response=f"I encountered an error while processing your query: {str(e)}",
                task_type=self.task_type,
                confidence=0.0,
                metadata={"error": str(e)}
            )
    
    @log_handler_operation("process")
    def process(self, user_input: str, context: ChatContext, classification_tags: Dict[str, Any] = None, **kwargs) -> TaskResult:
        logger.info(
            "Handler processing started",
            handler_type=self.task_type,
            user_input_length=len(user_input)
        )
        
        try:
            result = self._process_impl(user_input, context, self.task_type, classification_tags)
            logger.info(
                "Handler processing completed",
                handler_type=self.task_type,
                success=result.success,
                confidence=result.confidence,
                response_length=len(result.response)
            )
            return result
        except Exception as e:
            logger.error(
                "Handler processing failed",
                handler_type=self.task_type,
                error=str(e)
            )
            raise
    
    def build_prompt(self, user_input: str, context: ChatContext, classification_tags: Dict[str, Any] = None) -> str:
        """Build chat-style prompt with system and user messages."""
        # Get system message from context or use default
        system_message = context.get_system_message() or self.prompt_template
        
        # Build context information
        context_info = ""
        if classification_tags:
            if hasattr(classification_tags, 'location') and classification_tags.location:
                context_info += f"Current location context: {classification_tags.location}\n"
            if hasattr(classification_tags, 'needs_weather_api') and classification_tags.needs_weather_api:
                context_info += "Weather information is relevant to this query.\n"
        
        # Create chat messages
        messages = [
            {"role": "system", "content": f"{system_message}\n\n{context_info}".strip()},
            {"role": "user", "content": user_input}
        ]
        
        # Format as chat
        prompt_parts = []
        for msg in messages:
            prompt_parts.append(f"{msg['role'].title()}: {msg['content']}")
        
        prompt = "\n\n".join(prompt_parts) + "\n\nAssistant:"
        
        logger.debug(
            "Prompt built",
            handler_type=self.task_type,
            prompt_length=len(prompt),
            has_classification_tags=bool(classification_tags)
        )
        
        return prompt
    
    def extract_metadata(self, user_input: str, context: ChatContext, classification_tags: Dict[str, Any] = None) -> Dict[str, Any]:
        metadata = {
            "task_type": self.task_type,
            "user_input_length": len(user_input),
            "message_count": len(context.messages)
        }
        
        if classification_tags:
            metadata.update(classification_tags)
        
        return metadata
