# Travel Buddy - Local HF LLM + LangChain + LangGraph

Minimal skeleton to run a local HuggingFace model with Pydantic config, LangChain chain, and LangGraph app.

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

## Run
- LangChain chain:
  ```bash
  python -m travel_buddy chain "Plan a 3-day trip to Rome on a budget"
  ```
- LangGraph app:
  ```bash
  python -m travel_buddy graph "Suggest family-friendly attractions in Kyoto"
  ```

## Project Structure
```
src/
  travel_buddy/
    config/settings.py
    models/hf_loader.py
    chains/basic_chain.py
    graphs/basic_graph.py
    cli.py
```

## Notes
- If `torch` install fails on Windows, install the correct wheel from PyTorch website, then `pip install -r requirements.txt` again.
- The default `distilbert-base-uncased` is not a causal LM; change to a chat/causal model like `TinyLlama/TinyLlama-1.1B-Chat-v1.0`.
- For large models, consider `bitsandbytes`, `auto-gptq`, or `transformers` `device_map="auto"`.
