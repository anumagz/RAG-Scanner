import csv
from pathlib import Path

from parsers.base import BaseParser, ParsedDocument


class CSVParser(BaseParser):

    def parse(
        self,
        file_path: str,
        file_id: int | None = None,
    ):

        path = Path(file_path)

        rows = []

        with open(
            path,
            "r",
            encoding="utf-8",
            errors="ignore",
            newline="",
        ) as file:

            reader = csv.reader(file)

            for row in reader:

                rows.append(
                    " | ".join(row)
                )

        return [
            ParsedDocument(
                text="\n".join(rows),
                metadata={
                    "file": path.name,
                    "file_path": str(path),
                    "file_id": file_id,
                    "type": "csv",
                },
            )
        ]