# Travel Buddy

A smart travel assistant with conversation memory and specialized task handlers using Ollama LLMs.

## Features

- **Smart Task Routing**: Automatically routes queries to specialized handlers
- **Specialized Handlers**: Destination, attractions, packing, and general queries
- **Conversation Memory**: Remembers previous conversations and context
- **Interactive Mode**: Real-time conversation with the assistant
- **Memory Management**: Tools to view and manage conversation history
- **Comprehensive Logging**: Timing and performance tracking

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Start Ollama service and pull a model:
   ```bash
   ollama serve
   ollama pull hf.co/unsloth/Qwen3-4B-Instruct-2507-GGUF:Q4_K_M
   ```

3. Configure settings (optional):
   ```bash
   # Create .env file with custom settings
   OLLAMA_MODEL=hf.co/unsloth/Qwen3-4B-Instruct-2507-GGUF:Q4_K_M
   MAX_NEW_TOKENS=1024
   TEMPERATURE=0.5
   ```

## Usage

### Single Query
```bash
python -m travel_buddy query "Plan a 3-day trip to Rome"
```

### Interactive Mode
```bash
python -m travel_buddy interactive --session-id my-trip
```

### Memory Management
```bash
# List sessions
python -m travel_buddy memory sessions

# Show memory stats
python -m travel_buddy memory stats

# Clear specific session
python -m travel_buddy memory clear --session-id my-trip

# Clear all memory
python -m travel_buddy memory clear
```

### Logging Demo
```bash
python examples/logging_example.py
```

## Architecture

- **Smart Graph**: Routes queries to specialized handlers using LangGraph
- **Task Router**: Classifies queries and selects appropriate handlers
- **Handlers**: Specialized processors for different travel topics
- **Memory System**: Persistent conversation history and context
- **Logger**: Comprehensive timing and performance tracking

## Project Structure

```
travel_buddy/
├── cli.py                    # Command-line interface
├── logger.py                # Logging system
├── settings.py              # Configuration
├── general_types.py         # Type definitions
├── graphs/
│   ├── smart_graph.py       # Main processing graph
│   ├── conditional_graph.py # Conditional routing with API capabilities
│   └── task_router.py       # Task routing logic
├── handlers/
│   ├── base_handler.py      # Base handler class
│   ├── registry.py          # Handler registry
│   ├── task_classifier.py   # Query classification
│   ├── api_handlers.py      # Weather and web search APIs
│   └── taskHandlers/        # Specialized handlers
│       ├── destination_handler.py
│       ├── attractions_handler.py
│       ├── packing_handler.py
│       ├── other_handler.py
│       └── summary_handler.py
├── memory/
│   ├── conversation_manager.py # Conversation state
│   ├── memory_store.py      # Persistent storage
│   └── types.py             # Memory data structures
└── models/
    ├── llm_loader.py        # LLM interface
    ├── ollama_loader.py     # Ollama integration
    └── response_models.py   # Pydantic models
```

## Configuration

Key settings via environment variables:

- `OLLAMA_MODEL`: Model name (default: "hf.co/unsloth/Qwen3-4B-Instruct-2507-GGUF:Q4_K_M")
- `MAX_NEW_TOKENS`: Max tokens to generate (default: 1024)
- `TEMPERATURE`: Sampling temperature (default: 0.5)
- `MEMORY_STORAGE_PATH`: Memory file path (default: "memory_store.json")
- `MAX_CONTEXT_TURNS`: Max conversation turns in context (default: 10)
- `ENABLE_WEATHER_API`: Enable weather API integration (default: false)
- `ENABLE_WEB_SEARCH_API`: Enable web search API integration (default: false)

## Examples

See the `examples/` directory for:
- `conversation_example.py`: Conversation memory demo
- `logging_example.py`: Logging system demo
- `custom_handler_example.py`: Custom handler creation

## Testing

Run the test scripts to verify functionality:
```bash
python test_routing.py
python test_simple_routing.py
```