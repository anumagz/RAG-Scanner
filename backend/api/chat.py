import json

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from schemas.chat import (
    ChatRequest,
    ChatResponse,
)

from services.chat_service import (
    chat,
    stream_chat,
)


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


@router.post(
    "/stream",
)
def stream_chat_repository(
    request: ChatRequest,
):

    def event_stream():

        try:

            for event in stream_chat(
                question=request.question,
                repository_id=request.repository_id,
            ):

                yield (
                    json.dumps(
                        event,
                        separators=(",", ":"),
                    )
                    + "\n"
                )

        except Exception as error:

            yield (
                json.dumps(
                    {
                        "type": "error",
                        "message": str(error),
                    },
                    separators=(",", ":"),
                )
                + "\n"
            )

    return StreamingResponse(
        event_stream(),
        media_type="application/x-ndjson",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
