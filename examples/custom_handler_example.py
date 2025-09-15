#!/usr/bin/env python3
"""
Example of creating a custom handler for the smart graph system.

This demonstrates how to add a new handler for accommodation-related queries.
"""

import sys
from pathlib import Path

# Add the parent directory to the path so we can import travel_buddy
sys.path.insert(0, str(Path(__file__).parent.parent))

from travel_buddy.handlers.base_handler import BaseHandler, TaskResult
from travel_buddy.handlers.registry import register_handler
from langchain.chains import LLMChain


class AccommodationHandler(BaseHandler):
    """Custom handler for accommodation-related travel queries."""
    
    def __init__(self):
        super().__init__(
            task_type="accommodation",
            description="Handles accommodation, hotels, and lodging queries"
        )
    
    @property
    def prompt_template(self) -> str:
        return """You are a specialized travel accommodation expert. Your role is to help users with:

1. Hotel and accommodation recommendations
2. Lodging options and comparisons
3. Booking advice and tips
4. Location and neighborhood information
5. Budget accommodation options
6. Luxury and boutique hotels
7. Alternative accommodations (hostels, B&Bs, vacation rentals)

Focus on providing:
- Specific accommodation recommendations with reasons
- Location advantages and disadvantages
- Price ranges and value assessments
- Booking tips and best practices
- Amenities and facilities information
- Transportation access from accommodations
- Local area insights and safety considerations

Include practical details like:
- Booking platforms and timing
- Cancellation policies
- What to look for in reviews
- Questions to ask when booking
- Red flags to avoid
- Negotiation tips for longer stays

Be honest about trade-offs between price, location, and amenities."""

    
    def process(self, user_input: str, context: dict, llm_chain: LLMChain, **kwargs) -> TaskResult:
        """Process accommodation-related queries."""
        try:
            # Build the prompt
            prompt = self.build_prompt(user_input, context)
            
            # Get response from LLM
            response = llm_chain.run(question=prompt)
            
            # Extract metadata
            metadata = self.extract_metadata(user_input, context)
            metadata.update({
                "handler_type": "accommodation",
                "input_analysis": self._analyze_input(user_input)
            })
            
            # Get suggestions
            suggestions = self.get_suggestions("accommodation")
            
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
                response=f"I encountered an error while processing your accommodation query: {str(e)}",
                task_type=self.task_type,
                confidence=0.0,
                metadata={"error": str(e)},
                suggestions=[]
            )
    
    def _analyze_input(self, user_input: str) -> dict:
        """Analyze the user input for accommodation-related information."""
        analysis = {
            "has_hotel_mention": "hotel" in user_input.lower(),
            "is_budget_question": any(word in user_input.lower() for word in 
                ['cheap', 'budget', 'affordable', 'inexpensive']),
            "is_luxury_question": any(word in user_input.lower() for word in 
                ['luxury', 'expensive', 'high-end', 'boutique']),
            "is_location_question": any(word in user_input.lower() for word in 
                ['location', 'area', 'neighborhood', 'district']),
            "is_booking_question": any(word in user_input.lower() for word in 
                ['book', 'booking', 'reserve', 'reservation'])
        }
        return analysis


def main():
    """Demonstrate adding a custom handler."""
    print("Custom Handler Example: Accommodation Handler")
    print("=" * 50)
    
    # Register the custom handler
    register_handler(AccommodationHandler)
    print("✓ Registered AccommodationHandler")
    
    # Test the handler
    from travel_buddy.handlers.registry import registry
    
    # Get the handler
    handler = registry.get_handler("accommodation")
    print(f"✓ Retrieved handler: {handler.task_type}")
    print(f"  Description: {handler.description}")
    
    # Test confidence scoring
    test_inputs = [
        "I need a hotel in Paris",
        "What are the best budget accommodations in Tokyo?",
        "Can you recommend a luxury resort in the Maldives?",
        "Where should I stay in New York City?",
        "I want to book a room for next week"
    ]
    
    print("\nTesting handler confidence scores:")
    for test_input in test_inputs:
        print(f"  '{test_input}' -> {confidence:.2f}")
    
    # Show handler info
    info = registry.get_handler_info("accommodation")
    print(f"\nHandler Information:")
    print(f"  Task Type: {info['task_type']}")
    print(f"  Class: {info['class_name']}")
    print(f"  Description: {info['description']}")
    print(f"  Module: {info['module']}")
    
    print("\n✓ Custom handler example completed!")


if __name__ == "__main__":
    main()
