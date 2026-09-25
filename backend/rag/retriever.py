import os

from rag.vector_store import search
from utils.ollama_client import embed


TOP_K = int(
    os.getenv(
        "RAG_TOP_K",
        "6"
    )
)


def retrieve(
    question: str,
    repository_id: int | None = None,
    top_k: int = TOP_K,
):

    question_embedding = embed(
        question
    )

    where = None

    if repository_id is not None:
        where = {
            "repository_id": repository_id
        }

    result = search(
        embedding=question_embedding,
        n_results=top_k,
        where=where,
    )

    documents = (
        result.get("documents", [[]])[0]
    )

    metadatas = (
        result.get("metadatas", [[]])[0]
    )

    distances = (
        result.get("distances", [[]])[0]
    )

    chunks = []

    for index, document in enumerate(
        documents
    ):

        metadata = (
            metadatas[index]
            if index < len(metadatas)
            else {}
        )

        distance = (
            distances[index]
            if index < len(distances)
            else None
        )

        chunks.append(
            {
                "text": document,
                "metadata": metadata,
                "distance": distance,
            }
        )

    return chunks