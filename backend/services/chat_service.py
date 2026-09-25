import os
from collections.abc import Iterator

from rag.generator import (
    generate_answer,
    stream_answer,
)
from rag.retriever import retrieve


MAX_CONTEXT_CHARS = int(
    os.getenv(
        "RAG_MAX_CONTEXT_CHARS",
        "12000",
    )
)


def format_source(
    metadata: dict,
) -> dict:

    source = {
        "file": metadata.get(
            "file"
        ),
        "file_id": metadata.get(
            "file_id"
        ),
    }

    if metadata.get("start_line") is not None:

        source["start_line"] = metadata[
            "start_line"
        ]

        source["end_line"] = metadata[
            "end_line"
        ]

    if metadata.get("page") is not None:
        source["page"] = metadata[
            "page"
        ]

    if metadata.get("slide") is not None:
        source["slide"] = metadata[
            "slide"
        ]

    if metadata.get("sheet") is not None:
        source["sheet"] = metadata[
            "sheet"
        ]

    return source


def build_context(
    chunks: list[dict],
) -> tuple[str, list[dict]]:

    sections = []
    selected_chunks = []
    current_size = 0

    for index, chunk in enumerate(
        chunks,
        start=1,
    ):

        metadata = chunk[
            "metadata"
        ]

        source = metadata.get(
            "file",
            "Unknown",
        )

        if metadata.get("start_line"):

            location = (
                f"Lines "
                f"{metadata['start_line']}-"
                f"{metadata['end_line']}"
            )

        elif metadata.get("page"):

            location = (
                f"Page "
                f"{metadata['page']}"
            )

        elif metadata.get("slide"):

            location = (
                f"Slide "
                f"{metadata['slide']}"
            )

        elif metadata.get("sheet"):

            location = (
                f"Sheet "
                f"{metadata['sheet']}"
            )

        else:

            location = ""

        section = f"""
--- Context {index} ---
Source: {source}
{location}

{chunk['text']}
"""

        remaining = (
            MAX_CONTEXT_CHARS
            - current_size
        )

        if remaining <= 0:
            break

        if len(section) > remaining:
            section = section[:remaining]

        sections.append(section)
        selected_chunks.append(chunk)
        current_size += len(section)

        if current_size >= MAX_CONTEXT_CHARS:
            break

    return (
        "\n".join(sections),
        selected_chunks,
    )


def _sources_from_chunks(
    chunks: list[dict],
) -> list[dict]:

    sources = []
    seen = set()

    for chunk in chunks:

        metadata = chunk[
            "metadata"
        ]

        source = format_source(
            metadata
        )

        key = tuple(
            sorted(source.items())
        )

        if key not in seen:

            seen.add(key)
            sources.append(source)

    return sources


def _prepare_chat(
    question: str,
    repository_id: int | None,
) -> tuple[str | None, list[dict]]:

    chunks = retrieve(
        question=question,
        repository_id=repository_id,
    )

    if not chunks:
        return None, []

    context, selected_chunks = (
        build_context(chunks)
    )

    return (
        context,
        _sources_from_chunks(
            selected_chunks
        ),
    )


def chat(
    question: str,
    repository_id: int | None = None,
):

    context, sources = _prepare_chat(
        question=question,
        repository_id=repository_id,
    )

    if context is None:

        return {
            "answer": (
                "I could not find relevant "
                "information in the indexed repository."
            ),
            "sources": [],
        }

    answer = generate_answer(
        question=question,
        context=context,
    )

    return {
        "answer": answer,
        "sources": sources,
    }


def stream_chat(
    question: str,
    repository_id: int | None = None,
) -> Iterator[dict]:

    context, sources = _prepare_chat(
        question=question,
        repository_id=repository_id,
    )

    if context is None:

        yield {
            "type": "token",
            "content": (
                "I could not find relevant "
                "information in the indexed repository."
            ),
        }

        yield {
            "type": "sources",
            "sources": [],
        }

        yield {
            "type": "done",
        }

        return

    for token in stream_answer(
        question=question,
        context=context,
    ):

        yield {
            "type": "token",
            "content": token,
        }

    yield {
        "type": "sources",
        "sources": sources,
    }

    yield {
        "type": "done",
    }
