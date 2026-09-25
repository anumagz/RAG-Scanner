from datetime import datetime

from pydantic import BaseModel, ConfigDict


class RepositoryCreate(BaseModel):

    path: str


class RepositoryResponse(BaseModel):

    id: int

    name: str

    path: str

    status: str

    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )