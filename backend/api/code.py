from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.database import get_db
from schemas.code import (
    CodeRequest,
    CodeExplanationResponse,
    CodeReviewResponse,
)
from services.explanation_service import generate_code_explanation
from services.review_service import review_code


router = APIRouter(
    tags=["Code AI"]
)


@router.post(
    "/explain",
    response_model=CodeExplanationResponse,
)
def explain_code(
    request: CodeRequest,
    db: Session = Depends(get_db),
):
    try:
        result = generate_code_explanation(
            db=db,
            file_id=request.file_id,
        )

        return result

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    except RuntimeError as error:
        raise HTTPException(
            status_code=500,
            detail=str(error),
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {error}",
        )


@router.post(
    "/review",
    response_model=CodeReviewResponse,
)
def review_code_file(
    request: CodeRequest,
    db: Session = Depends(get_db),
):
    try:
        result = review_code(
            db=db,
            file_id=request.file_id,
        )

        return result

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    except RuntimeError as error:
        raise HTTPException(
            status_code=500,
            detail=str(error),
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {error}",
        )