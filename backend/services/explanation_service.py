from sqlalchemy.orm import Session

from models.file import File
from utils.ollama_client import generate, CODE_MODEL


def generate_code_explanation(db: Session, file_id: int):
    """
    Generate an AI explanation for a code file using Ollama.
    """

    # Find the file in the database
    file = db.query(File).filter(File.id == file_id).first()

    if not file:
        raise ValueError("File not found.")

    # Only allow code files
    if file.category != "Code":
        raise ValueError("Selected file is not a code file.")

    # Read the source code
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

    # Check if the file is empty
    if not code.strip():
        raise ValueError("The code file is empty.")

    # Prevent sending extremely large files to the model
    if len(code) > 50000:
        code = code[:50000]

    # AI prompt
    prompt = f"""
Analyze the following source code.

File Name: {file.file_name}
File Path: {file.file_path}

Provide a clear and practical explanation using the following sections:

1. Purpose
Explain what this file does and why it exists.

2. Classes
List the important classes and explain the responsibility of each class.

3. Functions / Methods
List the important functions or methods and explain what each one does.

4. Dependencies
Identify important libraries, modules, packages, or other files that this code depends on.

5. Important Variables
Explain important variables, constants, configuration values, or data structures.

6. Key Logic
Explain the important processing and business logic implemented in the code.

7. Execution Flow
Explain how the code executes from beginning to end.

8. Edge Cases
Mention important edge cases, possible errors, exceptions, or limitations.

9. Improvement Suggestions
Mention practical improvements that could make the code cleaner, safer, faster, or easier to maintain.

Keep the explanation easy to understand.
Do not invent functionality that is not present in the source code.
Base the explanation only on the provided source code.

  SOURCE CODE:

    ```text
    {code}
    ```
    """
