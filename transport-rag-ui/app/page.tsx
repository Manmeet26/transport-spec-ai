"use client";

import { useState } from "react";

export default function Home() {

  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(false);

  async function askQuestion() {

    if (!question) return;

    setLoading(true);

    try {

      const response = await fetch(
        "http://127.0.0.1:8000/query",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            question,
          }),
        }
      );

      const data = await response.json();

      setAnswer(data.answer);

    } catch (error) {

      console.error(error);

      setAnswer(
        "Error connecting to backend."
      );

    }

    setLoading(false);
  }

  return (

    <main className="min-h-screen bg-black text-white">

      <div className="max-w-5xl mx-auto p-10">

        <h1 className="text-5xl font-bold mb-10">
          Transportation Spec AI
        </h1>

        <textarea
          value={question}
          onChange={(e) =>
            setQuestion(e.target.value)
          }
          placeholder="Ask transportation specification questions..."
          className="
            w-full
            h-40
            p-5
            rounded-2xl
            bg-zinc-900
            border
            border-zinc-700
            outline-none
          "
        />

        <button
          onClick={askQuestion}
          disabled={loading}
          className="
            mt-5
            px-6
            py-3
            rounded-xl
            bg-white
            text-black
            font-semibold
          "
        >

          {loading ? "Thinking..." : "Ask"}

        </button>

        {answer && (

          <div
            className="
              mt-10
              p-8
              rounded-2xl
              bg-zinc-900
            "
          >

            <h2 className="text-2xl font-bold mb-5">
              Answer
            </h2>

            <p className="whitespace-pre-wrap">
              {answer}
            </p>

          </div>
        )}

      </div>

    </main>
  );
}