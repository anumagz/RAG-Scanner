from pathlib import Path


SUPPORTED_EXTENSIONS = {
    ".py",
    ".js",
    ".ts",
    ".java",
    ".cs",
    ".sql",

    ".md",
    ".txt",

    ".pdf",
    ".docx",
    ".pptx",

    ".xlsx",
    ".csv",

    ".json",
    ".xml",
    ".yaml",
    ".yml"
}


CATEGORY_MAP = {

    ".py": "Code",
    ".js": "Code",
    ".ts": "Code",
    ".java": "Code",
    ".cs": "Code",
    ".sql": "Code",

    ".pdf": "PDF",

    ".docx": "Documents",
    ".md": "Documents",

    ".pptx": "PowerPoint",

    ".xlsx": "Excel",

    ".csv": "Data",

    ".json": "Configuration",
    ".xml": "Configuration",
    ".yaml": "Configuration",
    ".yml": "Configuration",

    ".txt": "Text"
}


def is_supported_file(path: Path) -> bool:

    return (
        path.is_file()
        and path.suffix.lower()
        in SUPPORTED_EXTENSIONS
    )


def get_file_category(path: Path) -> str:

    return CATEGORY_MAP.get(
        path.suffix.lower(),
        "Other"
    )


def get_file_type(path: Path) -> str:

    return path.suffix.lower()