const API_BASE_URL =
  import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

export interface ChatSource {
  file?: string | null;
  file_id?: number | null;
  start_line?: number | null;
  end_line?: number | null;
  page?: number | null;
  slide?: number | null;
  sheet?: string | null;
}

export interface ChatResponse {
  answer: string;
  sources: ChatSource[];
}

export async function askRepository(
  repositoryId: number,
  question: string
): Promise<ChatResponse> {
  const response = await fetch(`${API_BASE_URL}/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      repository_id: repositoryId,
      question,
    }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => null);

    throw new Error(
      error?.detail || `Chat request failed (${response.status})`
    );
  }

  return response.json();
}