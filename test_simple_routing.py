#!/usr/bin/env python3
"""Simple test of smart graph routing without conversation context."""

from travel_buddy.graphs.smart_graph import create_task_router

def test_simple_routing():
    """Test routing without conversation context."""
    router = create_task_router()
    
    test_inputs = [
        "Hello, how are you today?",
        "I need help packing for a beach vacation",
        "What are the best attractions in Paris?",
    ]
    
    for user_input in test_inputs:
        print(f"\nInput: '{user_input}'")
        
        # Test routing with empty context
        handler, confidence = router.route(user_input, {})
        print(f"  -> Routed to: {handler.task_type} (confidence: {confidence:.3f})")

if __name__ == "__main__":
    test_simple_routing()
