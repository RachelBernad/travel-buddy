#!/usr/bin/env python3
"""Test script to debug handler routing."""

from travel_buddy.handlers.registry import registry

def test_routing():
    """Test handler routing with different inputs."""
    test_inputs = [
        "Hello, how are you today?",
        "I need help packing for a beach vacation",
        "What are the best attractions in Paris?",
        "Where should I go for my vacation?",
        "Can you help me with my taxes?"
    ]
    
    for user_input in test_inputs:
        print(f"\nInput: '{user_input}'")
        
        # Get all handlers and their confidence scores
        handlers = registry.create_all_handlers()
        scores = []
        
        for handler in handlers:
            confidence = handler.can_handle(user_input, {})
            scores.append((handler.task_type, confidence))
            print(f"  {handler.task_type}: {confidence:.3f}")
        
        # Sort by confidence
        scores.sort(key=lambda x: x[1], reverse=True)
        best_type, best_confidence = scores[0]
        
        print(f"  -> Best: {best_type} (confidence: {best_confidence:.3f})")
        
        # Test routing logic
        if best_confidence < 0.3:
            print(f"  -> Would route to 'other' handler (fallback)")
        else:
            print(f"  -> Would route to '{best_type}' handler")

if __name__ == "__main__":
    test_routing()
