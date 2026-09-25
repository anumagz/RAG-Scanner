import os
from collections.abc import Iterator

from utils.ollama_client import (
    CHAT_MODEL,
    generate,
    stream_generate,
)


SYSTEM_PROMPT = """
You are an AI assistant for a local repository
analysis system.

Answer questions using ONLY the repository
context provided to you.

Rules:

1. Do not invent facts.
2. Do not invent files.
3. Do not invent line numbers.
4. Do not invent pages.
5. Do not invent slides.
6. Do not invent Excel sheet names.
7. If the context does not contain enough
   information, clearly say so.
8. Explain technical concepts clearly.
9. Prefer concise but useful answers.
10. Source references will be generated separately
    by the application.
"""


CHAT_NUM_PREDICT = int(
    os.getenv(
        "OLLAMA_CHAT_NUM_PREDICT",
        "384",
    )
)


def _build_prompt(
    question: str,
    context: str,
) -> str:

    return f"""
Repository Context:

{context}

User Question:

{question}

Answer the question based only on the
repository context above.
"""


def generate_answer(
    question: str,
    context: str,
) -> str:

    return generate(
        prompt=_build_prompt(
            question=question,
            context=context,
        ),
        model=CHAT_MODEL,
        system=SYSTEM_PROMPT,
        temperature=0.1,
        num_predict=CHAT_NUM_PREDICT,
    )


def stream_answer(
    question: str,
    context: str,
) -> Iterator[str]:

    yield from stream_generate(
        prompt=_build_prompt(
            question=question,
            context=context,
        ),
        model=CHAT_MODEL,
        system=SYSTEM_PROMPT,
        temperature=0.1,
        num_predict=CHAT_NUM_PREDICT,
    )
