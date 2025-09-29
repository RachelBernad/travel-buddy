"""Persistent memory storage for conversation history and user preferences."""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any
from collections import defaultdict

from .types import MemoryEntry, ConversationTurn
from ..logger import logger, log_memory_access


class MemoryStore:
    """Handles persistent storage and retrieval of conversation memories."""
    
    def __init__(self, storage_path: str = "memory_store.json"):
        self.storage_path = Path(storage_path)
        self._memories: Dict[str, MemoryEntry] = {}
        self._conversations: Dict[str, List[ConversationTurn]] = defaultdict(list)
        self._load_from_disk()
    
    @log_memory_access("load_from_disk")
    def _load_from_disk(self) -> None:
        """Load memories and conversations from disk."""
        if not self.storage_path.exists():
            logger.debug("Memory store file does not exist", path=str(self.storage_path))
            return
        
        try:
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Load memories
            memory_count = 0
            for memory_data in data.get('memories', []):
                memory = MemoryEntry(**memory_data)
                self._memories[memory.entry_id] = memory
                memory_count += 1
            
            # Load conversations
            session_count = 0
            for session_id, turns_data in data.get('conversations', {}).items():
                self._conversations[session_id] = [
                    ConversationTurn(**turn_data) for turn_data in turns_data
                ]
                session_count += 1
            
            logger.info(
                "Memory store loaded",
                memory_count=memory_count,
                session_count=session_count,
                path=str(self.storage_path)
            )
                
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.warning("Could not load memory store", error=str(e), path=str(self.storage_path))
    
    @log_memory_access("save_to_disk")
    def _save_to_disk(self) -> None:
        """Save memories and conversations to disk."""
        data = {
            'memories': [memory.dict() for memory in self._memories.values()],
            'conversations': {
                session_id: [turn.dict() for turn in turns]
                for session_id, turns in self._conversations.items()
            }
        }
        
        try:
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str, ensure_ascii=False)
            logger.debug(
                "Memory store saved",
                memory_count=len(self._memories),
                session_count=len(self._conversations),
                path=str(self.storage_path)
            )
        except Exception as e:
            logger.warning("Could not save memory store", error=str(e), path=str(self.storage_path))
    
    @log_memory_access("add_memory")
    def add_memory(self, content: str, entry_type: str = "general", 
                   importance: float = 0.5, tags: Optional[List[str]] = None,
                   metadata: Optional[Dict[str, Any]] = None) -> str:
        """Add a new memory entry."""
        entry_id = str(uuid.uuid4())
        memory = MemoryEntry(
            entry_id=entry_id,
            content=content,
            entry_type=entry_type,
            importance=importance,
            tags=tags or [],
            metadata=metadata or {}
        )
        
        self._memories[entry_id] = memory
        self._save_to_disk()
        logger.debug(
            "Memory added",
            entry_id=entry_id,
            entry_type=entry_type,
            importance=importance,
            content_length=len(content)
        )
        return entry_id
    
    @log_memory_access("get_memory")
    def get_memory(self, entry_id: str) -> Optional[MemoryEntry]:
        """Retrieve a specific memory by ID."""
        memory = self._memories.get(entry_id)
        if memory:
            memory.last_accessed = datetime.now()
            memory.access_count += 1
            self._save_to_disk()
            logger.debug("Memory accessed", entry_id=entry_id, access_count=memory.access_count)
        else:
            logger.debug("Memory not found", entry_id=entry_id)
        return memory
    
    @log_memory_access("search_memories")
    def search_memories(self, query: str, entry_type: Optional[str] = None,
                       min_importance: float = 0.0, limit: int = 10) -> List[MemoryEntry]:
        """Search memories by content, type, and importance."""
        results = []
        
        for memory in self._memories.values():
            if entry_type and memory.entry_type != entry_type:
                continue
            if memory.importance < min_importance:
                continue
            
            # Simple text matching - in production, you'd use semantic search
            if query.lower() in memory.content.lower():
                results.append(memory)
        
        # Sort by importance and access count
        results.sort(key=lambda m: (m.importance, m.access_count), reverse=True)
        final_results = results[:limit]
        
        logger.debug(
            "Memory search completed",
            query=query[:50] + "..." if len(query) > 50 else query,
            entry_type=entry_type,
            min_importance=min_importance,
            results_count=len(final_results),
            total_matches=len(results)
        )
        return final_results
    
    def get_memories_by_tags(self, tags: List[str], limit: int = 10) -> List[MemoryEntry]:
        """Get memories that match any of the provided tags."""
        results = []
        tag_set = set(tags)
        
        for memory in self._memories.values():
            if tag_set.intersection(set(memory.tags)):
                results.append(memory)
        
        results.sort(key=lambda m: (m.importance, m.access_count), reverse=True)
        return results[:limit]
    
    def update_memory(self, entry_id: str, **updates) -> bool:
        """Update an existing memory entry."""
        if entry_id not in self._memories:
            return False
        
        memory = self._memories[entry_id]
        for key, value in updates.items():
            if hasattr(memory, key):
                setattr(memory, key, value)
        
        self._save_to_disk()
        return True
    
    def delete_memory(self, entry_id: str) -> bool:
        """Delete a memory entry."""
        if entry_id in self._memories:
            del self._memories[entry_id]
            self._save_to_disk()
            return True
        return False

    def delete_all_memories(self) -> None:
        """Delete all memories."""
        self._memories = {}
        self._save_to_disk()
    
    def add_conversation_turn(self, session_id: str, user_input: str, 
                            assistant_response: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Add a conversation turn to a session."""
        turn_id = str(uuid.uuid4())
        turn = ConversationTurn(
            turn_id=turn_id,
            user_input=user_input,
            assistant_response=assistant_response,
            metadata=metadata or {}
        )
        
        self._conversations[session_id].append(turn)
        self._save_to_disk()
        return turn_id
    
    def get_conversation_history(self, session_id: str, limit: Optional[int] = None) -> List[ConversationTurn]:
        """Get conversation history for a session."""
        turns = self._conversations.get(session_id, [])
        if limit:
            return turns[-limit:]
        return turns

    def get_conversation_summary(self, session_id: str) -> str:
        """Get a summary of the conversation session."""
        if session_id not in self._conversations:
            return ""
        last_turn = self.get_conversation_history(session_id, 1)[0]
        summary = last_turn.metasata.get("summary", "")
        return summary

    def update_conversation_summary(self, session_id: str, summary: str) -> None:
        """Update the conversation summary for a session."""
        if session_id in self._conversations:
            last_turn = self._conversations[session_id][-1]
            last_turn.metadata["summary"] = summary
    
    def clear_session(self, session_id: str) -> None:
        """Clear all conversation history for a session."""
        if session_id in self._conversations:
            del self._conversations[session_id]
            self._save_to_disk()
    
    def get_all_sessions(self) -> List[str]:
        """Get all session IDs."""
        return list(self._conversations.keys())
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get statistics about stored memories."""
        if not self._memories:
            return {"total_memories": 0, "memory_types": {}, "total_sessions": len(self._conversations)}
        
        memory_types = defaultdict(int)
        for memory in self._memories.values():
            memory_types[memory.entry_type] += 1
        
        return {
            "total_memories": len(self._memories),
            "memory_types": dict(memory_types),
            "total_sessions": len(self._conversations),
            "avg_importance": sum(m.importance for m in self._memories.values()) / len(self._memories)
        }
