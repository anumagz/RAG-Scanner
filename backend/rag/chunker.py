from parsers.base import ParsedDocument


def chunk_document(
    document: ParsedDocument,
    chunk_size: int = 1000,
    overlap: int = 100,
) -> list[ParsedDocument]:

    text = document.text.strip()

    if not text:
        return []

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