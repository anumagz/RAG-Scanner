export interface Repository {
  id: number;
  name: string;
  path: string;
  status: string;
  created_at?: string;
  file_count?: number;
}

export interface RepositoryFile {
  id: number;
  repository_id: number;
  file_name: string;
  file_path: string;
  file_type: string;
  category?: string;
  modified_at?: string;
}

export interface FileDetails extends RepositoryFile {
  content?: string;
  summary?: string;
}

export interface SourceCitation {
  file: string;
  location: string;
  type: "code" | "pdf" | "pptx" | "xlsx" | "document" | "text";
}

export interface ChatResponse {
  answer: string;
  sources: SourceCitation[];
}

export interface ReviewIssue {
  issue: string;
  severity: "High" | "Medium" | "Low";
  file: string;
  lines: string;
  explanation: string;
  suggested_fix: string;
}