import { useParams, Link } from "react-router-dom";
import { useMutation } from "@tanstack/react-query";
import {
  ArrowLeft,
  ShieldAlert,
  AlertTriangle,
  Info,
  CheckCircle2,
  FileCode2,
  Loader2,
  RefreshCw,
} from "lucide-react";

import { reviewFile } from "../services/api";

function CodeReview() {
  const { id } = useParams();

  const fileId = Number(id);

  const reviewMutation = useMutation({
    mutationFn: () => reviewFile(fileId),
  });

  const issues = reviewMutation.data || [];

  const highCount = issues.filter(
    (issue) => issue.severity === "High"
  ).length;

  const mediumCount = issues.filter(
    (issue) => issue.severity === "Medium"
  ).length;

  const lowCount = issues.filter(
    (issue) => issue.severity === "Low"
  ).length;

  const getSeverityIcon = (
    severity: string
  ) => {
    if (severity === "High") {
      return ShieldAlert;
    }

    if (severity === "Medium") {
      return AlertTriangle;
    }

    return Info;
  };

  const getSeverityStyle = (
    severity: string
  ) => {
    if (severity === "High") {
      return "text-red-400 bg-red-500/10 border-red-500/20";
    }

    if (severity === "Medium") {
      return "text-yellow-400 bg-yellow-500/10 border-yellow-500/20";
    }

    return "text-blue-400 bg-blue-500/10 border-blue-500/20";
  };

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      {/* Header */}
      <header className="border-b border-slate-800 bg-slate-900 px-8 py-5">
        <div className="flex items-center justify-between">
          <div>
            <Link
              to={`/files/${id}`}
              className="mb-2 flex items-center gap-2 text-sm text-slate-500 hover:text-white"
            >
              <ArrowLeft size={15} />
              Back to File
            </Link>

            <div className="flex items-center gap-3">
              <ShieldAlert
                size={26}
                className="text-purple-400"
              />

              <div>
                <h1 className="text-xl font-semibold">
                  AI Code Review
                </h1>

                <p className="text-sm text-slate-500">
                  Find bugs, security issues and code smells
                </p>
              </div>
            </div>
          </div>

          <button
            onClick={() =>
              reviewMutation.mutate()
            }
            disabled={
              reviewMutation.isPending ||
              Number.isNaN(fileId)
            }
            className="flex items-center gap-2 rounded-lg bg-purple-600 px-4 py-2 text-sm font-medium hover:bg-purple-500 disabled:opacity-50"
          >
            {reviewMutation.isPending ? (
              <Loader2
                size={16}
                className="animate-spin"
              />
            ) : (
              <RefreshCw size={16} />
            )}

            Run Review
          </button>
        </div>
      </header>

      <main className="p-8">
        {/* Summary */}
        <div className="mb-6 grid gap-4 md:grid-cols-4">
          <div className="rounded-xl border border-slate-800 bg-slate-900 p-5">
            <p className="text-xs text-slate-500">
              Total Issues
            </p>

            <p className="mt-2 text-3xl font-bold">
              {issues.length}
            </p>
          </div>

          <div className="rounded-xl border border-red-500/20 bg-slate-900 p-5">
            <p className="text-xs text-slate-500">
              High
            </p>

            <p className="mt-2 text-3xl font-bold text-red-400">
              {highCount}
            </p>
          </div>

          <div className="rounded-xl border border-yellow-500/20 bg-slate-900 p-5">
            <p className="text-xs text-slate-500">
              Medium
            </p>

            <p className="mt-2 text-3xl font-bold text-yellow-400">
              {mediumCount}
            </p>
          </div>

          <div className="rounded-xl border border-blue-500/20 bg-slate-900 p-5">
            <p className="text-xs text-slate-500">
              Low
            </p>

            <p className="mt-2 text-3xl font-bold text-blue-400">
              {lowCount}
            </p>
          </div>
        </div>

        {/* Error */}
        {reviewMutation.isError && (
          <div className="mb-6 rounded-xl border border-red-500/20 bg-red-500/5 p-5">
            <p className="text-sm text-red-400">
              Failed to run code review. Make sure the
              FastAPI backend and Ollama are running.
            </p>
          </div>
        )}

        {/* Initial state */}
        {!reviewMutation.data &&
          !reviewMutation.isPending && (
            <div className="rounded-xl border border-dashed border-slate-700 bg-slate-900/50 p-16 text-center">
              <ShieldAlert
                size={45}
                className="mx-auto text-slate-700"
              />

              <h2 className="mt-5 text-lg font-semibold">
                Ready for Code Review
              </h2>

              <p className="mx-auto mt-2 max-w-md text-sm text-slate-500">
                Run the local AI code reviewer to identify
                potential bugs, security issues, performance
                problems and code smells.
              </p>

              <button
                onClick={() =>
                  reviewMutation.mutate()
                }
                className="mt-6 rounded-lg bg-purple-600 px-5 py-2.5 text-sm font-medium hover:bg-purple-500"
              >
                Start Review
              </button>
            </div>
          )}

        {/* Loading */}
        {reviewMutation.isPending && (
          <div className="flex items-center justify-center rounded-xl border border-slate-800 bg-slate-900 py-20">
            <div className="text-center">
              <Loader2
                size={28}
                className="mx-auto animate-spin text-purple-400"
              />

              <p className="mt-4 text-sm text-slate-400">
                Deepseek-Coder is reviewing the file...
              </p>
            </div>
          </div>
        )}

        {/* Results */}
        {!reviewMutation.isPending &&
          reviewMutation.data && (
            <div className="rounded-xl border border-slate-800 bg-slate-900">
              <div className="border-b border-slate-800 p-5">
                <h2 className="font-semibold">
                  Review Findings
                </h2>

                <p className="mt-1 text-sm text-slate-500">
                  Potential issues identified by the local
                  AI code reviewer.
                </p>
              </div>

              {issues.length === 0 ? (
                <div className="p-12 text-center">
                  <CheckCircle2
                    size={35}
                    className="mx-auto text-emerald-400"
                  />

                  <h3 className="mt-4 font-semibold">
                    No issues found
                  </h3>

                  <p className="mt-2 text-sm text-slate-500">
                    The AI reviewer did not identify any
                    potential issues.
                  </p>
                </div>
              ) : (
                <div className="divide-y divide-slate-800">
                  {issues.map((issue, index) => {
                    const Icon =
                      getSeverityIcon(
                        issue.severity
                      );

                    const style =
                      getSeverityStyle(
                        issue.severity
                      );

                    return (
                      <div
                        key={index}
                        className="p-6"
                      >
                        <div className="flex items-start gap-4">
                          <div
                            className={`rounded-lg border p-2 ${style}`}
                          >
                            <Icon size={20} />
                          </div>

                          <div className="flex-1">
                            <div className="flex flex-wrap items-center gap-3">
                              <h3 className="font-medium">
                                {issue.issue}
                              </h3>

                              <span
                                className={`rounded-full border px-2 py-1 text-xs ${style}`}
                              >
                                {issue.severity}
                              </span>
                            </div>

                            <div className="mt-3 flex flex-wrap items-center gap-4 text-xs text-slate-500">
                              <span className="flex items-center gap-1">
                                <FileCode2
                                  size={13}
                                />
                                {issue.file}
                              </span>

                              <span>
                                Lines {issue.lines}
                              </span>
                            </div>

                            <div className="mt-4">
                              <p className="text-xs font-medium text-slate-600">
                                Explanation
                              </p>

                              <p className="mt-2 text-sm leading-6 text-slate-400">
                                {issue.explanation}
                              </p>
                            </div>

                            <div className="mt-4 rounded-lg border border-slate-800 bg-slate-950 p-4">
                              <p className="text-xs font-medium text-slate-600">
                                Suggested Fix
                              </p>

                              <p className="mt-2 text-sm leading-6 text-slate-300">
                                {issue.suggested_fix}
                              </p>
                            </div>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          )}
      </main>
    </div>
  );
}

export default CodeReview;