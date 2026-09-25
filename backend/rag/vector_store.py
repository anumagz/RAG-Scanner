import os
from typing import Any

import chromadb
from dotenv import load_dotenv


load_dotenv()


CHROMA_PATH = os.getenv(
    "CHROMA_PATH",
    "./chroma_db",
)

COLLECTION_NAME = os.getenv(
    "CHROMA_COLLECTION",
    "repository_documents",
)


client = chromadb.PersistentClient(
    path=CHROMA_PATH
)

collection = client.get_or_create_collection(
    name=COLLECTION_NAME,
    metadata={
        "description": (
            "Repository Scanner RAG documents"
        )
    },
)


def upsert_chunks(
    ids: list[str],
    documents: list[str],
    embeddings: list[list[float]],
    metadatas: list[dict[str, Any]],
):

    if not ids:
        return

    collection.upsert(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
    )


def search(
    embedding: list[float],
    n_results: int = 6,
    where: dict | None = None,
):

    kwargs = {
        "query_embeddings": [embedding],
        "n_results": n_results,
    }

    if where:
        kwargs["where"] = where

    return collection.query(
        **kwargs
    )


def delete_file_chunks(
    file_id: int,
):

    collection.delete(
        where={
            "file_id": file_id
        }
    )


def delete_repository_chunks(
    repository_id: int,
):

    collection.delete(
        where={
            "repository_id": repository_id
        }
    )


def count() -> int:
    return collection.count()