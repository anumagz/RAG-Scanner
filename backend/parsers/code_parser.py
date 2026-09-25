import ast
import re
from pathlib import Path

from parsers.base import BaseParser, ParsedDocument


SUPPORTED_CODE = {
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


class CodeParser(BaseParser):

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

        if path.suffix.lower() == ".py":
            return self._parse_python(
                text,
                path,
                file_id,
            )

        return self._parse_generic_code(
            text,
            path,
            file_id,
        )

    def _parse_python(
        self,
        text: str,
        path: Path,
        file_id: int | None,
    ):

        lines = text.splitlines()
        documents = []

        try:
            tree = ast.parse(text)
        except SyntaxError:

            return [
                ParsedDocument(
                    text=text,
                    metadata={
                        "file": path.name,
                        "file_path": str(path),
                        "file_id": file_id,
                        "start_line": 1,
                        "end_line": len(lines),
                        "type": "code",
                    },
                )
            ]

        nodes = []

        for node in ast.walk(tree):

            if isinstance(
                node,
                (
                    ast.FunctionDef,
                    ast.AsyncFunctionDef,
                    ast.ClassDef,
                ),
            ):
                nodes.append(node)

        nodes.sort(
            key=lambda node: (
                getattr(node, "lineno", 0)
            )
        )

        for node in nodes:

            start = node.lineno
            end = getattr(
                node,
                "end_lineno",
                start,
            )

            chunk = "\n".join(
                lines[start - 1:end]
            )

            node_type = (
                "class"
                if isinstance(node, ast.ClassDef)
                else "function"
            )

            name = getattr(
                node,
                "name",
                "unknown",
            )

            documents.append(
                ParsedDocument(
                    text=chunk,
                    metadata={
                        "file": path.name,
                        "file_path": str(path),
                        "file_id": file_id,
                        "start_line": start,
                        "end_line": end,
                        "type": "code",
                        "code_element": node_type,
                        "name": name,
                    },
                )
            )

        if not documents:

            documents.append(
                ParsedDocument(
                    text=text,
                    metadata={
                        "file": path.name,
                        "file_path": str(path),
                        "file_id": file_id,
                        "start_line": 1,
                        "end_line": len(lines),
                        "type": "code",
                    },
                )
            )

        return documents

    def _parse_generic_code(
        self,
        text: str,
        path: Path,
        file_id: int | None,
    ):

        lines = text.splitlines()

        pattern = re.compile(
            r"""
            (?:
                function\s+([A-Za-z0-9_$]+)
                |
                (?:public|private|protected|static|\s)+
                [A-Za-z0-9_<>\[\]]+\s+
                ([A-Za-z0-9_$]+)\s*\(
            )
            """,
            re.VERBOSE,
        )

        matches = list(
            pattern.finditer(text)
        )

        if not matches:

            return [
                ParsedDocument(
                    text=text,
                    metadata={
                        "file": path.name,
                        "file_path": str(path),
                        "file_id": file_id,
                        "start_line": 1,
                        "end_line": len(lines),
                        "type": "code",
                    },
                )
            ]

        documents = []

        for index, match in enumerate(matches):

            name = (
                match.group(1)
                or match.group(2)
                or "function"
            )

            start_char = match.start()

            start_line = (
                text[:start_char].count("\n")
                + 1
            )

            if index + 1 < len(matches):

                end_char = matches[
                    index + 1
                ].start()

            else:

                end_char = len(text)

            chunk = text[
                start_char:end_char
            ].strip()

            end_line = (
                start_line
                + chunk.count("\n")
            )

            documents.append(
                ParsedDocument(
                    text=chunk,
                    metadata={
                        "file": path.name,
                        "file_path": str(path),
                        "file_id": file_id,
                        "start_line": start_line,
                        "end_line": end_line,
                        "type": "code",
                        "code_element": "function",
                        "name": name,
                    },
                )
            )

        return documents