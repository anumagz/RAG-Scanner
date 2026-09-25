import json
import re

from sqlalchemy.orm import Session

from models.file import File
from utils.ollama_client import generate, CODE_MODEL


def _extract_json(text: str) -> dict:
    """Extract JSON from an Ollama response."""

    text = text.strip()

    # Remove Markdown JSON code fences
    text = re.sub(
        r"^```json\s*",
        "",
        text,
        flags=re.IGNORECASE,
    )

    text = re.sub(
        r"^```\s*",
        "",
        text,
    )

    text = re.sub(
        r"\s*```$",
        "",
        text,
    )

    # Try parsing the complete response
    try:
        result = json.loads(text)

        if isinstance(result, dict):
            return result

    except json.JSONDecodeError:
        pass

    # Try extracting JSON object from surrounding text
    start = text.find("{")
    end = text.rfind("}")

    if start != -1 and end != -1 and end > start:

        json_text = text[start:end + 1]

        try:
            result = json.loads(json_text)

            if isinstance(result, dict):
                return result

        except json.JSONDecodeError:
            pass

    raise ValueError(
        "AI returned an invalid JSON review."
    )


def review_code(
    db: Session,
    file_id: int,
):
    """Review a code file using Ollama."""

    # ---------------------------------------------------------
    # FIND FILE
    # ---------------------------------------------------------

    file = (
        db.query(File)
        .filter(File.id == file_id)
        .first()
    )

    if not file:
        raise ValueError(
            "File not found."
        )

    # ---------------------------------------------------------
    # VALIDATE FILE TYPE
    # ---------------------------------------------------------

    if file.category != "Code":
        raise ValueError(
            "Selected file is not a code file."
        )

    # ---------------------------------------------------------
    # READ SOURCE CODE
    # ---------------------------------------------------------

    try:
        with open(
            file.file_path,
            "r",
            encoding="utf-8",
            errors="ignore",
        ) as source_file:

            code = source_file.read()

    except OSError as error:

        raise ValueError(
            f"Unable to read file: {error}"
        )

    # ---------------------------------------------------------
    # CHECK EMPTY FILE
    # ---------------------------------------------------------

    if not code.strip():

        raise ValueError(
            "The code file is empty."
        )

    # ---------------------------------------------------------
    # LIMIT CODE SIZE
    # ---------------------------------------------------------

    if len(code) > 50000:

        code = code[:50000]

    # ---------------------------------------------------------
    # CREATE AI PROMPT
    # ---------------------------------------------------------

    prompt = f"""
Review the following source code carefully.

File Name: {file.file_name}
File Path: {file.file_path}

Identify potential:

- Bugs
- Logic errors
- Security issues
- Performance problems
- Error handling problems
- Maintainability issues
- Code quality problems
- Potential edge cases

Return ONLY valid JSON.

Use exactly this structure:

{{
    "issues": [
        {{
            "severity": "High",
            "issue": "Short description of the issue",
            "line": 10,
            "explanation": "Detailed explanation",
            "suggested_fix": "Practical suggested fix"
        }}
    ]
}}

Severity must be one of:

High
Medium
Low

If you cannot identify any meaningful issue, return:

{{
    "issues": []
}}

Rules:

- Do not invent issues.
- Only identify issues supported by the provided source code.
- Use the closest relevant line number when possible.
- If a line number cannot be determined, use null.
- Keep explanations practical.
- Do not include Markdown.
- Do not include text outside the JSON object.

SOURCE CODE:

```text
{code}
"""
    # ---------------------------------------------------------
    # CALL OLLAMA
    # ---------------------------------------------------------

    try:

        raw_review = generate(
            prompt=prompt,
            model=CODE_MODEL,
            temperature=0.1,
        )

    except Exception as error:

        raise RuntimeError(
            f"Failed to generate code review: {error}"
        )

    # ---------------------------------------------------------
    # PARSE AI RESPONSE
    # ---------------------------------------------------------

    try:

        parsed = _extract_json(
            raw_review
        )

    except ValueError:

        return {
            "file_id": file.id,
            "issues": [],
            "raw_review": raw_review,
        }

    # ---------------------------------------------------------
    # GET ISSUES
    # ---------------------------------------------------------

    issues = parsed.get(
        "issues",
        []
    )

    if not isinstance(
        issues,
        list
    ):

        issues = []

    cleaned_issues = []

    # ---------------------------------------------------------
    # CLEAN EACH ISSUE
    # ---------------------------------------------------------

    for issue in issues:

        if not isinstance(
            issue,
            dict
        ):
            continue

        severity = issue.get(
            "severity",
            "Low"
        )

        if severity not in {
            "High",
            "Medium",
            "Low",
        }:

            severity = "Low"

        line = issue.get(
            "line"
        )

        if not isinstance(
            line,
            int
        ):

            line = None

        cleaned_issues.append(
            {
                "severity": severity,

                "issue": str(
                    issue.get(
                        "issue",
                        "Unspecified issue"
                    )
                ),

                "line": line,

                "explanation": str(
                    issue.get(
                        "explanation",
                        ""
                    )
                ),

                "suggested_fix": (
                    str(
                        issue.get(
                            "suggested_fix"
                        )
                    )
                    if issue.get(
                        "suggested_fix"
                    ) is not None
                    else None
                ),
            }
        )

    # ---------------------------------------------------------
    # RETURN RESPONSE
    # ---------------------------------------------------------

    return {
        "file_id": file.id,
        "issues": cleaned_issues,
        "raw_review": raw_review,
    }
    