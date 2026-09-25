from dataclasses import dataclass, field
from typing import Any


@dataclass
class ParsedDocument:
    text: str
    metadata: dict[str, Any] = field(
        default_factory=dict
    )


class BaseParser:

    def parse(
        self,
        file_path: str,
        file_id: int | None = None,
    ) -> list[ParsedDocument]:

        raise NotImplementedError