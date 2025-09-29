from typing import Optional
from .ollama_loader import generate_ollama, check_ollama_available
from ..settings import settings
from ..logger import logger, log_model_call


def generate(prompt: str, custom_model: Optional[str] = None, max_new_tokens: Optional[int] = None,
            temperature: Optional[float] = None, top_p: Optional[float] = None, 
            top_k: Optional[int] = None) -> str:
    """
    Generate text using the configured LLM backend.
    
    Args:
        prompt: Input prompt
        custom_model: Custom model name to use for generation
        max_new_tokens: Maximum tokens to generate
        temperature: Sampling temperature
        top_p: Top-p sampling parameter
        top_k: Top-k sampling parameter
        
    Returns:
        Generated text response
    """
    # Determine actual values
    backend = settings.llm_backend.lower()
    model_name = custom_model if custom_model else settings.ollama_model
    actual_max_tokens = max_new_tokens or settings.max_new_tokens
    actual_temperature = temperature if temperature is not None else settings.temperature
    max_ctx = settings.max_ctx
    ollama_flash_attention = settings.ollama_flash_attention
    
    # Log with model identification and LangSmith integration
    logger.info(
        "LLM generation started",
        backend=backend,
        model=model_name,
        prompt_length=len(prompt),
        max_tokens=actual_max_tokens,
        temperature=actual_temperature,
        top_p=top_p if top_p is not None else settings.top_p,
        top_k=top_k if top_k is not None else settings.top_k,
        langsmith_project=settings.langchain_project,
        langsmith_tracing=settings.langchain_tracing_v2
    )

    if not check_ollama_available():
        raise RuntimeError("Ollama is not running. Please start Ollama service.")

    # Generate with timing
    import time
    start_time = time.time()
    
    try:
        response = generate_ollama(
            prompt=prompt,
            model=model_name,
            max_tokens=actual_max_tokens,
            temperature=actual_temperature,
            top_p=top_p if top_p is not None else settings.top_p,
            max_ctx=max_ctx,
            ollama_flash_attention=ollama_flash_attention
        )
        
        duration = time.time() - start_time
        response_length = len(response) if isinstance(response, str) else 0
        
        logger.info(
            "LLM generation completed",
            model=model_name,
            duration=f"{duration:.3f}s",
            response_length=response_length,
            tokens_per_sec=f"{response_length/duration:.1f}" if duration > 0 else "0",
            success=True
        )
        
        return response
        
    except Exception as e:
        duration = time.time() - start_time
        logger.error(
            "LLM generation failed",
            model=model_name,
            duration=f"{duration:.3f}s",
            error=str(e),
            success=False
        )
        raise
