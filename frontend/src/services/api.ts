import type {
  Repository,
  RepositoryFile,
  FileDetails,
  ChatResponse,
  ReviewIssue,
} from "../types";

const API_BASE_URL =
  import.meta.env.VITE_API_URL ||
  "http://localhost:8000";


async function request<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {

  const response = await fetch(
    `${API_BASE_URL}${endpoint}`,
    {
      headers: {
        "Content-Type":
          "application/json",

        ...(options?.headers || {}),
      },

      ...options,
    }
  );


  if (!response.ok) {

    let message =
      `Request failed: ${response.status}`;

    try {

      const errorData =
        await response.json();

      if (errorData?.detail) {
        message = errorData.detail;
      }

    } catch {

      try {
        const text =
          await response.text();

        if (text) {
          message = text;
        }
      } catch {
        // Ignore response parsing errors
      }
    }


    throw new Error(message);
  }


  return response.json();
}


/* ----------------------------------
   REPOSITORIES
---------------------------------- */

export async function getRepositories(): Promise<
  Repository[]
> {

  return request<Repository[]>(
    "/repositories"
  );
}


export async function getRepository(
  id: number
): Promise<Repository> {

  return request<Repository>(
    `/repositories/${id}`
  );
}


export async function addRepository(
  path: string
): Promise<Repository> {

  return request<Repository>(
    "/repositories",
    {
      method: "POST",

      body: JSON.stringify({
        path,
      }),
    }
  );
}


export async function deleteRepository(
  id: number
): Promise<void> {

  await request(
    `/repositories/${id}`,
    {
      method: "DELETE",
    }
  );
}


export async function rescanRepository(
  id: number
): Promise<Repository> {

  return request<Repository>(
    `/repositories/${id}/rescan`,
    {
      method: "POST",
    }
  );
}


/* ----------------------------------
   FILES
---------------------------------- */

export async function getRepositoryFiles(
  repositoryId: number
): Promise<RepositoryFile[]> {

  return request<RepositoryFile[]>(
    `/repositories/${repositoryId}/files`
  );
}


export async function getFile(
  fileId: number
): Promise<FileDetails> {

  return request<FileDetails>(
    `/files/${fileId}`
  );
}


/* ----------------------------------
   SUMMARIES
---------------------------------- */

export async function getRepositorySummary(
  repositoryId: number
): Promise<{ summary: string }> {

  return request<{ summary: string }>(
    `/repositories/${repositoryId}/summary`
  );
}


export async function getFileSummary(
  fileId: number
): Promise<{ summary: string }> {

  return request<{ summary: string }>(
    `/files/${fileId}/summary`
  );
}


/* ----------------------------------
   CHAT / RAG
---------------------------------- */

export async function chatWithRepository(
  repositoryId: number,
  question: string
): Promise<ChatResponse> {

  return request<ChatResponse>(
    "/chat",
    {
      method: "POST",

      body: JSON.stringify({
        repository_id:
          repositoryId,

        question:
          question,
      }),
    }
  );
}


/* ----------------------------------
   CODE EXPLANATION
---------------------------------- */

export async function explainFile(
  fileId: number
): Promise<{ explanation: string }> {

  return request<{ explanation: string }>(
    "/explain",
    {
      method: "POST",

      body: JSON.stringify({
        file_id: fileId,
      }),
    }
  );
}


/* ----------------------------------
   CODE REVIEW
---------------------------------- */

export async function reviewFile(
  fileId: number
): Promise<ReviewIssue[]> {

  return request<ReviewIssue[]>(
    "/review",
    {
      method: "POST",

      body: JSON.stringify({
        file_id: fileId,
      }),
    }
  );
}