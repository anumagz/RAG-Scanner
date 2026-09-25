from pathlib import Path
from datetime import datetime

from scanner.file_detector import (
    is_supported_file,
    get_file_category,
    get_file_type,
)
from utils.hashing import calculate_file_hash


# Directories that should never be scanned
EXCLUDED_DIRECTORIES = {
    ".git",
    ".venv",
    "venv",
    "env",
    "node_modules",
    "dist",
    "build",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".next",
    ".nuxt",
    "coverage",
    ".idea",
    ".vscode",
}


def scan_repository(repository_path: str):
    root = Path(repository_path).resolve()

    if not root.exists():
        raise FileNotFoundError(
            f"Repository does not exist: {root}"
        )

    if not root.is_dir():
        raise NotADirectoryError(
            f"Not a directory: {root}"
        )

    print("=" * 60)
    print("SCANNING REPOSITORY")
    print(f"Root: {root}")
    print("=" * 60)

    files = []
    total_files = 0
    supported_files = 0

    for path in root.rglob("*"):

        # Skip excluded directories
        if any(
            part.lower() in {
                directory.lower()
                for directory in EXCLUDED_DIRECTORIES
            }
            for part in path.parts
        ):
            continue

        try:
            if not path.is_file():
                continue

            total_files += 1

            if not is_supported_file(path):
                continue

            supported_files += 1

            stat = path.stat()

            file_hash = calculate_file_hash(
                str(path)
            )

            file_data = {
                "file_name": path.name,
                "file_path": str(path),
                "file_type": get_file_type(path),
                "category": get_file_category(path),
                "modified_at": datetime.fromtimestamp(
                    stat.st_mtime
                ),
                "file_hash": file_hash,
            }

            files.append(file_data)

            print(
                f"[{supported_files}] "
                f"{file_data['category']:15} "
                f"{path.name}"
            )

        except (
            PermissionError,
            OSError,
        ) as error:

            print(
                f"Skipped: {path} -> {error}"
            )

    print("=" * 60)
    print(f"Total files scanned: {total_files}")
    print(f"Supported files:     {supported_files}")
    print("=" * 60)

    return files