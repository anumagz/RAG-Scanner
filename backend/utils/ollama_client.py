import json
import os
from collections.abc import Iterator
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

OLLAMA_KEEP_ALIVE = os.getenv(
    "OLLAMA_KEEP_ALIVE",
    "15m",
)

HTTP_TIMEOUT = httpx.Timeout(
    timeout=600.0,
    connect=10.0,
)

_http_client = httpx.Client(
    timeout=HTTP_TIMEOUT,
    limits=httpx.Limits(
        max_connections=20,
        max_keepalive_connections=10,
    ),
)


def _generate_payload(
    prompt: str,
    model: str,
    system: str | None,
    temperature: float,
    stream: bool,
    num_predict: int | None,
) -> dict[str, Any]:

    options: dict[str, Any] = {
        "temperature": temperature,
    }

    if num_predict is not None:
        options["num_predict"] = num_predict

    payload: dict[str, Any] = {
        "model": model,
        "prompt": prompt,
        "stream": stream,
        "keep_alive": OLLAMA_KEEP_ALIVE,
        "options": options,
    }

    if system:
        payload["system"] = system

    return payload


def generate(
    prompt: str,
    model: str = CHAT_MODEL,
    system: str | None = None,
    temperature: float = 0.2,
    num_predict: int | None = None,
) -> str:

    response = _http_client.post(
        f"{OLLAMA_URL}/api/generate",
        json=_generate_payload(
            prompt=prompt,
            model=model,
            system=system,
            temperature=temperature,
            stream=False,
            num_predict=num_predict,
        ),
    )

    response.raise_for_status()

    data = response.json()

    return data.get("response", "").strip()


def stream_generate(
    prompt: str,
    model: str = CHAT_MODEL,
    system: str | None = None,
    temperature: float = 0.2,
    num_predict: int | None = None,
) -> Iterator[str]:

    with _http_client.stream(
        "POST",
        f"{OLLAMA_URL}/api/generate",
        json=_generate_payload(
            prompt=prompt,
            model=model,
            system=system,
            temperature=temperature,
            stream=True,
            num_predict=num_predict,
        ),
    ) as response:

        response.raise_for_status()

        for line in response.iter_lines():

            if not line:
                continue

            data = json.loads(line)

            if data.get("error"):
                raise RuntimeError(
                    str(data["error"])
                )

            token = data.get(
                "response",
                "",
            )

            if token:
                yield token


def embed(
    text: str,
    model: str = EMBED_MODEL,
) -> list[float]:

    response = _http_client.post(
        f"{OLLAMA_URL}/api/embed",
        json={
            "model": model,
            "input": text,
            "keep_alive": OLLAMA_KEEP_ALIVE,
        },
        timeout=300,
    )

    if response.status_code == 404:
        # Compatibility with older Ollama versions
        response = _http_client.post(
            f"{OLLAMA_URL}/api/embeddings",
            json={
                "model": model,
                "prompt": text,
                "keep_alive": OLLAMA_KEEP_ALIVE,
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

    response = _http_client.post(
        f"{OLLAMA_URL}/api/embed",
        json={
            "model": model,
            "input": texts,
            "keep_alive": OLLAMA_KEEP_ALIVE,
        },
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
        response = _http_client.get(
            f"{OLLAMA_URL}/api/tags",
            timeout=10,
        )

        return response.status_code == 200

    except Exception:
        return False
