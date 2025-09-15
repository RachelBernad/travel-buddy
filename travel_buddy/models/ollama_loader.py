"""Ollama LLM integration for travel buddy."""

from typing import Optional
import ollama


def generate_ollama(prompt: str, model: str = "llama2", max_tokens: Optional[int] = None, 
                   temperature: Optional[float] = None, top_p: Optional[float] = None) -> str:
    """
    Generate text using Ollama.
    
    Args:
        prompt: Input prompt
        model: Ollama model name
        max_tokens: Maximum tokens to generate
        temperature: Sampling temperature
        top_p: Top-p sampling parameter
        
    Returns:
        Generated text response
    """
    try:
        options = {}
        if max_tokens is not None:
            options["num_predict"] = max_tokens
        if temperature is not None:
            options["temperature"] = temperature
        if top_p is not None:
            options["top_p"] = top_p
        
        response = ollama.generate(
            model=model,
            prompt=prompt,
            options=options
        )
        
        return response["response"].strip()
        
    except Exception as e:
        raise RuntimeError(f"Ollama error: {e}")


def check_ollama_available() -> bool:
    try:
        ollama.list()
        return True
    except Exception:
        return False
