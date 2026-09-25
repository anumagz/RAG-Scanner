from pydantic import BaseModel, Field


class ChatRequest(BaseModel):

    repository_id: int | None = None

    question: str = Field(
        min_length=1
    )


class ChatSource(BaseModel):

    file: str | None = None
    file_id: int | None = None

    start_line: int | None = None
    end_line: int | None = None

    page: int | None = None
    slide: int | None = None
    sheet: str | None = None


class ChatResponse(BaseModel):

    answer: str

    sources: list[ChatSource]