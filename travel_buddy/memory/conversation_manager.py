"""Conversation manager for handling session state and context."""

import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple

from .memory_store import MemoryStore
from .types import ConversationContext, ConversationTurn, MemoryEntry


class ConversationManager:
    """Manages conversation state, context, and memory integration."""
    
    def __init__(self, memory_store: Optional[MemoryStore] = None, 
                 max_context_turns: int = 10, max_memories: int = 5):
        self.memory_store = memory_store or MemoryStore()
        self.max_context_turns = max_context_turns
        self.max_memories = max_memories
        self._active_sessions: Dict[str, ConversationContext] = {}
    
    def start_session(self, session_id: Optional[str] = None) -> str:
        """Start a new conversation session."""
        if session_id is None:
            session_id = str(uuid.uuid4())
        
        context = ConversationContext(session_id=session_id)
        self._active_sessions[session_id] = context
        return session_id
    
    def get_session(self, session_id: str) -> Optional[ConversationContext]:
        """Get an active session context."""
        return self._active_sessions.get(session_id)
    
    def end_session(self, session_id: str) -> None:
        """End a conversation session and clean up."""
        if session_id in self._active_sessions:
            del self._active_sessions[session_id]
    
    def add_turn(self, session_id: str, user_input: str, assistant_response: str,
                metadata: Optional[Dict[str, Any]] = None) -> str:
        """Add a conversation turn and update context."""
        context = self.get_session(session_id)
        if not context:
            raise ValueError(f"Session {session_id} not found")
        
        # Add turn to memory store
        turn_id = self.memory_store.add_conversation_turn(
            session_id, user_input, assistant_response, metadata
        )
        
        # Create turn object
        turn = ConversationTurn(
            turn_id=turn_id,
            user_input=user_input,
            assistant_response=assistant_response,
            metadata=metadata or {}
        )
        
        # Update context
        context.conversation_turns.append(turn)
        context.last_updated = datetime.now()
        
        # Extract and store relevant memories
        self._extract_memories_from_turn(turn)
        
        # Update relevant memories for context
        self._update_relevant_memories(context)
        
        return turn_id
    
    def update_session_summary(self, session_id: str, summary: str) -> None:
        """Update the conversation summary for a session."""
        context = self.get_session(session_id)
        if context:
            context.summary = summary
            context.last_updated = datetime.now()
        self.memory_store.update_conversation_summary(session_id, summary)
    
    def _extract_memories_from_turn(self, turn: ConversationTurn) -> None:
        """Extract and store relevant memories from a conversation turn."""
        # Simple extraction logic - in production, you'd use more sophisticated NLP
        
        # Extract user preferences
        user_input_lower = turn.user_input.lower()
        if any(word in user_input_lower for word in ['like', 'prefer', 'love', 'hate', 'dislike']):
            self.memory_store.add_memory(
                content=f"User preference: {turn.user_input}",
                entry_type="preference",
                importance=0.7,
                tags=["user_preference"],
                metadata={"turn_id": turn.turn_id}
            )
    
    def _update_relevant_memories(self, context: ConversationContext) -> None:
        """Update relevant memories for the current context."""
        # Get recent conversation turns for context
        recent_turns = context.conversation_turns[-3:] if context.conversation_turns else []
        
        # Search for relevant memories based on recent conversation
        relevant_memories = []
        
        for turn in recent_turns:
            # Search by content
            content_memories = self.memory_store.search_memories(
                turn.user_input, limit=self.max_memories // 2
            )
            relevant_memories.extend(content_memories)
            
            # Search by tags
            travel_tags = ["travel", "preference", "budget", "context"]
            tag_memories = self.memory_store.get_memories_by_tags(
                travel_tags, limit=self.max_memories // 2
            )
            relevant_memories.extend(tag_memories)
        
        # Remove duplicates and sort by importance
        unique_memories = {}
        for memory in relevant_memories:
            if memory.entry_id not in unique_memories:
                unique_memories[memory.entry_id] = memory
        
        context.relevant_memories = sorted(
            unique_memories.values(),
            key=lambda m: m.importance,
            reverse=True
        )[:self.max_memories]
    
    def get_conversation_context(self, session_id: str) -> Optional[ConversationContext]:
        """Get the current conversation context for a session."""
        context = self.get_session(session_id)
        if not context:
            return None


        # Load conversation history from memory store
        history = self.memory_store.get_conversation_history(session_id, self.max_context_turns)
        context.conversation_turns = history

        if not context.summary:
            context.summary = self.memory_store.get_conversation_summary(session_id)
        # Update relevant memories
        self._update_relevant_memories(context)
        
        return context
    
    def build_chat_context(self, session_id: str, current_input: str) -> "ChatContext":
        """Build a chat-style context with system and user messages using summaries."""
        from travel_buddy.models.response_models import ChatContext, ChatMessage
        
        chat_context = ChatContext(messages=[])
        
        # Add system message
        chat_context.add_message("system", "You are a helpful travel assistant.")
        
        # Add relevant memories as context
        context = self.get_conversation_context(session_id)
        if context and context.relevant_memories:
            memory_info = "Relevant context from previous conversations:\n"
            for memory in context.relevant_memories[:3]:  # Top 3 memories
                memory_info += f"- {memory.content}\n"
            chat_context.add_message("system", memory_info.strip())

        if context and context.summary:
            chat_context.add_message("system", f"Previous conversation summary: {context.summary}")
        elif context and context.conversation_turns:
            for turn in context.conversation_turns[-3:]:
                chat_context.add_message("assistant", turn.assistant_response)
        
        # Add current input
        chat_context.add_message("user", current_input)
        
        return chat_context
    
    def extract_user_preferences(self, session_id: str) -> Dict[str, Any]:
        """Extract user preferences from conversation history."""
        context = self.get_conversation_context(session_id)
        if not context:
            return {}
        
        preferences = {}
        
        # Extract from memories
        preference_memories = self.memory_store.search_memories(
            "", entry_type="preference", limit=20
        )
        
        for memory in preference_memories:
            # Simple extraction - in production, use more sophisticated parsing
            content = memory.content.lower()
            if "budget" in content or "price" in content:
                preferences["budget_conscious"] = True
            if "luxury" in content or "expensive" in content:
                preferences["luxury_preference"] = True
            if "family" in content or "kids" in content:
                preferences["family_travel"] = True
        
        return preferences
    
    def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """Get a summary of the conversation session."""
        context = self.get_conversation_context(session_id)
        if not context:
            return {}
        
        return {
            "session_id": session_id,
            "total_turns": len(context.conversation_turns),
            "duration_minutes": (
                context.last_updated - context.created_at
            ).total_seconds() / 60,
            "current_topic": context.current_topic,
            "user_preferences": self.extract_user_preferences(session_id),
            "relevant_memories_count": len(context.relevant_memories),
            "created_at": context.created_at,
            "last_updated": context.last_updated
        }

    def get_sessions(self):
        """Get a list of all active sessions."""
        return self.memory_store.get_all_sessions()

    def get_memory_stats(self) -> Dict[str, Any]:
        """Get statistics about stored memories."""
        return self.memory_store.get_memory_stats()

    def clear_session(self, session_id: str) -> None:
        """Clear all conversation history for a session."""
        self.memory_store.clear_session(session_id)

    def clear_all_memory(self) -> None:
        """Delete all memories."""
        self.memory_store.delete_all_memories()
