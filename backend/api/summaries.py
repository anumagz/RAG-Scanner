from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.database import get_db
from models.repository import Repository
from models.summary import RepositorySummary, FileSummary


router = APIRouter(
    tags=["Summaries"]
)


@router.get("/repositories/{repository_id}/summary")
def get_repository_summary(
    repository_id: int,
    db: Session = Depends(get_db)
):
    repository = (
        db.query(Repository)
        .filter(Repository.id == repository_id)
        .first()
    )

    if not repository:
        raise HTTPException(
            status_code=404,
            detail="Repository not found"
        )

    summary = (
        db.query(RepositorySummary)
        .filter(
            RepositorySummary.repository_id == repository_id
        )
        .first()
    )

    if not summary:
        return {
            "repository_id": repository_id,
            "summary": None,
            "message": "Repository summary has not been generated yet."
        }

    return {
        "repository_id": repository_id,
        "summary": summary.summary
    }


@router.get("/files/{file_id}/summary")
def get_file_summary(
    file_id: int,
    db: Session = Depends(get_db)
):
    summary = (
        db.query(FileSummary)
        .filter(FileSummary.file_id == file_id)
        .first()
    )

    if not summary:
        return {
            "file_id": file_id,
            "summary": None,
            "message": "File summary has not been generated yet."
        }

    return {
        "file_id": file_id,
        "summary": summary.summary
    }