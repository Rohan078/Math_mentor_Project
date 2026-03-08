"""Groq LLM client for chat completions."""
import os
from typing import Optional
from groq import Groq
from app.config import GROQ_API_KEY, GROQ_CHAT_MODEL


def _clean_key(key: Optional[str]) -> str:
    if not key:
        return ""
    return key.strip().strip('"').strip("'")


def get_client() -> Groq:
    key = _clean_key(GROQ_API_KEY or os.getenv("GROQ_API_KEY"))
    if not key:
        raise ValueError("GROQ_API_KEY not set. Add it to .env or environment.")
    if key == "your_groq_api_key_here":
        raise ValueError(
            "Replace 'your_groq_api_key_here' in .env with your real Groq API key from https://console.groq.com/"
        )
    return Groq(api_key=key)


def chat(
    messages: list[dict],
    model: Optional[str] = None,
    temperature: float = 0.3,
    max_tokens: int = 2048,
) -> str:
    client = get_client()
    model = model or GROQ_CHAT_MODEL
    resp = client.chat.completions.create(
        messages=messages,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return resp.choices[0].message.content or ""


def chat_json(
    messages: list[dict],
    model: Optional[str] = None,
    temperature: float = 0.2,
) -> str:
    return chat(messages=messages, model=model, temperature=temperature, max_tokens=2048)
