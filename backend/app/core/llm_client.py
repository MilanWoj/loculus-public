# Author: MilanWoj
import json
from collections.abc import AsyncGenerator

import httpx
from app.core.config import settings


class LLMError(Exception):
    pass


async def stream_chat_completion(messages: list[dict]) -> AsyncGenerator[str, None]:
    payload = {"messages": messages, "temperature": 0.3, "stream": True}

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream("POST", f"{settings.llm_base_url}/chat/completions", json=payload) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if not line or not line.startswith("data: "):
                        continue
                    data_str = line[len("data: "):]
                    if data_str.strip() == "[DONE]":
                        break
                    delta = json.loads(data_str)["choices"][0]["delta"].get("content")
                    if delta:
                        yield delta
    except httpx.ConnectError as exc:
        raise LLMError(f"Cannot reach the inference engine at {settings.llm_base_url}") from exc
    except httpx.HTTPStatusError as exc:
        raise LLMError(f"llama-server error: {exc.response.text}") from exc


async def complete_once(messages: list[dict], max_tokens: int = 200) -> str:
    payload = {"messages": messages, "temperature": 0.0, "max_tokens": max_tokens, "stream": False}
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(f"{settings.llm_base_url}/chat/completions", json=payload)
            response.raise_for_status()
    except httpx.ConnectError as exc:
        raise LLMError("Cannot reach the inference engine") from exc
    except httpx.HTTPStatusError as exc:
        raise LLMError(f"llama-server error: {exc.response.text}") from exc

    return response.json()["choices"][0]["message"]["content"]
