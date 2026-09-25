from pydantic import BaseModel


class CodeRequest(BaseModel):
    file_id: int


class ReviewIssue(BaseModel):
    severity: str
    issue: str
    line: int | None = None
    explanation: str
    suggested_fix: str | None = None


class CodeReviewResponse(BaseModel):
    file_id: int
    issues: list[ReviewIssue]
    raw_review: str


class CodeExplanationResponse(BaseModel):
    file_id: int
    explanation: str