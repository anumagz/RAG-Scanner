from sqlalchemy import (
    Column,
    Integer,
    Text,
    ForeignKey
)

from database.database import Base


class RepositorySummary(Base):

    __tablename__ = "repository_summaries"

    id = Column(
        Integer,
        primary_key=True
    )

    repository_id = Column(
        Integer,
        ForeignKey(
            "repositories.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        unique=True
    )

    summary = Column(
        Text,
        nullable=False
    )


class FileSummary(Base):

    __tablename__ = "file_summaries"

    id = Column(
        Integer,
        primary_key=True
    )

    file_id = Column(
        Integer,
        ForeignKey(
            "files.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        unique=True
    )

    summary = Column(
        Text,
        nullable=False
    )