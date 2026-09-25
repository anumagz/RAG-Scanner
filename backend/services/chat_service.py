from rag.generator import generate_answer
from rag.retriever import retrieve


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
) -> str:

    sections = []

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

        sections.append(
            f"""
--- Context {index} ---
Source: {source}
{location}

{chunk['text']}
"""
        )

    return "\n".join(sections)


def chat(
    question: str,
    repository_id: int | None = None,
):

    chunks = retrieve(
        question=question,
        repository_id=repository_id,
    )

    if not chunks:

        return {
            "answer": (
                "I could not find relevant "
                "information in the indexed repository."
            ),
            "sources": [],
        }

    context = build_context(
        chunks
    )

    answer = generate_answer(
        question=question,
        context=context,
    )

    sources = []

    seen = set()

    for chunk in chunks:

        metadata = chunk[
            "metadata"
        ]

        source = format_source(
            metadata
        )

        key = str(source)

        if key not in seen:

            seen.add(key)
            sources.append(source)

    return {
        "answer": answer,
        "sources": sources,
    }