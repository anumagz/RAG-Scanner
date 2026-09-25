from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey
)

from database.database import Base


class File(Base):

    __tablename__ = "files"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    repository_id = Column(
        Integer,
        ForeignKey(
            "repositories.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    file_name = Column(
        String,
        nullable=False
    )

    file_path = Column(
        String,
        nullable=False
    )

    file_type = Column(
        String,
        nullable=False
    )

    category = Column(
        String,
        nullable=True
    )

    modified_at = Column(
        DateTime,
        nullable=True
    )

    file_hash = Column(
        String,
        nullable=True
    )

    indexed_at = Column(
        DateTime,
        nullable=True
    )