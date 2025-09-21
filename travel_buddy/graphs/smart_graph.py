"""Smart graph with task routing and specialized handlers."""

from typing import Dict, Any, Optional

from travel_buddy.memory import ConversationManager


def run_smart_graph(question: str, session_id: str = "default", 
                   conversation_manager: Optional[ConversationManager] = None) -> Dict[str, Any]:
    """Run the smart graph - now uses conditional graph with API capabilities."""
    from travel_buddy.graphs.conditional_graph import run_conditional_graph
    return run_conditional_graph(question, session_id, conversation_manager)