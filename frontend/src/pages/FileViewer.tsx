import { useParams, Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import {
  ArrowLeft,
  FileCode2,
  FileText,
  Search,
  MessageSquare,
  Code2,
  BookOpen,
  Loader2,
  ShieldAlert,
} from "lucide-react";

import {
  getFile,
  getFileSummary,
} from "../services/api";

function FileViewer() {
  const { id } = useParams();

  const fileId = Number(id);

  const {
    data: file,
    isLoading: fileLoading,
  } = useQuery({
    queryKey: ["file", fileId],
    queryFn: () => getFile(fileId),
    enabled: !Number.isNaN(fileId),
  });

  const {
    data: summaryData,
    isLoading: summaryLoading,
  } = useQuery({
    queryKey: ["file-summary", fileId],
    queryFn: () => getFileSummary(fileId),
    enabled: !Number.isNaN(fileId),
  });

  if (fileLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-950 text-white">
        <Loader2
          size={22}
          className="animate-spin text-blue-400"
        />
      </div>
    );
  }

  if (!file) {
    return (
      <div className="min-h-screen bg-slate-950 p-8 text-white">
        File not found.
      </div>
    );
  }

  const fileName = file.file_name;

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      {/* Header */}
      <header className="border-b border-slate-800 bg-slate-900 px-8 py-4">
        <div className="flex items-center justify-between">
          <div>
            <Link
              to={`/repositories/${file.repository_id}`}
              className="mb-2 flex items-center gap-2 text-sm text-slate-500 hover:text-white"
            >
              <ArrowLeft size={15} />
              Repository
            </Link>

            <div className="flex items-center gap-3">
              <FileCode2
                size={23}
                className="text-blue-400"
              />

              <div>
                <h1 className="font-semibold">
                  {fileName}
                </h1>

                <p className="text-xs text-slate-500">
                  {file.file_path}
                </p>
              </div>
            </div>
          </div>

          <div className="flex gap-2">
            <Link
              to={`/files/${file.id}/review`}
              className="flex items-center gap-2 rounded-lg border border-purple-500/30 px-4 py-2 text-sm text-purple-400 hover:bg-purple-500/10"
            >
              <ShieldAlert size={15} />
              Review Code
            </Link>

            <button className="flex items-center gap-2 rounded-lg border border-slate-700 px-4 py-2 text-sm hover:bg-slate-800">
              <Search size={15} />
              Search
            </button>

            <button className="flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm hover:bg-blue-500">
              <MessageSquare size={15} />
              Explain
            </button>
          </div>
        </div>
      </header>

      <main className="grid grid-cols-12 gap-6 p-8">
        {/* Source code */}
        <section className="col-span-8 overflow-hidden rounded-xl border border-slate-800 bg-slate-900">
          <div className="flex items-center justify-between border-b border-slate-800 px-5 py-3">
            <div className="flex items-center gap-2">
              <Code2
                size={17}
                className="text-blue-400"
              />

              <span className="text-sm font-medium">
                File Content
              </span>
            </div>

            <span className="text-xs text-slate-600">
              {file.file_type}
            </span>
          </div>

          <div className="max-h-[700px] overflow-auto bg-slate-950 p-5">
            {file.content ? (
              <pre className="text-sm leading-7">
                {file.content
                  .split("\n")
                  .map((line, index) => (
                    <div
                      key={index}
                      className="flex"
                    >
                      <span className="mr-6 w-10 shrink-0 select-none text-right text-slate-700">
                        {index + 1}
                      </span>

                      <code className="whitespace-pre text-slate-300">
                        {line}
                      </code>
                    </div>
                  ))}
              </pre>
            ) : (
              <div className="py-16 text-center">
                <FileText
                  size={35}
                  className="mx-auto text-slate-700"
                />

                <p className="mt-4 text-sm text-slate-500">
                  File content will be displayed here.
                </p>
              </div>
            )}
          </div>
        </section>

        {/* Summary */}
        <aside className="col-span-4 space-y-6">
          <div className="rounded-xl border border-slate-800 bg-slate-900 p-5">
            <div className="flex items-center gap-2">
              <BookOpen
                size={18}
                className="text-blue-400"
              />

              <h2 className="font-semibold">
                AI Summary
              </h2>
            </div>

            <div className="mt-5 text-sm leading-7 text-slate-400">
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
                  AI summary will appear here after the
                  backend processes this file.
                </p>
              )}
            </div>
          </div>

          {/* File information */}
          <div className="rounded-xl border border-slate-800 bg-slate-900 p-5">
            <h2 className="font-semibold">
              File Information
            </h2>

            <div className="mt-5 space-y-4 text-sm">
              <div>
                <p className="text-xs text-slate-600">
                  File Name
                </p>

                <p className="mt-1 break-all text-slate-300">
                  {file.file_name}
                </p>
              </div>

              <div>
                <p className="text-xs text-slate-600">
                  Type
                </p>

                <p className="mt-1 text-slate-300">
                  {file.file_type}
                </p>
              </div>

              <div>
                <p className="text-xs text-slate-600">
                  Category
                </p>

                <p className="mt-1 text-slate-300">
                  {file.category || "Unknown"}
                </p>
              </div>

              <div>
                <p className="text-xs text-slate-600">
                  Modified
                </p>

                <p className="mt-1 text-slate-300">
                  {file.modified_at || "Unknown"}
                </p>
              </div>
            </div>
          </div>
        </aside>
      </main>
    </div>
  );
}

export default FileViewer;