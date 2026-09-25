from database.database import Base, engine

from models.repository import Repository
from models.file import File
from models.summary import (
    RepositorySummary,
    FileSummary
)


def init_database():

    Base.metadata.create_all(
        bind=engine
    )

    print("Database initialized successfully.")


if __name__ == "__main__":

    init_database()