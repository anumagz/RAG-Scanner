from utils.ollama_client import generate


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


def generate_answer(
    question: str,
    context: str,
) -> str:

    prompt = f"""
Repository Context:

{context}

User Question:

{question}

Answer the question based only on the
repository context above.
"""

    return generate(
        prompt=prompt,
        model="qwen2.5:3b",
        system=SYSTEM_PROMPT,
        temperature=0.1,
    )