"""Conditional graph with API capabilities for weather and web search."""

from typing import Dict, Any, Optional
from langgraph.graph import StateGraph, START, END

from travel_buddy.memory import ConversationManager
from travel_buddy.nodes import (
    classify_intent,
    fetch_weather_data,
    fetch_web_data,
    process_with_handler,
    validate_response,
    self_correct_response,
    generate_summary,
    update_conversation_memory,
    should_fetch_additional_data,
    should_correct_response
)




def build_conditional_graph() -> StateGraph:
    """Build the conditional graph with API capabilities and validation."""
    graph = StateGraph(dict)
    
    # Add nodes
    graph.add_node("classify_intent", classify_intent)
    graph.add_node("fetch_weather", fetch_weather_data)
    graph.add_node("fetch_web", fetch_web_data)
    graph.add_node("process_handler", process_with_handler)
    graph.add_node("validate_response", validate_response)
    graph.add_node("self_correct", self_correct_response)
    graph.add_node("generate_summary", generate_summary)
    graph.add_node("update_memory", update_conversation_memory)
    
    # Add edges with conditional routing
    graph.add_edge(START, "classify_intent")
    
    # Conditional routing from classification
    graph.add_conditional_edges(
        "classify_intent",
        should_fetch_additional_data,
        {
            "fetch_weather": "fetch_weather",
            "fetch_web": "fetch_web", 
            "process_handler": "process_handler"
        }
    )

    
    # From web fetch, go to processing
    graph.add_edge("fetch_web", "process_handler")
    graph.add_edge("fetch_weather", "process_handler")
    
    # From processing, go to validation
    graph.add_edge("process_handler", "validate_response")
    
    # Conditional routing from validation
    graph.add_conditional_edges(
        "validate_response",
        should_correct_response,
        {
            "self_correct": "self_correct",
            "generate_summary": "generate_summary"
        }
    )
    
    # From self-correction, go to summary generation
    graph.add_edge("self_correct", "generate_summary")
    
    # From summary, go to memory update
    graph.add_edge("generate_summary", "update_memory")
    
    # From memory update, end
    graph.add_edge("update_memory", END)
    
    return graph.compile()


def run_conditional_graph(question: str, session_id: str = "default", 
                         conversation_manager: Optional[ConversationManager] = None) -> Dict[str, Any]:
    """Run the conditional graph with API capabilities."""
    app = build_conditional_graph()

    initial_state = {
        "question": question,
        "session_id": session_id,
        "conversation_manager": conversation_manager,
    }
    
    return app.invoke(initial_state)
 