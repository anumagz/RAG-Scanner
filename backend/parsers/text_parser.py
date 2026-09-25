from pathlib import Path

from parsers.base import BaseParser, ParsedDocument


class TextParser(BaseParser):

    def parse(
        self,
        file_path: str,
        file_id: int | None = None,
    ) -> list[ParsedDocument]:

        path = Path(file_path)

        text = path.read_text(
            encoding="utf-8",
            errors="ignore",
        )

        return [
            ParsedDocument(
                text=text,
                metadata={
                    "file": path.name,
                    "file_path": str(path),
                    "file_id": file_id,
                    "type": "text",
                },
            )
        ]