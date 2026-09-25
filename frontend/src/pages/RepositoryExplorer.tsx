import { useParams, Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import {
  ArrowLeft,
  Folder,
  FileCode2,
  FileText,
  FileSpreadsheet,
  FileType2,
  Settings,
  Database,
  MessageSquare,
  RefreshCw,
  CheckCircle2,
  Loader2,
  AlertCircle,
} from "lucide-react";

import {
  getRepository,
  getRepositoryFiles,
  getRepositorySummary,
} from "../services/api";

function getFileIcon(fileType: string) {
  const type = fileType.toLowerCase();

  if (
    [".py", ".js", ".ts", ".java", ".cs", ".sql"].some(
      (extension) => type.includes(extension)
    )
  ) {
    return FileCode2;
  }

  if (type.includes("xlsx") || type.includes("csv")) {
    return FileSpreadsheet;
  }

  if (type.includes("pdf")) {
    return FileType2;
  }

  if (
    type.includes("json") ||
    type.includes("xml") ||
    type.includes("yaml")
  ) {
    return Settings;
  }

  return FileText;
}

function RepositoryExplorer() {
  const { id } = useParams();

  const repositoryId = Number(id);

  const {
    data: repository,
    isLoading: repositoryLoading,
  } = useQuery({
    queryKey: ["repository", repositoryId],
    queryFn: () => getRepository(repositoryId),
    enabled: !Number.isNaN(repositoryId),
  });

  const {
    data: files = [],
    isLoading: filesLoading,
  } = useQuery({
    queryKey: ["repository-files", repositoryId],
    queryFn: () => getRepositoryFiles(repositoryId),
    enabled: !Number.isNaN(repositoryId),
  });

  const {
    data: summaryData,
    isLoading: summaryLoading,
  } = useQuery({
    queryKey: ["repository-summary", repositoryId],
    queryFn: () =>
      getRepositorySummary(repositoryId),
    enabled: !Number.isNaN(repositoryId),
  });

  if (repositoryLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-950 text-white">
        <div className="flex items-center gap-3 text-slate-400">
          <Loader2
            size={20}
            className="animate-spin"
          />
          Loading repository...
        </div>
      </div>
    );
  }

  if (!repository) {
    return (
      <div className="min-h-screen bg-slate-950 p-8 text-white">
        <p className="text-red-400">
          Repository not found.
        </p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      {/* Header */}
      <header className="border-b border-slate-800 bg-slate-900 px-8 py-5">
        <div className="flex items-center justify-between">
          <div>
            <Link
              to="/"
              className="mb-3 flex items-center gap-2 text-sm text-slate-500 hover:text-white"
            >
              <ArrowLeft size={16} />
              Dashboard
            </Link>

            <div className="flex items-center gap-3">
              <Folder
                size={27}
                className="text-blue-400"
              />

              <div>
                <h1 className="text-2xl font-semibold">
                  {repository.name}
                </h1>

                <p className="mt-1 max-w-2xl break-all text-xs text-slate-500">
                  {repository.path}
                </p>
              </div>
            </div>
          </div>

          <div className="flex gap-3">
            <button className="flex items-center gap-2 rounded-lg border border-slate-700 px-4 py-2 text-sm hover:bg-slate-800">
              <RefreshCw size={15} />
              Rescan
            </button>

            <Link
              to={`/repositories/${repository.id}/chat`}
              className="flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium hover:bg-blue-500"
            >
              <MessageSquare size={16} />
              Ask Repository
            </Link>
          </div>
        </div>
      </header>

      <main className="grid grid-cols-12 gap-6 p-8">
        {/* Repository tree */}
        <aside className="col-span-3 rounded-xl border border-slate-800 bg-slate-900">
          <div className="border-b border-slate-800 p-5">
            <h2 className="font-semibold">
              Repository Files
            </h2>

            <p className="mt-1 text-xs text-slate-500">
              {files.length} indexed files
            </p>
          </div>

          <div className="max-h-[650px] overflow-y-auto p-3">
            {files.length === 0 ? (
              <p className="p-3 text-sm text-slate-500">
                No files indexed yet.
              </p>
            ) : (
              files.map((file) => {
                const Icon = getFileIcon(
                  file.file_type
                );

                return (
                  <Link
                    key={file.id}
                    to={`/files/${file.id}`}
                    className="flex items-center gap-2 rounded-lg px-3 py-2 text-sm text-slate-400 hover:bg-slate-800 hover:text-white"
                  >
                    <Icon
                      size={15}
                      className="shrink-0 text-blue-400"
                    />

                    <span className="truncate">
                      {file.file_name}
                    </span>
                  </Link>
                );
              })
            )}
          </div>
        </aside>

        {/* Main */}
        <section className="col-span-9 space-y-6">
          {/* Status */}
          <div className="flex items-center justify-between rounded-xl border border-emerald-500/20 bg-emerald-500/5 p-5">
            <div className="flex items-center gap-3">
              <CheckCircle2
                size={20}
                className="text-emerald-400"
              />

              <div>
                <p className="text-sm font-medium">
                  Repository indexed
                </p>

                <p className="text-xs text-slate-500">
                  Files are available for AI search and
                  analysis.
                </p>
              </div>
            </div>

            <span className="text-sm text-emerald-400">
              {files.length} files
            </span>
          </div>

          {/* Summary */}
          <div className="rounded-xl border border-slate-800 bg-slate-900 p-6">
            <h2 className="text-lg font-semibold">
              Repository Summary
            </h2>

            <p className="mt-1 text-sm text-slate-500">
              AI-generated understanding of this repository.
            </p>

            <div className="mt-5 leading-7 text-sm text-slate-400">
              {summaryLoading ? (
                <div className="flex items-center gap-2">
                  <Loader2
                    size={16}
                    className="animate-spin"
                  />
                  Generating summary...
                </div>
              ) : summaryData?.summary ? (
                <p className="whitespace-pre-wrap">
                  {summaryData.summary}
                </p>
              ) : (
                <p>
                  Repository summary will appear here once
                  the backend generates it using Ollama.
                </p>
              )}
            </div>
          </div>

          {/* File list */}
          <div className="rounded-xl border border-slate-800 bg-slate-900">
            <div className="border-b border-slate-800 p-5">
              <h2 className="font-semibold">
                Indexed Files
              </h2>

              <p className="mt-1 text-sm text-slate-500">
                Open a file to view its contents and AI
                summary.
              </p>
            </div>

            {filesLoading ? (
              <div className="p-10 text-center text-slate-500">
                <Loader2
                  size={20}
                  className="mx-auto animate-spin"
                />
              </div>
            ) : files.length === 0 ? (
              <div className="p-10 text-center">
                <AlertCircle
                  size={30}
                  className="mx-auto text-slate-700"
                />

                <p className="mt-3 text-sm text-slate-500">
                  No indexed files found.
                </p>
              </div>
            ) : (
              <div className="divide-y divide-slate-800">
                {files.map((file) => {
                  const Icon = getFileIcon(
                    file.file_type
                  );

                  return (
                    <Link
                      key={file.id}
                      to={`/files/${file.id}`}
                      className="flex items-center justify-between p-4 hover:bg-slate-800/40"
                    >
                      <div className="flex items-center gap-3">
                        <Icon
                          size={19}
                          className="text-blue-400"
                        />

                        <div>
                          <p className="text-sm font-medium">
                            {file.file_name}
                          </p>

                          <p className="mt-1 text-xs text-slate-600">
                            {file.file_path}
                          </p>
                        </div>
                      </div>

                      <span className="rounded-md bg-slate-800 px-2 py-1 text-xs text-slate-500">
                        {file.category ||
                          file.file_type}
                      </span>
                    </Link>
                  );
                })}
              </div>
            )}
          </div>
        </section>
      </main>
    </div>
  );
}

export default RepositoryExplorer;