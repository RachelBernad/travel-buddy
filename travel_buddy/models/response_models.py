"""Pydantic models for structured LLM responses."""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from enum import Enum


class HandlerTypeEnum(str, Enum):
    """Handler types for routing."""
    DESTINATION = "destination"
    ATTRACTIONS = "attractions"
    PACKING = "packing"
    OTHER = "other"


class ClassificationTags(BaseModel):
    needs_weather_api: bool = Field(default=False, description="Whether weather API is needed")
    needs_web_search: bool = Field(default=False, description="Whether web search is needed")
    location: Optional[str] = Field(default=None, description="Extracted location or None")
    is_question: bool = Field(default=True, description="Whether input is a question")
    is_comparison: bool = Field(default=False, description="Whether input is a comparison")
    is_recommendation_request: bool = Field(default=False, description="Whether input requests recommendations")
    
    @validator('location')
    def validate_location(cls, v):
        """Clean and validate location."""
        if v is None:
            return None
        # Clean location string
        cleaned = v.strip().lower()
        if cleaned in ['none', 'null', '']:
            return None
        return cleaned


class ClassificationResponse(BaseModel):
    """Structured response for task classification."""
    category: HandlerTypeEnum = Field(..., description="The task category")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    tags: ClassificationTags = Field(..., description="Classification tags")

class ChatMessage(BaseModel):
    """Individual chat message."""
    role: str = Field(..., description="Message role: system, user, or assistant")
    content: str = Field(..., description="Message content")
    
    @validator('role')
    def validate_role(cls, v):
        """Validate role is one of the allowed values."""
        allowed_roles = {'system', 'user', 'assistant'}
        if v not in allowed_roles:
            raise ValueError(f"Role must be one of {allowed_roles}")
        return v


class ChatContext(BaseModel):
    """Chat context with system and user messages."""
    messages: List[ChatMessage] = Field(default_factory=list, description="List of chat messages")
    
    def add_message(self, role: str, content: str) -> None:
        """Add a message to the context."""
        self.messages.append(ChatMessage(role=role, content=content))
    
    def get_system_message(self) -> Optional[str]:
        """Get the system message content if it exists."""
        for msg in self.messages:
            if msg.role == "system":
                return msg.content
        return None
    
    def get_user_messages(self) -> List[str]:
        """Get all user message contents."""
        return [msg.content for msg in self.messages if msg.role == "user"]


class TaskResult(BaseModel):
    """Result of a task handler execution."""
    success: bool = Field(..., description="Whether the task was completed successfully")
    response: str = Field(..., description="The response text")
    task_type: str = Field(..., description="Type of task that was handled")
    confidence: float = Field(default=0.8, ge=0.0, le=1.0, description="Confidence in the response")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    created_at: str = Field(default_factory=lambda: __import__('datetime').datetime.now().isoformat(), description="Creation timestamp")
    
    @validator('response')
    def validate_response(cls, v):
        """Clean response text."""
        if not v or not v.strip():
            raise ValueError("Response cannot be empty")
        return v.strip()


