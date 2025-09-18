"""Base handler class for all task handlers."""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any, List

from pydantic import BaseModel, Field

from ..logger import logger, log_handler_operation


class TaskResult(BaseModel):
    """Result of a task handler execution."""
    
    success: bool = Field(..., description="Whether the task was completed successfully")
    response: str = Field(..., description="The response text")
    task_type: str = Field(..., description="Type of task that was handled")
    confidence: float = Field(default=0.8, ge=0.0, le=1.0, description="Confidence in the response")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    suggestions: List[str] = Field(default_factory=list, description="Suggested follow-up actions")
    created_at: datetime = Field(default_factory=datetime.now)


class BaseHandler(ABC):
    """Base class for all task handlers."""
    
    def __init__(self, task_type: str, description: str):
        self.task_type = task_type
        self.description = description
    
    @property
    @abstractmethod
    def prompt_template(self) -> str:
        pass

    ## todo: add validation to each of handler methods


    def _process_impl(self, user_input: str, context: Dict[str, Any], handler_type: str, classification_tags: Dict[str, Any] = None) -> TaskResult:
        try:
            prompt = self.build_prompt(user_input, context, classification_tags)
            from travel_buddy.models.llm_loader import generate
            response = generate(prompt)

            metadata = self.extract_metadata(user_input, context, classification_tags)
            metadata.update({"handler_type": handler_type})

            suggestions = self.get_suggestions(handler_type)

            return TaskResult(
                success=True,
                response=response,
                task_type=self.task_type,
                confidence=0.9,
                metadata=metadata,
                suggestions=suggestions
            )

        except Exception as e:
            return TaskResult(
                success=False,
                response=f"I encountered an error while processing your query: {str(e)}",
                task_type=self.task_type,
                confidence=0.0,
                metadata={"error": str(e)},
                suggestions=[]
            )
    
    @log_handler_operation("process", "dynamic")
    def process(self, user_input: str, context: Dict[str, Any], classification_tags: Dict[str, Any] = None, **kwargs) -> TaskResult:
        logger.info(
            "Handler processing started",
            handler_type=self.task_type,
            user_input_length=len(user_input),
            session_id=context.get("session_id", "unknown")
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
    
    def build_prompt(self, user_input: str, context: Dict[str, Any], classification_tags: Dict[str, Any] = None) -> str:
        conversation_context = context.get("conversation_context", "")
        relevant_memories = context.get("relevant_memories", [])
        
        memory_context = ""
        if relevant_memories:
            memory_context = "Relevant info:\n"
            for memory in relevant_memories[:2]:
                memory_context += f"- {memory.content[:100]}...\n"
        
        full_context = ""
        if conversation_context and len(conversation_context) < 200:
            full_context += f"Context: {conversation_context[:200]}...\n\n"
        if memory_context:
            full_context += f"{memory_context}\n"
        
        if classification_tags:
            tag_info = ""
            if classification_tags.get('location'):
                tag_info += f"Location: {classification_tags['location']}\n"
            if classification_tags.get('has_weather_mentioned'):
                tag_info += "Weather information is relevant to this query.\n"
            if tag_info:
                full_context += f"{tag_info}\n"
        
        prompt = f"{full_context}{self.prompt_template}\n\nUser: {user_input}\nAssistant:"
        
        logger.debug(
            "Prompt built",
            handler_type=self.task_type,
            prompt_length=len(prompt),
            context_length=len(conversation_context),
            memory_count=len(relevant_memories),
            has_classification_tags=bool(classification_tags)
        )
        
        return prompt
    
    def extract_metadata(self, user_input: str, context: Dict[str, Any], classification_tags: Dict[str, Any] = None) -> Dict[str, Any]:
        metadata = {
            "task_type": self.task_type,
            "user_input_length": len(user_input),
            "has_context": bool(context.get("conversation_context")),
            "memory_count": len(context.get("relevant_memories", [])),
            "session_id": context.get("session_id", "unknown")
        }
        
        if classification_tags:
            metadata.update(classification_tags)
        
        return metadata
    
    def get_suggestions(self, task_type: str) -> List[str]:
        from ..general_types import HandlerType
        
        suggestions_map = {
            HandlerType.DESTINATION.value: [
                "Ask about specific attractions in this destination",
                "Get recommendations for hotels or accommodations",
                "Learn about local transportation options",
                "Find out about local cuisine and restaurants"
            ],
            HandlerType.ATTRACTIONS.value: [
                "Get information about ticket prices and booking",
                "Ask about the best time to visit these attractions",
                "Find nearby restaurants or cafes",
                "Get transportation directions to these places"
            ],
            HandlerType.PACKING.value: [
                "Get weather information for your destination",
                "Ask about local customs and dress codes",
                "Get recommendations for travel accessories",
                "Find out about luggage restrictions"
            ],
            HandlerType.OTHER.value: [
                "Try asking about destination recommendations",
                "Ask about attractions and activities in a specific place",
                "Get help with packing for your trip",
                "Ask about travel planning in general terms"
            ]
        }
        return suggestions_map.get(task_type, [])
