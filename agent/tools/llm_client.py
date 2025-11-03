"""LLM client with audit logging."""
import os
import time
import structlog
from typing import Optional, Dict, Any
from openai import OpenAI

logger = structlog.get_logger()

_client: Optional[OpenAI] = None


def get_client() -> OpenAI:
    """Get or create OpenAI client."""
    global _client
    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not set")
        _client = OpenAI(api_key=api_key)
    return _client


def call_llm(
    prompt: str,
    model: str = "gpt-4o",
    system_prompt: Optional[str] = None,
    temperature: float = 0.7,
    run_id: Optional[str] = None,
) -> str:
    """Call LLM with audit logging."""
    client = get_client()
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    start = time.time()
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=2000,
        )
        latency_ms = int((time.time() - start) * 1000)
        content = response.choices[0].message.content or ""

        # Audit logging (would integrate with Supabase prompts/completions tables)
        if run_id:
            logger.info(
                "LLM call",
                run_id=run_id,
                model=model,
                prompt_len=len(prompt),
                response_len=len(content),
                latency_ms=latency_ms,
            )

        return content
    except Exception as e:
        logger.error("LLM call failed", error=str(e), model=model)
        raise

