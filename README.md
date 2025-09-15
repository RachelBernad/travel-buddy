# Travel Buddy - Local HF LLM + LangChain + LangGraph + Memory

A sophisticated travel assistant with conversation memory, context awareness, and persistent user preferences using local HuggingFace models, LangChain, and LangGraph.

## Features

- **Smart Task Routing**: Automatically routes queries to specialized handlers
- **Specialized Handlers**: Dedicated handlers for destinations, attractions, and packing
- **Conversation Memory**: Remembers previous conversations and user preferences
- **Context-Aware Responses**: Uses conversation history to provide better, more relevant answers
- **Session Management**: Support for multiple conversation sessions
- **Interactive Mode**: Real-time conversation with the assistant
- **Memory Management**: Tools to view, manage, and clear conversation history
- **Extensible Architecture**: Easy to add new specialized handlers
- **Flexible Processing**: Support for chain, graph, and smart graph modes
- **Comprehensive Logging**: Lightweight logging system with timing and model specs tracking

## Setup
1. Create and activate a virtualenv (recommended).
2. Install deps:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy env:
   ```bash
   copy .env.example .env   # Windows PowerShell: cp .env.example .env
   ```
4. Edit `.env` for your model. For a small chat model:
   - `HF_MODEL_ID=TinyLlama/TinyLlama-1.1B-Chat-v1.0`
   - Set `HF_DEVICE=cuda` if you have a GPU.

Note: Some models require `trust_remote_code=True` or specific tokenizers. If needed, adapt the loader.

## Usage

### Basic Mode (No Memory)
```bash
python -m travel_buddy basic "Plan a 3-day trip to Rome on a budget"
```

### Conversation Mode (With Memory)
```bash
# Single conversation with memory
python -m travel_buddy conversation "I love Italian food" --session-id my-trip

# Use specific session for continuity
python -m travel_buddy conversation "What restaurants do you recommend?" --session-id my-trip

# Use smart graph mode with task routing
python -m travel_buddy conversation "I need help planning a trip to Japan" --mode smart --session-id my-trip
```

### Smart Graph Mode (Task Routing)
```bash
# Use smart graph with automatic task routing
python -m travel_buddy smart "What are the best attractions in Paris?" --session-id my-trip

# The system will automatically route to the attractions handler
python -m travel_buddy smart "I need help packing for a beach vacation" --session-id my-trip
```

### Interactive Mode
```bash
# Start an interactive conversation
python -m travel_buddy interactive --session-id my-trip

# Use chain mode instead of graph mode
python -m travel_buddy interactive --mode chain --session-id my-trip

# Use smart graph mode with task routing
python -m travel_buddy interactive --mode smart --session-id my-trip
```

### Memory Management
```bash
# List all conversation sessions
python -m travel_buddy memory sessions

# Show details for a specific session
python -m travel_buddy memory session my-trip

# Show memory statistics
python -m travel_buddy memory stats

# Clear a specific session
python -m travel_buddy memory clear --session-id my-trip

# Clear all memory
python -m travel_buddy memory clear
```

### Handler Management
```bash
# List all available handlers
python -m travel_buddy handlers list

# Show information about a specific handler
python -m travel_buddy handlers info destination
python -m travel_buddy handlers info attractions
python -m travel_buddy handlers info packing
```

### Logging System
The system includes a comprehensive logging system that tracks:
- **Handler Operations**: Registration, instantiation, and processing with timing
- **Memory Access**: All memory operations (load, save, search, access) with timing
- **Model Calls**: LLM generation with model specs, timing, and performance metrics
- **System Events**: Important system events and errors

```bash
# Run the logging demo to see the system in action
python examples/logging_example.py
```

The logger provides structured output with context information:
```
16:11:13 - travel_buddy - INFO - Handler registered | task_type=destination | class_name=DestinationHandler
16:11:13 - travel_buddy - INFO - LLM generation started | backend=ollama | model=llama2 | prompt_length=326
16:11:13 - travel_buddy - INFO - Model response: dynamic | duration=215.648s | response_length=1022 | tokens_per_sec=4.7
```

## Configuration

The system supports various configuration options via environment variables or `.env` file:

### Model Settings
- `HF_MODEL_ID`: HuggingFace model identifier (default: "distilgpt2")
- `HF_DEVICE`: Device to use ("cpu" or "cuda")
- `MAX_NEW_TOKENS`: Maximum tokens to generate (default: 256)
- `TEMPERATURE`: Sampling temperature (default: 0.5)
- `TOP_P`: Top-p sampling parameter (default: 0.95)
- `TOP_K`: Top-k sampling parameter (default: 50)

### Memory Settings
- `MEMORY_STORAGE_PATH`: Path to memory storage file (default: "memory_store.json")
- `MAX_CONTEXT_TURNS`: Maximum conversation turns to keep in context (default: 10)
- `MAX_RELEVANT_MEMORIES`: Maximum relevant memories to include (default: 5)
- `ENABLE_MEMORY`: Enable memory system (default: true)
- `ENABLE_CONVERSATION_MODE`: Enable conversation mode (default: true)

## Project Structure
```
travel_buddy/
├── __init__.py
├── __main__.py
├── cli.py                    # Enhanced CLI with conversation support
├── settings.py               # Configuration with memory settings
├── chains/
│   ├── basic_chain.py        # Original basic chain
│   └── conversation_chain.py # Enhanced chain with memory
├── graphs/
│   ├── basic_graph.py        # Original basic graph
│   ├── conversation_graph.py # Enhanced graph with memory
│   └── smart_graph.py        # Smart graph with task routing
├── handlers/                 # Specialized task handlers
│   ├── __init__.py
│   ├── base_handler.py      # Base handler class
│   ├── task_router.py       # Task routing logic
│   ├── registry.py          # Handler registry system
│   ├── destination_handler.py # Destination queries
│   ├── attractions_handler.py # Attractions and activities
│   └── packing_handler.py   # Packing and preparation
├── logger.py                # Lightweight logging system
├── memory/                   # Memory and conversation system
│   ├── __init__.py
│   ├── types.py             # Data structures for memory
│   ├── memory_store.py      # Persistent memory storage
│   └── conversation_manager.py # Conversation state management
└── models/
    └── hf_loader.py         # HuggingFace model loading
```

## Architecture

The system is built with a modular architecture that separates concerns:

1. **Smart Task Routing**: Automatically routes user queries to specialized handlers
2. **Specialized Handlers**: Dedicated handlers for different types of travel queries
3. **Memory System**: Handles persistent storage and retrieval of conversation history and user preferences
4. **Conversation Manager**: Orchestrates conversation state and context building
5. **Enhanced Chains/Graphs**: Integrate memory and context into LLM processing
6. **CLI Interface**: Provides multiple interaction modes and management tools

## Notes
- If `torch` install fails on Windows, install the correct wheel from PyTorch website, then `pip install -r requirements.txt` again.
- The default `distilgpt2` is not ideal for chat; change to a chat/causal model like `TinyLlama/TinyLlama-1.1B-Chat-v1.0`.
- For large models, consider `bitsandbytes`, `auto-gptq`, or `transformers` `device_map="auto"`.
- Memory is stored in JSON format by default; for production use, consider a proper database.
- The memory extraction is currently rule-based; for production, consider using NLP models for better extraction.
