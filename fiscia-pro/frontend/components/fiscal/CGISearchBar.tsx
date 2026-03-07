"use client";

import { useState } from "react";

export default function CGISearchBar() {
  const [query, setQuery] = useState("");
  const [result, setResult] = useState<null | Record<string, unknown>>(null);

  async function search() {
    const res = await fetch("http://localhost:8000/api/recherche-cgi", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query })
    });
    setResult(await res.json());
  }

  return (
    <div className="rounded bg-white p-4 shadow-sm">
      <div className="mb-2 font-semibold">Recherche CGI semantique</div>
      <div className="flex gap-2">
        <input className="flex-1 rounded border p-2" value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Ex: Art. 219 taux reduit PME" />
        <button className="rounded bg-fiscal-500 px-3 py-2 text-white" onClick={search}>
          Rechercher
        </button>
      </div>
      {result && <pre className="mt-3 rounded bg-slate-900 p-3 text-xs text-slate-100">{JSON.stringify(result, null, 2)}</pre>}
    </div>
  );
}

