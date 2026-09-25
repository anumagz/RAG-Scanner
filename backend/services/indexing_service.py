from datetime import datetime

from sqlalchemy.orm import Session

from database.database import SessionLocal

from models.repository import Repository
from models.file import File

from scanner.scanner import scan_repository

from parsers.parser_factory import get_parser
from rag.chunker import chunk_documents
from rag.vector_store import (
    delete_file_chunks,
    upsert_chunks,
)

from utils.ollama_client import (
    embed_many,
)


def index_ai_file(
    file: File,
):

    parser = get_parser(
        file.file_path
    )

    if parser is None:
        return 0

    documents = parser.parse(
        file.file_path,
        file.id,
    )

    chunks = chunk_documents(
        documents
    )

    if not chunks:
        return 0

    texts = [
        chunk.text
        for chunk in chunks
    ]

    embeddings = embed_many(
        texts
    )

    ids = []
    metadatas = []

    for index, chunk in enumerate(
        chunks
    ):

        metadata = dict(
            chunk.metadata
        )

        metadata[
            "repository_id"
        ] = file.repository_id

        metadata[
            "file_id"
        ] = file.id

        metadata[
            "category"
        ] = file.category or ""

        metadata[
            "file_type"
        ] = file.file_type or ""

        chunk_id = (
            f"file_{file.id}"
            f"_chunk_{index}"
        )

        ids.append(chunk_id)
        metadatas.append(metadata)

    # Remove previous vectors for this file
    delete_file_chunks(
        file.id
    )

    upsert_chunks(
        ids=ids,
        documents=texts,
        embeddings=embeddings,
        metadatas=metadatas,
    )

    return len(chunks)


def index_repository(
    repository_id: int,
):

    db: Session = SessionLocal()

    try:

        repository = (
            db.query(Repository)
            .filter(
                Repository.id
                == repository_id
            )
            .first()
        )

        if not repository:
            return

        repository.status = "Running"
        db.commit()

        scanned_files = scan_repository(
            repository.path
        )

        existing_files = {
            file.file_path: file
            for file in db.query(File)
            .filter(
                File.repository_id
                == repository.id
            )
            .all()
        }

        # -----------------------------------------
        # SQLite file indexing
        # -----------------------------------------

        for file_data in scanned_files:

            existing = existing_files.get(
                file_data["file_path"]
            )

            if existing:

                if (
                    existing.file_hash
                    == file_data["file_hash"]
                ):
                    continue

                existing.file_name = (
                    file_data["file_name"]
                )

                existing.file_type = (
                    file_data["file_type"]
                )

                existing.category = (
                    file_data["category"]
                )

                existing.modified_at = (
                    file_data["modified_at"]
                )

                existing.file_hash = (
                    file_data["file_hash"]
                )

                existing.indexed_at = (
                    datetime.utcnow()
                )

                db.commit()

            else:

                existing = File(
                    repository_id=repository.id,
                    **file_data,
                    indexed_at=datetime.utcnow(),
                )

                db.add(existing)
                db.commit()
                db.refresh(existing)

        # -----------------------------------------
        # AI indexing
        # -----------------------------------------

        files = (
            db.query(File)
            .filter(
                File.repository_id
                == repository.id
            )
            .all()
        )

        total = len(files)

        print(
            f"AI indexing {total} files..."
        )

        for index, file in enumerate(
            files,
            start=1,
        ):

            try:

                print(
                    f"[AI {index}/{total}] "
                    f"{file.file_name}"
                )

                chunk_count = index_ai_file(
                    file
                )

                file.indexed_at = (
                    datetime.utcnow()
                )

                db.commit()

                print(
                    f"  -> {chunk_count} chunks"
                )

            except Exception as error:

                print(
                    f"  -> AI indexing failed: "
                    f"{error}"
                )

                db.rollback()

        repository.status = "Completed"
        db.commit()

        print(
            f"Repository {repository.id} "
            f"AI indexing completed."
        )

    except Exception as error:

        repository = (
            db.query(Repository)
            .filter(
                Repository.id
                == repository_id
            )
            .first()
        )

        if repository:

            repository.status = "Failed"
            db.commit()

        print(
            f"Repository indexing failed: "
            f"{error}"
        )

        raise

    finally:

        db.close()