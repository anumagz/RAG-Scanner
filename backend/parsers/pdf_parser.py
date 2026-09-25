from pathlib import Path

import fitz

from parsers.base import BaseParser, ParsedDocument


class PDFParser(BaseParser):

    def parse(
        self,
        file_path: str,
        file_id: int | None = None,
    ):

        path = Path(file_path)

        documents = []

        pdf = fitz.open(str(path))

        try:

            for page_number, page in enumerate(
                pdf,
                start=1,
            ):

                text = page.get_text(
                    "text"
                ).strip()

                if not text:
                    continue

                documents.append(
                    ParsedDocument(
                        text=text,
                        metadata={
                            "file": path.name,
                            "file_path": str(path),
                            "file_id": file_id,
                            "page": page_number,
                            "type": "pdf",
                        },
                    )
                )

        finally:
            pdf.close()

        return documents