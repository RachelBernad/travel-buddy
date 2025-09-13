from __future__ import annotations

from typing import Optional

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline, TextGenerationPipeline

from travel_buddy.settings import settings


def get_dtype(dtype_name: Optional[str]) -> Optional[torch.dtype]:
    if not dtype_name:
        return None
    name = dtype_name.lower()
    mapping = {
        "float16": torch.float16,
        "bfloat16": torch.bfloat16,
        "float32": torch.float32,
    }
    return mapping.get(name)


def load_local_hf_pipeline(model_id: Optional[str] = None, max_new_tokens: Optional[int] = None, temperature: Optional[float] = None, top_k: Optional[float] = None, top_p: Optional[float] = None) -> TextGenerationPipeline:
    model_id = model_id or settings.hf_model_id

    device = 0 if settings.hf_device.lower() in {"cuda", "gpu"} and torch.cuda.is_available() else -1

    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        device_map="auto" if device == 0 else None,
    )

    text_gen = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        device=device,
        max_new_tokens=max_new_tokens or settings.max_new_tokens,
        do_sample=True,
        temperature=temperature if temperature is not None else settings.temperature,
        top_p=top_p if top_p is not None else settings.top_p,
        top_k=top_k if top_k is not None else settings.top_k,
    )

    return text_gen


def generate(prompt: str, max_new_tokens: Optional[int] = None, temperature: Optional[float] = None, top_k: Optional[float] = None, top_p: Optional[float] = None) -> str:
    pipe = load_local_hf_pipeline()
    outputs = pipe(
        prompt,
        max_new_tokens=max_new_tokens or settings.max_new_tokens,
        do_sample=True,
        temperature=temperature if temperature is not None else settings.temperature,
        top_p=top_p if top_p is not None else settings.top_p,
        top_k=top_k if top_k is not None else settings.top_k,
        pad_token_id=pipe.tokenizer.eos_token_id,
    )
    return outputs[0]["generated_text"]
