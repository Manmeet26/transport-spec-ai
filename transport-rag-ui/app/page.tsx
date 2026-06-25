"use client";

import { useState } from "react";

type Citation = {
  section: string;
  title: string;
  page?: number | null;
  snippet: string;
};

type Message = {
  role: "user" | "assistant";
  content: string;
  citations?: Citation[];
};

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

export default function Home() {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);

  function startNewChat() {
    setMessages([]);
    setQuestion("");
  }

  async function askQuestion() {
    if (!question.trim() || loading) return;

    const currentQuestion = question;

    setMessages((prev) => [
      ...prev,
      {
        role: "user",
        content: currentQuestion,
      },
    ]);

    setQuestion("");
    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/query`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question: currentQuestion,
        }),
      });

      const data = await response.json();

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: data.answer,
          citations: data.citations ?? [],
        },
      ]);
    } catch (error) {
      console.error(error);

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Error connecting to backend.",
        },
      ]);
    }

    setLoading(false);
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      askQuestion();
    }
  }

  return (
    <main className="min-h-screen bg-[#0b0f14] text-white">
      <div className="flex h-screen">
        <aside className="hidden w-72 border-r border-zinc-800 bg-[#080b10] p-5 md:block">
          <div className="mb-8">
            <h1 className="text-xl font-bold">Transport Spec RAG AI</h1>
            <p className="mt-2 text-sm text-zinc-400">
              Local RAG assistant for engineering standards.
            </p>
          </div>

          <button
            onClick={startNewChat}
            className="w-full rounded-xl border border-zinc-700 px-4 py-3 text-left text-sm hover:bg-zinc-900"
          >
            + New Chat
          </button>

          <div className="mt-8">
            <p className="mb-3 text-xs uppercase tracking-widest text-zinc-500">
              System
            </p>

            <div className="space-y-2 text-sm text-zinc-400">
              <div className="rounded-lg bg-zinc-900/60 p-3">
                Hybrid Retrieval
              </div>
              <div className="rounded-lg bg-zinc-900/60 p-3">
                BM25 + Vector Search
              </div>
              <div className="rounded-lg bg-zinc-900/60 p-3">
                Local Llama 3.1
              </div>
            </div>
          </div>
        </aside>

        <section className="flex flex-1 flex-col">
          <header className="border-b border-zinc-800 px-6 py-4">
            <h2 className="text-lg font-semibold">
              Transportation Engineering Copilot
            </h2>
            <p className="text-sm text-zinc-400">
              Ask specification questions and follow up naturally.
            </p>
          </header>

          <div className="flex-1 overflow-y-auto px-6 py-8">
            {messages.length === 0 && (
              <div className="mx-auto mt-20 max-w-3xl text-center">
                <div className="mx-auto mb-6 flex h-16 w-16 items-center justify-center rounded-2xl bg-zinc-900 text-3xl">
                  🛣️
                </div>

                <h3 className="text-3xl font-bold">
                  Ask your transportation specs
                </h3>

                <p className="mt-4 text-zinc-400">
                  Search Caltrans specifications using a fully local RAG system
                  with hybrid retrieval, reranking, and grounded answers.
                </p>

                <div className="mt-8 grid gap-3 text-left md:grid-cols-2">
                  {[
                    "What are curing requirements for concrete?",
                    "What are the requirements for pull boxes?",
                    "Explain high mast luminaire requirements.",
                    "What about cold weather?",
                  ].map((sample) => (
                    <button
                      key={sample}
                      onClick={() => setQuestion(sample)}
                      className="rounded-xl border border-zinc-800 bg-zinc-900/50 p-4 text-sm text-zinc-300 hover:bg-zinc-900"
                    >
                      {sample}
                    </button>
                  ))}
                </div>
              </div>
            )}

            <div className="mx-auto max-w-4xl space-y-6">
              {messages.map((message, index) => (
                <div
                  key={index}
                  className={`flex ${
                    message.role === "user" ? "justify-end" : "justify-start"
                  }`}
                >
                  <div
                    className={`max-w-[80%] rounded-2xl px-5 py-4 text-sm leading-7 shadow-lg whitespace-pre-wrap ${
                      message.role === "user"
                        ? "bg-white text-black"
                        : "border border-zinc-800 bg-zinc-900 text-zinc-100"
                    }`}
                  >
                    {message.content}

                    {message.role === "assistant" &&
                      message.citations &&
                      message.citations.length > 0 && (
                        <div className="mt-4 border-t border-zinc-700 pt-4">
                          <p className="mb-2 text-xs uppercase tracking-widest text-zinc-500">
                            Sources
                          </p>
                          <div className="space-y-2">
                            {message.citations.map((citation, citationIndex) => (
                              <div
                                key={citationIndex}
                                className="rounded-lg bg-zinc-950/70 p-3 text-xs text-zinc-300"
                              >
                                <p className="font-medium text-zinc-100">
                                  Section {citation.section}
                                  {citation.title ? ` — ${citation.title}` : ""}
                                  {citation.page ? ` (p. ${citation.page})` : ""}
                                </p>
                                <p className="mt-1 text-zinc-400">
                                  {citation.snippet}
                                </p>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                  </div>
                </div>
              ))}

              {loading && (
                <div className="flex justify-start">
                  <div className="rounded-2xl border border-zinc-800 bg-zinc-900 px-5 py-4 text-sm text-zinc-400">
                    Searching specifications...
                  </div>
                </div>
              )}
            </div>
          </div>

          <div className="border-t border-zinc-800 bg-[#0b0f14] px-6 py-5">
            <div className="mx-auto flex max-w-4xl gap-3">
              <textarea
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Ask a question about transportation specifications..."
                className="h-14 flex-1 resize-none rounded-2xl border border-zinc-700 bg-zinc-900 px-5 py-4 text-sm outline-none placeholder:text-zinc-500 focus:border-zinc-500"
              />

              <button
                onClick={askQuestion}
                disabled={loading}
                className="rounded-2xl bg-white px-6 font-semibold text-black transition hover:bg-zinc-200 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {loading ? "..." : "Send"}
              </button>
            </div>
          </div>
        </section>
      </div>
    </main>
  );
}
