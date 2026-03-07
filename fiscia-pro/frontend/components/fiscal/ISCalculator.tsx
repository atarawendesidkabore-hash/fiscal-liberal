"use client";

import { useState } from "react";

export default function ISCalculator() {
  const [rf, setRf] = useState(0);
  const [ca, setCa] = useState(0);
  const [capitalOk, setCapitalOk] = useState(false);
  const [result, setResult] = useState<null | Record<string, unknown>>(null);

  async function runCalc() {
    const res = await fetch("http://localhost:8000/api/is-calcul", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ rf, ca_ht: ca, capital_75pct_pp: capitalOk })
    });
    setResult(await res.json());
  }

  return (
    <div className="space-y-3 rounded bg-white p-4 shadow-sm">
      <h2 className="text-lg font-semibold">Calculateur IS Art. 219</h2>
      <input className="w-full rounded border p-2" type="number" value={rf} onChange={(e) => setRf(Number(e.target.value))} placeholder="Resultat fiscal" />
      <input className="w-full rounded border p-2" type="number" value={ca} onChange={(e) => setCa(Number(e.target.value))} placeholder="CA HT" />
      <label className="flex items-center gap-2 text-sm">
        <input type="checkbox" checked={capitalOk} onChange={(e) => setCapitalOk(e.target.checked)} />
        Capital >= 75% personnes physiques
      </label>
      <button className="rounded bg-fiscal-500 px-4 py-2 text-white" onClick={runCalc}>
        Calculer
      </button>
      {result && <pre className="rounded bg-slate-900 p-3 text-xs text-slate-100">{JSON.stringify(result, null, 2)}</pre>}
    </div>
  );
}

