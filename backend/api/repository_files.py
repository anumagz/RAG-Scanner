from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.database import get_db
from models.repository import Repository
from models.file import File


router = APIRouter(
    prefix="/repositories",
    tags=["Repository Files"]
)


@router.get("/{repository_id}/files")
def get_repository_files(
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

    files = (
        db.query(File)
        .filter(File.repository_id == repository_id)
        .order_by(File.file_path)
        .all()
    )

    return [
        {
            "id": file.id,
            "repository_id": file.repository_id,
            "file_name": file.file_name,
            "file_path": file.file_path,
            "file_type": file.file_type,
            "category": file.category,
            "modified_at": file.modified_at,
        }
        for file in files
    ]