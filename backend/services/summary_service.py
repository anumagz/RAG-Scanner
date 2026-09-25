from sqlalchemy.orm import Session

from models.file import File
from models.repository import Repository
from models.summary import (
    FileSummary,
    RepositorySummary,
)

from parsers.parser_factory import get_parser
from utils.ollama_client import generate


def generate_file_summary(
    db: Session,
    file: File,
):

    parser = get_parser(
        file.file_path
    )

    if parser is None:

        return None

    documents = parser.parse(
        file.file_path,
        file.id,
    )

    text = "\n\n".join(
        document.text
        for document in documents
    )

    if len(text) > 30000:
        text = text[:30000]

    prompt = f"""
Analyze the following repository file.

File:
{file.file_name}

File type:
{file.file_type}

Content:

{text}

Provide:

1. Purpose
2. Important Functions
3. Classes
4. Dependencies
5. Key Logic
6. Execution Flow

Do not invent information that is not
present in the file.
"""

    summary = generate(
        prompt,
        model="llama3.2",
        temperature=0.1,
    )

    existing = (
        db.query(FileSummary)
        .filter(
            FileSummary.file_id == file.id
        )
        .first()
    )

    if existing:

        existing.summary = summary

    else:

        db.add(
            FileSummary(
                file_id=file.id,
                summary=summary,
            )
        )

    db.commit()

    return summary


def generate_repository_summary(
    db: Session,
    repository: Repository,
):

    files = (
        db.query(File)
        .filter(
            File.repository_id
            == repository.id
        )
        .order_by(File.file_path)
        .all()
    )

    if not files:
        return None

    file_information = []

    for file in files:

        file_information.append(
            f"""
File: {file.file_name}
Path: {file.file_path}
Type: {file.file_type}
Category: {file.category}
"""
        )

    combined = "\n".join(
        file_information
    )

    if len(combined) > 30000:
        combined = combined[:30000]

    prompt = f"""
Analyze this software repository.

Repository:
{repository.name}

Files:

{combined}

Provide a structured repository overview:

1. Purpose
2. Architecture
3. Technologies
4. Modules
5. Business Flow
6. Dependencies
7. Important Files
8. Overall Execution Flow

Use only information that can be
reasonably derived from the supplied
repository information.
"""

    summary = generate(
        prompt,
        model="llama3.2",
        temperature=0.1,
    )

    existing = (
        db.query(RepositorySummary)
        .filter(
            RepositorySummary.repository_id
            == repository.id
        )
        .first()
    )

    if existing:

        existing.summary = summary

    else:

        db.add(
            RepositorySummary(
                repository_id=repository.id,
                summary=summary,
            )
        )

    db.commit()

    return summary