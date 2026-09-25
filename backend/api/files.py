from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.database import get_db
from models.file import File


router = APIRouter(
    prefix="/files",
    tags=["Files"]
)


@router.get("/{file_id}")
def get_file(
    file_id: int,
    db: Session = Depends(get_db)
):
    file = (
        db.query(File)
        .filter(File.id == file_id)
        .first()
    )

    if not file:
        raise HTTPException(
            status_code=404,
            detail="File not found"
        )

    content = None

    try:
        path = Path(file.file_path)

        if (
            path.exists()
            and file.category in [
                "Code",
                "Documents",
                "Text",
                "Configuration",
                "Data"
            ]
        ):
            content = path.read_text(
                encoding="utf-8",
                errors="ignore"
            )

    except Exception:
        content = None

    return {
        "id": file.id,
        "repository_id": file.repository_id,
        "file_name": file.file_name,
        "file_path": file.file_path,
        "file_type": file.file_type,
        "category": file.category,
        "modified_at": file.modified_at,
        "content": content
    }