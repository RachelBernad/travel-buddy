import argparse

from travel_buddy.graphs.smart_graph import run_smart_graph
from travel_buddy.memory import ConversationManager
from travel_buddy.general_types import InteractionType


def main():
    parser = argparse.ArgumentParser(description="Travel Buddy Smart Assistant")
    
    # Subcommands for different interaction types
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Single query command
    single_parser = subparsers.add_parser(InteractionType.SINGLE.value, help="Single query mode")
    single_parser.add_argument("prompt", nargs="+", help="User prompt")
    single_parser.add_argument("--session-id", default="default", help="Session ID for memory")
    
    # Interactive conversation command
    interactive_parser = subparsers.add_parser(InteractionType.INTERACTIVE.value, help="Interactive conversation mode")
    interactive_parser.add_argument("--session-id", default="default", help="Session ID for memory")
    
    # Memory management commands
    memory_parser = subparsers.add_parser(InteractionType.MEMORY.value, help="Memory management")
    memory_subparsers = memory_parser.add_subparsers(dest="memory_action", help="Memory actions")
    
    # Memory subcommands
    memory_subparsers.add_parser("sessions", help="List all sessions")
    memory_subparsers.add_parser("stats", help="Show memory statistics")
    clear_parser = memory_subparsers.add_parser("clear", help="Clear memory")
    clear_parser.add_argument("--session-id", help="Clear specific session (omit to clear all)")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if args.command == InteractionType.SINGLE.value:
        handle_single_query(args)
    elif args.command == InteractionType.INTERACTIVE.value:
        handle_interactive_mode(args)
    elif args.command == InteractionType.MEMORY.value:
        handle_memory_commands(args)


def handle_single_query(args):
    """Handle single query mode."""
    prompt = " ".join(args.prompt)
    conversation_manager = ConversationManager()
    session_id = args.session_id or "default"
    
    # Ensure session exists
    if not conversation_manager.get_session(session_id):
        conversation_manager.start_session(session_id)
    
    state = run_smart_graph(prompt, session_id, conversation_manager)
    print(state.get("answer", ""))


def handle_interactive_mode(args):
    """Handle interactive conversation mode."""
    conversation_manager = ConversationManager()
    session_id = args.session_id or "default"
    
    # Ensure session exists
    if not conversation_manager.get_session(session_id):
        conversation_manager.start_session(session_id)
    
    print("Travel Buddy Interactive Mode")
    print("Type 'quit' or 'exit' to end the conversation")
    print("=" * 50)
    
    while True:
        try:
            user_input = input("\nYou: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("Goodbye!")
                break
            
            if not user_input:
                continue
            
            state = run_smart_graph(user_input, session_id, conversation_manager)
            answer = state.get("answer", "")
            
            print(f"\nTravel Buddy: {answer}")
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except EOFError:
            print("\nGoodbye!")
            break


def handle_memory_commands(args):
    """Handle memory management commands."""
    conversation_manager = ConversationManager()
    
    if args.memory_action == "sessions":
        sessions = conversation_manager.get_sessions()
        if sessions:
            print("Active sessions:")
            for session_id in sessions:
                print(f"  - {session_id}")
        else:
            print("No active sessions found.")
    
    elif args.memory_action == "stats":
        stats = conversation_manager.get_memory_stats()
        print(f"Memory Statistics:")
        print(f"  Total sessions: {stats.get('total_sessions', 0)}")
        print(f"  Total turns: {stats.get('total_turns', 0)}")
        print(f"  Storage path: {conversation_manager.memory_store.storage_path}")
    
    elif args.memory_action == "clear":
        if args.session_id:
            conversation_manager.clear_session(args.session_id)
            print(f"Cleared session: {args.session_id}")
        else:
            conversation_manager.clear_all_memory()
            print("Cleared all memory.")


if __name__ == "__main__":
    main()
