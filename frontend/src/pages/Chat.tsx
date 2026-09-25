import { useState } from "react";
import { useParams, Link } from "react-router-dom";
import {
  ArrowLeft,
  Send,
  Bot,
  User,
  FileCode,
  FileText,
  FileSpreadsheet,
  Search,
  Loader2,
} from "lucide-react";

type Message = {
  role: "user" | "assistant";
  content: string;
  sources?: Source[];
};

type Source = {
  file: string;
  location: string;
  type: "code" | "pdf" | "pptx" | "xlsx" | "document";
};

type BackendSource = {
  file?: string | null;
  file_id?: number | null;
  start_line?: number | null;
  end_line?: number | null;
  page?: number | null;
  slide?: number | null;
  sheet?: string | null;
};

type ChatResponse = {
  answer: string;
  sources: BackendSource[];
};

const API_BASE_URL =
  import.meta.env.VITE_API_URL ||
  "http://127.0.0.1:8000";


function Chat() {
  const { id } = useParams();

  const repositoryId = Number(id);

  const [question, setQuestion] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content:
        "Hello! I can answer questions about this repository using its indexed code, documents, configuration files, spreadsheets, and other supported files. Ask me about architecture, functions, workflows, dependencies, or specific implementation details.",
    },
  ]);


  /*
   * Convert backend source metadata into
   * the format already used by the UI.
   */
  const convertSource = (
    source: BackendSource
  ): Source => {

    const fileName =
      source.file || "Unknown file";

    const extension =
      fileName
        .split(".")
        .pop()
        ?.toLowerCase();


    let type: Source["type"] = "document";


    if (
      [
        "py",
        "js",
        "ts",
        "java",
        "cs",
        "sql",
      ].includes(extension || "")
    ) {
      type = "code";
    } else if (extension === "pdf") {
      type = "pdf";
    } else if (extension === "pptx") {
      type = "pptx";
    } else if (extension === "xlsx") {
      type = "xlsx";
    }


    let location = "";


    if (
      source.start_line !== null &&
      source.start_line !== undefined &&
      source.end_line !== null &&
      source.end_line !== undefined
    ) {

      location = `Lines ${source.start_line}-${source.end_line}`;

    } else if (
      source.start_line !== null &&
      source.start_line !== undefined
    ) {

      location = `Line ${source.start_line}`;

    } else if (
      source.page !== null &&
      source.page !== undefined
    ) {

      location = `Page ${source.page}`;

    } else if (
      source.slide !== null &&
      source.slide !== undefined
    ) {

      location = `Slide ${source.slide}`;

    } else if (source.sheet) {

      location = `Sheet: ${source.sheet}`;

    } else {

      location = "Repository source";

    }


    return {
      file: fileName,
      location,
      type,
    };
  };


  const sendMessage = async () => {

    const trimmedQuestion =
      question.trim();

    if (
      !trimmedQuestion ||
      isLoading
    ) {
      return;
    }

    if (
      !repositoryId ||
      Number.isNaN(repositoryId)
    ) {

      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          content:
            "Invalid repository ID. Please return to the Repository Explorer and open Chat again.",
        },
      ]);

      return;
    }

    const userMessage: Message = {
      role: "user",
      content: trimmedQuestion,
    };

    setMessages((previous) => [
      ...previous,
      userMessage,
    ]);

    setQuestion("");
    setIsLoading(true);

    let assistantStarted = false;

    const updateAssistant = (
      updater: (message: Message) => Message
    ) => {
      setMessages((previous) => {
        const lastIndex = previous.length - 1;

        if (
          lastIndex < 0 ||
          previous[lastIndex].role !== "assistant"
        ) {
          return previous;
        }

        const next = [...previous];
        next[lastIndex] = updater(next[lastIndex]);

        return next;
      });
    };

    const appendToken = (token: string) => {
      if (!token) {
        return;
      }

      if (!assistantStarted) {
        assistantStarted = true;

        setMessages((previous) => [
          ...previous,
          {
            role: "assistant",
            content: token,
          },
        ]);

        return;
      }

      updateAssistant((message) => ({
        ...message,
        content: message.content + token,
      }));
    };

    const attachSources = (
      sources: BackendSource[]
    ) => {
      const convertedSources =
        sources.map(convertSource);

      if (!assistantStarted) {
        assistantStarted = true;

        setMessages((previous) => [
          ...previous,
          {
            role: "assistant",
            content: "",
            sources: convertedSources,
          },
        ]);

        return;
      }

      updateAssistant((message) => ({
        ...message,
        sources: convertedSources,
      }));
    };

    const processStreamLine = (
      line: string
    ) => {
      if (!line.trim()) {
        return;
      }

      const event = JSON.parse(line) as {
        type: "token" | "sources" | "done" | "error";
        content?: string;
        sources?: BackendSource[];
        message?: string;
      };

      if (event.type === "token") {
        appendToken(event.content || "");
      } else if (event.type === "sources") {
        attachSources(event.sources || []);
      } else if (event.type === "error") {
        throw new Error(
          event.message ||
            "The AI stream failed."
        );
      }
    };

    try {
      const response = await fetch(
        `${API_BASE_URL}/chat/stream`,
        {
          method: "POST",
          headers: {
            "Content-Type":
              "application/json",
          },
          body: JSON.stringify({
            repository_id:
              repositoryId,
            question:
              trimmedQuestion,
          }),
        }
      );

      if (!response.ok) {
        let errorMessage =
          `Chat request failed (${response.status})`;

        try {
          const errorData =
            await response.json();

          if (errorData?.detail) {
            errorMessage =
              errorData.detail;
          }
        } catch {
          // Ignore JSON parsing errors
        }

        throw new Error(errorMessage);
      }

      if (!response.body) {
        throw new Error(
          "Streaming response is unavailable."
        );
      }

      const reader =
        response.body.getReader();

      const decoder =
        new TextDecoder();

      let buffer = "";

      while (true) {
        const {
          value,
          done,
        } = await reader.read();

        buffer += decoder.decode(
          value,
          {
            stream: !done,
          }
        );

        const lines =
          buffer.split("\n");

        buffer =
          lines.pop() || "";

        for (const line of lines) {
          processStreamLine(line);
        }

        if (done) {
          break;
        }
      }

      if (buffer.trim()) {
        processStreamLine(buffer);
      }

      if (!assistantStarted) {
        appendToken(
          "The AI did not return an answer."
        );
      }

    } catch (error) {
      console.error(
        "Chat error:",
        error
      );

      const errorMessage =
        error instanceof Error
          ? error.message
          : "Unable to connect to the RAG backend.";

      if (assistantStarted) {
        updateAssistant((message) => ({
          ...message,
          content:
            message.content ||
            `Sorry, I couldn't process your question.\n\n${errorMessage}`,
        }));
      } else {
        setMessages((previous) => [
          ...previous,
          {
            role: "assistant",
            content:
              `Sorry, I couldn't process your question.\n\n${errorMessage}`,
          },
        ]);
      }

    } finally {
      setIsLoading(false);
    }
  };


  const getSourceIcon = (
    type: Source["type"]
  ) => {

    switch (type) {

      case "code":

        return (
          <FileCode
            size={14}
            className="text-blue-400"
          />
        );


      case "pdf":

        return (
          <FileText
            size={14}
            className="text-red-400"
          />
        );


      case "pptx":

        return (
          <FileText
            size={14}
            className="text-orange-400"
          />
        );


      case "xlsx":

        return (
          <FileSpreadsheet
            size={14}
            className="text-emerald-400"
          />
        );


      default:

        return (
          <FileText
            size={14}
            className="text-slate-400"
          />
        );

    }
  };


  return (
    <div className="flex min-h-screen flex-col bg-slate-950 text-white">

      {/* Header */}

      <header className="border-b border-slate-800 bg-slate-900 px-8 py-5">

        <div className="flex items-center justify-between">

          <div>

            <Link
              to={`/repositories/${id}`}
              className="mb-2 flex items-center gap-2 text-sm text-slate-400 transition hover:text-white"
            >

              <ArrowLeft size={16} />

              Repository Explorer

            </Link>


            <div className="flex items-center gap-3">

              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-500/10">

                <Bot
                  size={22}
                  className="text-blue-400"
                />

              </div>


              <div>

                <h1 className="text-xl font-semibold">
                  Repository Chat
                </h1>

                <p className="text-sm text-slate-500">
                  Ask questions about your repository
                </p>

              </div>

            </div>

          </div>


          {/* RAG status */}

          <div className="flex items-center gap-2 rounded-full border border-emerald-500/20 bg-emerald-500/10 px-3 py-1.5 text-xs text-emerald-400">

            <span className="h-2 w-2 rounded-full bg-emerald-400" />

            RAG Ready

          </div>

        </div>

      </header>


      {/* Main chat area */}

      <main className="mx-auto flex w-full max-w-6xl flex-1 flex-col px-8">

        <div className="flex-1 space-y-6 overflow-y-auto py-8">

          {messages.map(
            (message, index) => (

              <div
                key={index}
                className={`flex gap-4 ${
                  message.role === "user"
                    ? "justify-end"
                    : "justify-start"
                }`}
              >

                {/* Assistant avatar */}

                {message.role ===
                  "assistant" && (

                  <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-blue-500/10">

                    <Bot
                      size={18}
                      className="text-blue-400"
                    />

                  </div>

                )}


                {/* Message */}

                <div
                  className={`max-w-3xl rounded-xl p-4 ${
                    message.role === "user"
                      ? "bg-blue-600"
                      : "border border-slate-800 bg-slate-900"
                  }`}
                >

                  <p className="whitespace-pre-wrap text-sm leading-7">
                    {message.content}
                  </p>


                  {/* Sources */}

                  {message.role ===
                    "assistant" &&
                    message.sources &&
                    message.sources.length >
                      0 && (

                    <div className="mt-5 border-t border-slate-800 pt-4">

                      <div className="mb-3 flex items-center gap-2">

                        <Search
                          size={14}
                          className="text-slate-500"
                        />

                        <p className="text-xs font-medium text-slate-500">
                          Sources
                        </p>

                      </div>


                      <div className="space-y-2">

                        {message.sources.map(
                          (
                            source,
                            sourceIndex
                          ) => (

                            <div
                              key={
                                sourceIndex
                              }
                              className="flex items-center gap-2 rounded-lg border border-slate-800 bg-slate-950 px-3 py-2"
                            >

                              {getSourceIcon(
                                source.type
                              )}


                              <span className="text-xs text-slate-300">
                                {source.file}
                              </span>


                              <span className="ml-auto text-xs text-slate-500">
                                {
                                  source.location
                                }
                              </span>

                            </div>

                          )
                        )}

                      </div>

                    </div>

                  )}

                </div>


                {/* User avatar */}

                {message.role ===
                  "user" && (

                  <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-slate-800">

                    <User size={18} />

                  </div>

                )}

              </div>

            )
          )}


          {/* Loading */}

          {isLoading &&\n            messages[messages.length - 1]?.role !== "assistant" && (

            <div className="flex gap-4">

              <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-blue-500/10">

                <Bot
                  size={18}
                  className="text-blue-400"
                />

              </div>


              <div className="flex items-center gap-3 rounded-xl border border-slate-800 bg-slate-900 px-5 py-4">

                <Loader2
                  size={17}
                  className="animate-spin text-blue-400"
                />

                <span className="text-sm text-slate-400">
                  Searching repository and generating answer...
                </span>

              </div>

            </div>

          )}

        </div>


        {/* Input section */}

        <div className="border-t border-slate-800 py-6">

          <div className="flex items-end gap-3 rounded-xl border border-slate-700 bg-slate-900 p-3 transition focus-within:border-blue-500">

            <textarea
              value={question}
              onChange={(event) =>
                setQuestion(
                  event.target.value
                )
              }
              onKeyDown={(event) => {

                if (
                  event.key === "Enter" &&
                  !event.shiftKey
                ) {

                  event.preventDefault();

                  sendMessage();

                }

              }}
              placeholder="Ask anything about this repository..."
              rows={2}
              disabled={isLoading}
              className="flex-1 resize-none bg-transparent px-2 py-2 text-sm text-white outline-none placeholder:text-slate-600 disabled:cursor-not-allowed disabled:opacity-50"
            />


            <button
              onClick={sendMessage}
              disabled={
                !question.trim() ||
                isLoading
              }
              className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-blue-600 transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-40"
            >

              {isLoading ? (

                <Loader2
                  size={17}
                  className="animate-spin"
                />

              ) : (

                <Send size={17} />

              )}

            </button>

          </div>


          <p className="mt-2 text-center text-xs text-slate-600">

            Answers are generated locally using indexed
            repository content and include source references.

          </p>

        </div>

      </main>

    </div>
  );
}


export default Chat;