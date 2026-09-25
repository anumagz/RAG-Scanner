from fastapi import APIRouter, HTTPException

from schemas.chat import (
    ChatRequest,
    ChatResponse,
)

from services.chat_service import chat


router = APIRouter(
    prefix="/chat",
    tags=["AI Chat"],
)


@router.post(
    "",
    response_model=ChatResponse,
)
def chat_repository(
    request: ChatRequest,
):

    try:

        result = chat(
            question=request.question,
            repository_id=request.repository_id,
        )

        return result

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error),
        )