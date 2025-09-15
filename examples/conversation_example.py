#!/usr/bin/env python3
"""
Example script demonstrating the conversation memory features of Travel Buddy.

This script shows how to use the conversation system programmatically.
"""

import sys
from pathlib import Path

# Add the parent directory to the path so we can import travel_buddy
sys.path.insert(0, str(Path(__file__).parent.parent))

from travel_buddy.memory import ConversationManager, MemoryStore
from travel_buddy.chains.conversation_chain import run_conversation_chain
from travel_buddy.settings import settings


def main():
    """Demonstrate conversation memory features."""
    print("Travel Buddy Conversation Memory Demo")
    print("=" * 40)
    
    # Create conversation manager
    memory_store = MemoryStore("demo_memory.json")
    conversation_manager = ConversationManager(
        memory_store=memory_store,
        max_context_turns=5,
        max_memories=3
    )
    
    # Start a session
    session_id = "demo-session"
    conversation_manager.start_session(session_id)
    print(f"Started session: {session_id}")
    
    # Simulate a conversation
    conversation_turns = [
        "Hi! I'm planning a trip to Japan and I love sushi.",
        "What are some good restaurants in Tokyo?",
        "I'm on a budget, so nothing too expensive.",
        "What about family-friendly activities?",
        "Thanks! What about transportation options?"
    ]
    
    print("\nSimulating conversation...")
    for i, user_input in enumerate(conversation_turns, 1):
        print(f"\nTurn {i}:")
        print(f"User: {user_input}")
        
        # In a real scenario, you'd call the LLM here
        # For demo purposes, we'll simulate a response
        response = f"I understand you're interested in {user_input.lower()}. Let me help you with that."
        
        # Add the turn to conversation history
        turn_id = conversation_manager.add_turn(session_id, user_input, response)
        print(f"Assistant: {response}")
        print(f"Turn ID: {turn_id}")
    
    # Show conversation context
    print("\n" + "=" * 40)
    print("CONVERSATION CONTEXT")
    print("=" * 40)
    
    context = conversation_manager.get_conversation_context(session_id)
    if context:
        print(f"Session ID: {context.session_id}")
        print(f"Total turns: {len(context.conversation_turns)}")
        print(f"Relevant memories: {len(context.relevant_memories)}")
        
        print("\nRelevant memories:")
        for memory in context.relevant_memories:
            print(f"  - {memory.content} (importance: {memory.importance})")
    
    # Show user preferences
    print("\n" + "=" * 40)
    print("USER PREFERENCES")
    print("=" * 40)
    
    preferences = conversation_manager.extract_user_preferences(session_id)
    print("Extracted preferences:")
    for key, value in preferences.items():
        print(f"  {key}: {value}")
    
    # Show session summary
    print("\n" + "=" * 40)
    print("SESSION SUMMARY")
    print("=" * 40)
    
    summary = conversation_manager.get_session_summary(session_id)
    for key, value in summary.items():
        print(f"{key}: {value}")
    
    # Show memory statistics
    print("\n" + "=" * 40)
    print("MEMORY STATISTICS")
    print("=" * 40)
    
    stats = memory_store.get_memory_stats()
    for key, value in stats.items():
        print(f"{key}: {value}")
    
    # Clean up
    conversation_manager.end_session(session_id)
    print(f"\nDemo completed! Memory stored in: demo_memory.json")


if __name__ == "__main__":
    main()
