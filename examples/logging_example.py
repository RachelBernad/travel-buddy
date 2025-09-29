"""Example demonstrating the logging system in travel-buddy."""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from travel_buddy.handlers.registry import registry
from travel_buddy.memory.memory_store import MemoryStore


def main():
    """Demonstrate the logging system."""
    print("=== Travel Buddy Logging System Demo ===\n")
    
    # 1. Show handler registration logging
    print("1. Handler Registration Logging:")
    print("   (Handlers are auto-registered on import)")
    print()
    
    # 2. Show memory access logging
    print("2. Memory Access Logging:")
    memory_store = MemoryStore("demo_memory.json")
    
    # Add some memories
    memory_id1 = memory_store.add_memory(
        "User prefers beach destinations",
        entry_type="preference",
        importance=0.8,
        tags=["destination", "beach"]
    )
    
    memory_id2 = memory_store.add_memory(
        "User is traveling to Japan in spring",
        entry_type="trip",
        importance=0.9,
        tags=["trip", "japan", "spring"]
    )
    
    # Search memories
    results = memory_store.search_memories("japan", limit=5)
    print(f"   Found {len(results)} memories about Japan")
    
    # Get specific memory
    memory = memory_store.get_memory(memory_id1)
    print(f"   Retrieved memory: {memory.content[:30]}...")
    print()
    
    # 3. Show handler processing logging
    print("3. Handler Processing Logging:")
    try:
        # Get a handler and process a query
        destination_handler = registry.get_handler("destination")
        context = {
            "session_id": "demo_session",
            "conversation_context": "User is planning a trip",
            "relevant_memories": results
        }
        
        result = destination_handler.process(
            "I want to visit a beach destination in Asia",
            context
        )
        print(f"   Handler response: {result.response[:100]}...")
        print(f"   Success: {result.success}, Confidence: {result.confidence}")
        
    except Exception as e:
        print(f"   Note: LLM generation failed (expected in demo): {e}")
    print()
    
    # 4. Show memory statistics
    print("4. Memory Statistics:")
    stats = memory_store.get_memory_stats()
    print(f"   Total memories: {stats['total_memories']}")
    print(f"   Memory types: {stats['memory_types']}")
    print(f"   Total sessions: {stats['total_sessions']}")
    print()
    
    # Clean up demo file
    if os.path.exists("demo_memory.json"):
        os.remove("demo_memory.json")
    
    print("=== Demo Complete ===")
    print("Check the console output above to see the logging in action!")
    print("The logger provides:")
    print("- Handler registration and instance creation")
    print("- Memory operations with timing")
    print("- Model call specifications and timing")
    print("- Handler processing with context")


if __name__ == "__main__":
    main()
