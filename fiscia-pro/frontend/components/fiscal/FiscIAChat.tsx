"use client";

import { useState } from "react";

export default function FiscIAChat() {
  const [query, setQuery] = useState("");
  const [answer, setAnswer] = useState("");

  async function send() {
    const res = await fetch("http://localhost:8000/api/assistant/query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query, module: "assistant", is_confidentiel: false })
    });
    const data = await res.json();
    setAnswer((data?.suggestions || []).join("\n"));
  }

  return (
    <div className="rounded bg-white p-4 shadow-sm">
      <h3 className="mb-2 font-semibold">Assistant fiscal IA</h3>
      <textarea className="w-full rounded border p-2" rows={4} value={query} onChange={(e) => setQuery(e.target.value)} />
      <button className="mt-2 rounded bg-fiscal-500 px-3 py-2 text-white" onClick={send}>
        Envoyer
      </button>
      {answer && <pre className="mt-3 rounded bg-slate-900 p-3 text-xs text-slate-100">{answer}</pre>}
    </div>
  );
}

