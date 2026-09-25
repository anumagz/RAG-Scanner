import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import {
  FolderGit2,
  Folder,
  FileCode2,
  Database,
  Plus,
  Trash2,
  RefreshCw,
  Search,
  CheckCircle2,
  Clock3,
  Loader2,
  AlertCircle,
  ArrowRight,
} from "lucide-react";

import {
  getRepositories,
  addRepository,
  deleteRepository,
  rescanRepository,
} from "../services/api";

export default function Dashboard() {
  const queryClient = useQueryClient();

  const [repositoryPath, setRepositoryPath] =
    useState("");

  const [showAddForm, setShowAddForm] =
    useState(false);

  const {
    data: repositories = [],
    isLoading,
    error,
  } = useQuery({
    queryKey: ["repositories"],
    queryFn: getRepositories,
  });

  const addMutation = useMutation({
    mutationFn: addRepository,

    onSuccess: () => {
      setRepositoryPath("");
      setShowAddForm(false);

      queryClient.invalidateQueries({
        queryKey: ["repositories"],
      });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: deleteRepository,

    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["repositories"],
      });
    },
  });

  const rescanMutation = useMutation({
    mutationFn: rescanRepository,

    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["repositories"],
      });
    },
  });

  const handleAddRepository = () => {
    if (!repositoryPath.trim()) {
      return;
    }

    addMutation.mutate(repositoryPath.trim());
  };

  const totalFiles = repositories.reduce(
    (total, repository) =>
      total + (repository.file_count || 0),
    0
  );

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      {/* Header */}
      <header className="border-b border-slate-800 bg-slate-900/80 px-8 py-5">
        <div className="mx-auto flex max-w-7xl items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-blue-500/10">
              <FolderGit2
                size={24}
                className="text-blue-400"
              />
            </div>

            <div>
              <h1 className="text-xl font-semibold">
                AI Repository Scanner
              </h1>

              <p className="text-sm text-slate-500">
                Understand your repositories locally with AI
              </p>
            </div>
          </div>

          <button
            onClick={() => setShowAddForm(true)}
            className="flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2.5 text-sm font-medium transition hover:bg-blue-500"
          >
            <Plus size={17} />
            Add Repository
          </button>
        </div>
      </header>

      <main className="mx-auto max-w-7xl space-y-8 p-8">
        {/* Statistics */}
        <section className="grid gap-5 md:grid-cols-3">
          <div className="rounded-xl border border-slate-800 bg-slate-900 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-500">
                  Repositories
                </p>

                <p className="mt-2 text-3xl font-bold">
                  {repositories.length}
                </p>
              </div>

              <div className="rounded-lg bg-blue-500/10 p-3">
                <Folder
                  size={22}
                  className="text-blue-400"
                />
              </div>
            </div>
          </div>

          <div className="rounded-xl border border-slate-800 bg-slate-900 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-500">
                  Files Indexed
                </p>

                <p className="mt-2 text-3xl font-bold">
                  {totalFiles}
                </p>
              </div>

              <div className="rounded-lg bg-purple-500/10 p-3">
                <FileCode2
                  size={22}
                  className="text-purple-400"
                />
              </div>
            </div>
          </div>

          <div className="rounded-xl border border-slate-800 bg-slate-900 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-500">
                  AI Engine
                </p>

                <p className="mt-2 text-lg font-semibold text-emerald-400">
                  Local / Ollama
                </p>
              </div>

              <div className="rounded-lg bg-emerald-500/10 p-3">
                <Database
                  size={22}
                  className="text-emerald-400"
                />
              </div>
            </div>
          </div>
        </section>

        {/* Add repository */}
        {showAddForm && (
          <section className="rounded-xl border border-blue-500/20 bg-slate-900 p-6">
            <div className="flex items-start justify-between">
              <div>
                <h2 className="text-lg font-semibold">
                  Add Repository
                </h2>

                <p className="mt-1 text-sm text-slate-500">
                  Enter the absolute path of a local repository.
                </p>
              </div>

              <button
                onClick={() => setShowAddForm(false)}
                className="text-slate-500 hover:text-white"
              >
                ✕
              </button>
            </div>

            <div className="mt-5 flex gap-3">
              <input
                value={repositoryPath}
                onChange={(event) =>
                  setRepositoryPath(event.target.value)
                }
                onKeyDown={(event) => {
                  if (event.key === "Enter") {
                    handleAddRepository();
                  }
                }}
                placeholder="C:\Projects\MyApplication"
                className="flex-1 rounded-lg border border-slate-700 bg-slate-950 px-4 py-3 text-sm outline-none placeholder:text-slate-600 focus:border-blue-500"
              />

              <button
                onClick={handleAddRepository}
                disabled={addMutation.isPending}
                className="flex items-center gap-2 rounded-lg bg-blue-600 px-6 py-3 text-sm font-medium hover:bg-blue-500 disabled:opacity-50"
              >
                {addMutation.isPending ? (
                  <Loader2
                    size={16}
                    className="animate-spin"
                  />
                ) : (
                  <Plus size={16} />
                )}

                Add
              </button>
            </div>

            {addMutation.isError && (
              <p className="mt-3 flex items-center gap-2 text-sm text-red-400">
                <AlertCircle size={15} />
                {addMutation.error instanceof Error
                  ? addMutation.error.message
                  : "Failed to add repository."}
              </p>
            )}
          </section>
        )}

        {/* Repository list */}
        <section>
          <div className="mb-5 flex items-center justify-between">
            <div>
              <h2 className="text-xl font-semibold">
                Your Repositories
              </h2>

              <p className="mt-1 text-sm text-slate-500">
                Browse and analyze your indexed repositories.
              </p>
            </div>

            <div className="relative">
              <Search
                size={16}
                className="absolute left-3 top-2.5 text-slate-600"
              />

              <input
                placeholder="Search repositories"
                className="rounded-lg border border-slate-800 bg-slate-900 py-2 pl-9 pr-4 text-sm outline-none focus:border-blue-500"
              />
            </div>
          </div>

          {/* Loading */}
          {isLoading && (
            <div className="flex items-center justify-center rounded-xl border border-slate-800 bg-slate-900 py-16">
              <div className="flex items-center gap-3 text-slate-400">
                <Loader2
                  size={20}
                  className="animate-spin"
                />
                Loading repositories...
              </div>
            </div>
          )}

          {/* Error */}
          {error && (
            <div className="rounded-xl border border-red-500/20 bg-red-500/5 p-6">
              <div className="flex items-center gap-3 text-red-400">
                <AlertCircle size={20} />

                <div>
                  <p className="font-medium">
                    Failed to load repositories
                  </p>

                  <p className="mt-1 text-sm text-slate-500">
                    Make sure the FastAPI backend is running on
                    port 8000.
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Empty */}
          {!isLoading &&
            !error &&
            repositories.length === 0 && (
              <div className="rounded-xl border border-dashed border-slate-700 bg-slate-900/50 p-16 text-center">
                <FolderGit2
                  size={45}
                  className="mx-auto text-slate-700"
                />

                <h3 className="mt-5 text-lg font-semibold">
                  No repositories yet
                </h3>

                <p className="mx-auto mt-2 max-w-md text-sm text-slate-500">
                  Add a local repository to start scanning,
                  indexing and understanding your codebase.
                </p>

                <button
                  onClick={() => setShowAddForm(true)}
                  className="mt-6 rounded-lg bg-blue-600 px-5 py-2.5 text-sm font-medium hover:bg-blue-500"
                >
                  Add Your First Repository
                </button>
              </div>
            )}

          {/* Repository cards */}
          {!isLoading &&
            !error &&
            repositories.length > 0 && (
              <div className="grid gap-5 md:grid-cols-2">
                {repositories.map((repository) => {
                  const status =
                    repository.status?.toLowerCase();

                  return (
                    <div
                      key={repository.id}
                      className="group rounded-xl border border-slate-800 bg-slate-900 p-6 transition hover:border-slate-700"
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex gap-4">
                          <div className="flex h-11 w-11 items-center justify-center rounded-lg bg-blue-500/10">
                            <Folder
                              size={22}
                              className="text-blue-400"
                            />
                          </div>

                          <div>
                            <h3 className="font-semibold">
                              {repository.name}
                            </h3>

                            <p className="mt-1 max-w-sm break-all text-xs text-slate-500">
                              {repository.path}
                            </p>
                          </div>
                        </div>

                        <button
                          onClick={() =>
                            deleteMutation.mutate(
                              repository.id
                            )
                          }
                          disabled={deleteMutation.isPending}
                          className="rounded-lg p-2 text-slate-600 transition hover:bg-red-500/10 hover:text-red-400"
                          title="Delete repository"
                        >
                          <Trash2 size={17} />
                        </button>
                      </div>

                      <div className="mt-6 flex items-center justify-between border-t border-slate-800 pt-5">
                        <div className="flex items-center gap-2">
                          {status === "completed" ? (
                            <>
                              <CheckCircle2
                                size={15}
                                className="text-emerald-400"
                              />

                              <span className="text-xs text-emerald-400">
                                Indexed
                              </span>
                            </>
                          ) : status === "running" ||
                            status === "queued" ? (
                            <>
                              <Clock3
                                size={15}
                                className="text-yellow-400"
                              />

                              <span className="text-xs text-yellow-400">
                                {repository.status}
                              </span>
                            </>
                          ) : (
                            <span className="text-xs text-slate-500">
                              {repository.status ||
                                "Ready"}
                            </span>
                          )}

                          <span className="ml-2 text-xs text-slate-600">
                            {repository.file_count || 0} files
                          </span>
                        </div>

                        <div className="flex gap-2">
                          <button
                            onClick={() =>
                              rescanMutation.mutate(
                                repository.id
                              )
                            }
                            disabled={
                              rescanMutation.isPending
                            }
                            className="rounded-lg border border-slate-700 p-2 text-slate-400 hover:bg-slate-800 hover:text-white"
                            title="Rescan"
                          >
                            <RefreshCw
                              size={15}
                              className={
                                rescanMutation.isPending
                                  ? "animate-spin"
                                  : ""
                              }
                            />
                          </button>

                          <Link
                            to={`/repositories/${repository.id}`}
                            className="flex items-center gap-2 rounded-lg bg-slate-800 px-3 py-2 text-xs font-medium hover:bg-slate-700"
                          >
                            Explore
                            <ArrowRight size={14} />
                          </Link>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
        </section>
      </main>
    </div>
  );
}