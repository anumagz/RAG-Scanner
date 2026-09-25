from pathlib import Path
from sqlalchemy.orm import Session

from models.repository import Repository


def create_repository(db: Session, path: str):
    repository_path = Path(path)

    if not repository_path.exists():
        raise ValueError("Repository path does not exist.")

    if not repository_path.is_dir():
        raise ValueError("Repository path is not a directory.")

    # Automatically use the folder name
    name = repository_path.name

    existing = (
        db.query(Repository)
        .filter(Repository.path == str(repository_path))
        .first()
    )

    if existing:
        raise ValueError("Repository already exists.")

    repository = Repository(
        name=name,
        path=str(repository_path),
        status="Queued",
    )

    db.add(repository)
    db.commit()
    db.refresh(repository)

    return repository