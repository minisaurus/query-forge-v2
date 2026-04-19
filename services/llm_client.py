import sys
import os
import json
import time
import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import config


def get_embedding(text: str) -> list[float]:
    resp = requests.post(
        "https://openrouter.ai/api/v1/embeddings",
        headers={
            "Authorization": f"Bearer {config.OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": config.OPENROUTER_EMBED_MODEL,
            "input": text,
        },
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["data"][0]["embedding"]


def call_llm(system_prompt: str, user_prompt: str, model: str = None, temperature: float = 0.7, max_tokens: int = 2000) -> str:
    model = model or config.ZHIPU_MODEL

    for attempt in range(config.MAX_RETRIES):
        try:
            resp = requests.post(
                f"{config.ZHIPU_BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {config.ZHIPU_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                },
                timeout=60,
            )
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"]
        except Exception as e:
            if attempt < config.MAX_RETRIES - 1:
                time.sleep((attempt + 1) * 2)
            else:
                raise


def call_llm_json(system_prompt: str, user_prompt: str, model: str = None, temperature: float = 0.3) -> dict | list:
    raw = call_llm(system_prompt, user_prompt, model=model, temperature=temperature)

    if "```json" in raw:
        raw = raw.split("```json")[1].split("```")[0]
    elif "```" in raw:
        raw = raw.split("```")[1].split("```")[0]

    return json.loads(raw.strip())
