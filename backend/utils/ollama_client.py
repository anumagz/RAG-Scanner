import os
from typing import Any

import httpx
from dotenv import load_dotenv


load_dotenv()


OLLAMA_URL = os.getenv(
    "OLLAMA_URL",
    "http://localhost:11434"
).rstrip("/")

CHAT_MODEL = os.getenv(
    "OLLAMA_CHAT_MODEL",
    "qwen2.5:3b"
)

SUMMARY_MODEL = os.getenv(
    "OLLAMA_SUMMARY_MODEL",
    "llama3.2"
)

CODE_MODEL = os.getenv(
    "OLLAMA_CODE_MODEL",
    "deepseek-coder"
)

EMBED_MODEL = os.getenv(
    "OLLAMA_EMBED_MODEL",
    "nomic-embed-text"
)


def generate(
    prompt: str,
    model: str = CHAT_MODEL,
    system: str | None = None,
    temperature: float = 0.2,
) -> str:

    payload: dict[str, Any] = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": temperature,
        },
    }

    if system:
        payload["system"] = system

    response = httpx.post(
        f"{OLLAMA_URL}/api/generate",
        json=payload,
        timeout=600,
    )

    response.raise_for_status()

    data = response.json()

    return data.get("response", "").strip()


def embed(
    text: str,
    model: str = EMBED_MODEL,
) -> list[float]:

    response = httpx.post(
        f"{OLLAMA_URL}/api/embed",
        json={
            "model": model,
            "input": text,
        },
        timeout=300,
    )

    if response.status_code == 404:
        # Compatibility with older Ollama versions
        response = httpx.post(
            f"{OLLAMA_URL}/api/embeddings",
            json={
                "model": model,
                "prompt": text,
            },
            timeout=300,
        )

        response.raise_for_status()

        data = response.json()

        return data["embedding"]

    response.raise_for_status()

    data = response.json()

    embeddings = data.get("embeddings")

    if not embeddings:
        raise RuntimeError(
            "Ollama returned no embeddings."
        )

    return embeddings[0]


def embed_many(
    texts: list[str],
    model: str = EMBED_MODEL,
) -> list[list[float]]:

    if not texts:
        return []

    response = httpx.post(
        f"{OLLAMA_URL}/api/embed",
        json={
            "model": model,
            "input": texts,
        },
        timeout=600,
    )

    if response.status_code == 404:
        return [
            embed(text, model)
            for text in texts
        ]

    response.raise_for_status()

    data = response.json()

    embeddings = data.get("embeddings")

    if not embeddings:
        raise RuntimeError(
            "Ollama returned no embeddings."
        )

    return embeddings


def check_ollama() -> bool:

    try:
        response = httpx.get(
            f"{OLLAMA_URL}/api/tags",
            timeout=10,
        )

        return response.status_code == 200

    except Exception:
        return False