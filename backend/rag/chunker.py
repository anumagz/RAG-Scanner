import os

from parsers.base import ParsedDocument


DEFAULT_CHUNK_SIZE = int(
    os.getenv(
        "RAG_CHUNK_SIZE",
        "500",
    )
)

DEFAULT_CHUNK_OVERLAP = int(
    os.getenv(
        "RAG_CHUNK_OVERLAP",
        "50",
    )
)


def chunk_document(
    document: ParsedDocument,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[ParsedDocument]:

    text = document.text.strip()

    if not text:
        return []

    if chunk_size <= 0:
        raise ValueError(
            "chunk_size must be greater than zero."
        )

    overlap = max(
        0,
        min(overlap, chunk_size - 1),
    )

    words = text.split()

    if len(words) <= chunk_size:
        return [document]

    chunks = []

    start = 0
    chunk_number = 0

    while start < len(words):

        end = min(
            start + chunk_size,
            len(words),
        )

        chunk_text = " ".join(
            words[start:end]
        )

        metadata = dict(
            document.metadata
        )

        metadata["chunk"] = chunk_number

        chunks.append(
            ParsedDocument(
                text=chunk_text,
                metadata=metadata,
            )
        )

        chunk_number += 1

        if end >= len(words):
            break

        start = end - overlap

    return chunks


def chunk_documents(
    documents: list[ParsedDocument],
) -> list[ParsedDocument]:

    results = []

    for document in documents:

        results.extend(
            chunk_document(document)
        )

    return results
