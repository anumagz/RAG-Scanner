from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException,
)
from sqlalchemy.orm import Session

from database.database import get_db
from models.repository import Repository

from schemas.repository import (
    RepositoryCreate,
    RepositoryResponse,
)

from services.repository_service import (
    create_repository,
)

from services.indexing_service import (
    index_repository,
)


router = APIRouter(
    prefix="/repositories",
    tags=["Repositories"],
)


# ---------------------------------------------------------
# CREATE REPOSITORY
# ---------------------------------------------------------

@router.post(
    "",
    response_model=RepositoryResponse,
)
def add_repository(
    request: RepositoryCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):

    try:

        repository = create_repository(
            db=db,
            path=request.path,
        )

        background_tasks.add_task(
            index_repository,
            repository.id,
        )

        return repository

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error),
        )


# ---------------------------------------------------------
# GET ALL REPOSITORIES
# ---------------------------------------------------------

@router.get(
    "",
    response_model=list[RepositoryResponse],
)
def get_repositories(
    db: Session = Depends(get_db),
):

    return (
        db.query(Repository)
        .order_by(Repository.created_at.desc())
        .all()
    )


# ---------------------------------------------------------
# GET SINGLE REPOSITORY
# ---------------------------------------------------------

@router.get(
    "/{repository_id}",
    response_model=RepositoryResponse,
)
def get_repository(
    repository_id: int,
    db: Session = Depends(get_db),
):

    repo = (
        db.query(Repository)
        .filter(
            Repository.id == repository_id
        )
        .first()
    )

    if not repo:

        raise HTTPException(
            status_code=404,
            detail="Repository not found",
        )

    return repo


# ---------------------------------------------------------
# DELETE REPOSITORY
# ---------------------------------------------------------

@router.delete(
    "/{repository_id}"
)
def delete_repository(
    repository_id: int,
    db: Session = Depends(get_db),
):

    repo = (
        db.query(Repository)
        .filter(
            Repository.id == repository_id
        )
        .first()
    )

    if not repo:

        raise HTTPException(
            status_code=404,
            detail="Repository not found",
        )

    db.delete(repo)
    db.commit()

    return {
        "message": "Repository deleted successfully"
    }


# ---------------------------------------------------------
# RESCAN REPOSITORY
# ---------------------------------------------------------

@router.post(
    "/{repository_id}/rescan"
)
def rescan_repository(
    repository_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):

    repo = (
        db.query(Repository)
        .filter(
            Repository.id == repository_id
        )
        .first()
    )

    if not repo:

        raise HTTPException(
            status_code=404,
            detail="Repository not found",
        )

    repo.status = "Queued"

    db.commit()

    background_tasks.add_task(
        index_repository,
        repository_id,
    )

    return {
        "message": "Repository rescan queued",
        "repository_id": repository_id,
    }