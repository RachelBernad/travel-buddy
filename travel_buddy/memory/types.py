"""Type definitions for memory and conversation system."""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class ConversationTurn(BaseModel):
    """Represents a single turn in a conversation."""
    
    turn_id: str = Field(..., description="Unique identifier for this turn")
    timestamp: datetime = Field(default_factory=datetime.now)
    user_input: str = Field(..., description="User's input message")
    assistant_response: str = Field(..., description="Assistant's response")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class MemoryEntry(BaseModel):
    """Represents a memory entry that can be stored and retrieved."""
    
    entry_id: str = Field(..., description="Unique identifier for this memory entry")
    content: str = Field(..., description="The memory content")
    entry_type: str = Field(..., description="Type of memory (e.g., 'preference', 'fact', 'context')")
    importance: float = Field(default=0.5, ge=0.0, le=1.0, description="Importance score for this memory")
    created_at: datetime = Field(default_factory=datetime.now)
    last_accessed: Optional[datetime] = Field(None, description="When this memory was last accessed")
    access_count: int = Field(default=0, description="Number of times this memory has been accessed")
    tags: List[str] = Field(default_factory=list, description="Tags for categorizing this memory")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class ConversationContext(BaseModel):
    """Represents the current conversation context."""
    
    session_id: str = Field(..., description="Unique session identifier")
    conversation_turns: List[ConversationTurn] = Field(default_factory=list)
    relevant_memories: List[MemoryEntry] = Field(default_factory=list)
    current_topic: Optional[str] = Field(None, description="Current conversation topic")
    user_preferences: Dict[str, Any] = Field(default_factory=dict, description="User preferences learned during conversation")
    created_at: datetime = Field(default_factory=datetime.now)
    last_updated: datetime = Field(default_factory=datetime.now)
