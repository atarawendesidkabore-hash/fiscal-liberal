"use client";

import { useState } from "react";

export default function MereFiliale145() {
  const [pct, setPct] = useState(5);
  const [years, setYears] = useState(2);
  const [result, setResult] = useState<string>("");

  function quickCheck() {
    const ok = pct >= 5 && years >= 2;
    setResult(ok ? "Pre-check OK (a confirmer avec les 6 conditions)." : "Pre-check NOK.");
  }

  return (
    <div className="rounded bg-white p-4 shadow-sm">
      <h3 className="mb-2 font-semibold">Verificateur Art. 145</h3>
      <div className="grid gap-2 md:grid-cols-2">
        <input type="number" className="rounded border p-2" value={pct} onChange={(e) => setPct(Number(e.target.value))} />
        <input type="number" className="rounded border p-2" value={years} onChange={(e) => setYears(Number(e.target.value))} />
      </div>
      <button className="mt-3 rounded bg-fiscal-700 px-3 py-2 text-white" onClick={quickCheck}>
        Verifier
      </button>
      {result && <p className="mt-2 text-sm">{result}</p>}
    </div>
  );
}

