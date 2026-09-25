from pathlib import Path

from parsers.base import BaseParser
from parsers.code_parser import CodeParser
from parsers.csv_parser import CSVParser
from parsers.docx_parser import DOCXParser
from parsers.pdf_parser import PDFParser
from parsers.pptx_parser import PPTXParser
from parsers.text_parser import TextParser
from parsers.xlsx_parser import XLSXParser


CODE_EXTENSIONS = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".java",
    ".cs",
    ".cpp",
    ".c",
    ".h",
    ".hpp",
    ".sql",
}


TEXT_EXTENSIONS = {
    ".txt",
    ".md",
    ".json",
    ".xml",
    ".yaml",
    ".yml",
    ".toml",
    ".ini",
    ".env",
}


def get_parser(
    file_path: str,
) -> BaseParser | None:

    extension = Path(
        file_path
    ).suffix.lower()

    if extension in CODE_EXTENSIONS:
        return CodeParser()

    if extension in TEXT_EXTENSIONS:
        return TextParser()

    if extension == ".pdf":
        return PDFParser()

    if extension == ".docx":
        return DOCXParser()

    if extension == ".pptx":
        return PPTXParser()

    if extension in {".xlsx", ".xls"}:
        return XLSXParser()

    if extension == ".csv":
        return CSVParser()

    return None