"""Ollama LLM integration for travel buddy."""

from typing import Optional
import ollama


def generate_ollama(prompt: str, model: str = "llama2", max_tokens: Optional[int] = None, 
                   temperature: Optional[float] = None, top_p: Optional[float] = None, max_ctx: Optional[int] = None, ollama_flash_attention: Optional[bool] = None) -> str:
    """
    Generates a text response using the specified language model and customization options.

    Parameters
    ----------
    prompt : str
        The input prompt or text to generate a response for.
    model : str, optional
        The name of the language model to use. Defaults to "llama2".
    max_tokens : Optional[int], optional
        The maximum number of tokens to generate. If not specified, the default
        behavior of the model is used.
    temperature : Optional[float], optional
        The sampling temperature for randomness control. Higher values result
        in more randomness, lower values make the output more deterministic.
        If not specified, the default value is used.
    top_p : Optional[float], optional
        Controls nucleus sampling by selecting only the top cumulative
        probability tokens. If not specified, the default value is used.
    max_ctx : Optional[int], optional
        The maximum context window size for the model. This parameter
        is not utilized directly in the function.
    ollama_flash_attentio : Optional[bool], optional
        A flag for enabling or customizing flash attention in the model. This
        parameter is not utilized directly in the function.

    Returns
    -------
    str
        The generated response as a string, stripped of excess whitespace.

    Raises
    ------
    RuntimeError
        If there is an exception while interacting with the language model
        or processing the response.
    """
    try:
        options = {}
        if max_tokens is not None:
            options["num_predict"] = max_tokens
        if temperature is not None:
            options["temperature"] = temperature
        if top_p is not None:
            options["top_p"] = top_p
        if ollama_flash_attention is not None:
            options["flash_attention"] = ollama_flash_attention
        if max_ctx is not None:
            options["max_ctx"] = max_ctx
        
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
