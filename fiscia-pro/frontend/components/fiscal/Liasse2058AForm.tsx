"use client";

import { useMemo, useState } from "react";

import { DisclaimerBanner } from "./DisclaimerBanner";

type LiassePayload = {
  siren: string;
  ca_ht: number;
  capital_pme: boolean;
  WA_benefice_comptable: number;
  WQ_perte_comptable: number;
  WI_is_et_ifa: number;
  WG_amendes_penalites: number;
  WM_interets_excedentaires: number;
  WV_regime_mere_filiale: number;
  WN_reintegrations_diverses: number;
  ZL_deficit_reporte_arriere: number;
  XI_deficits_anterieurs_imputes: number;
};

export default function Liasse2058AForm() {
  const [form, setForm] = useState<LiassePayload>({
    siren: "",
    ca_ht: 0,
    capital_pme: false,
    WA_benefice_comptable: 0,
    WQ_perte_comptable: 0,
    WI_is_et_ifa: 0,
    WG_amendes_penalites: 0,
    WM_interets_excedentaires: 0,
    WV_regime_mere_filiale: 0,
    WN_reintegrations_diverses: 0,
    ZL_deficit_reporte_arriere: 0,
    XI_deficits_anterieurs_imputes: 0
  });
  const [result, setResult] = useState<null | Record<string, unknown>>(null);
  const [loading, setLoading] = useState(false);

  const fields = useMemo(
    () => [
      { key: "WA_benefice_comptable", label: "WA Benefice comptable", tip: "Base de depart resultat comptable." },
      { key: "WI_is_et_ifa", label: "WI IS comptabilise", tip: "Toujours reintegration (Art. 213 CGI)." },
      { key: "WG_amendes_penalites", label: "WG Amendes", tip: "Toujours reintegration (Art. 39-2 CGI)." },
      { key: "WM_interets_excedentaires", label: "WM Interets CC associes", tip: "Verifier plafond Art. 39-1-3 et 212 CGI." },
      { key: "WV_regime_mere_filiale", label: "WV Dividendes mere-filiale", tip: "Verifier les 6 conditions Art. 145 CGI." }
    ],
    []
  );

  async function submit() {
    setLoading(true);
    try {
      const res = await fetch("http://localhost:8000/api/liasse/calculer", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form)
      });
      const data = await res.json();
      setResult(data);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-4">
      <DisclaimerBanner />
      <div className="grid gap-3 rounded-lg bg-white p-4 shadow-sm md:grid-cols-2">
        {fields.map((f) => (
          <label key={f.key} className="text-sm">
            <div className="mb-1 font-medium">{f.label}</div>
            <input
              type="number"
              className="w-full rounded border border-slate-300 p-2"
              title={f.tip}
              value={(form as Record<string, number>)[f.key]}
              onChange={(e) =>
                setForm((prev) => ({
                  ...prev,
                  [f.key]: Number(e.target.value)
                }))
              }
            />
            <div className="mt-1 text-xs text-slate-500">{f.tip}</div>
          </label>
        ))}
        <label className="text-sm">
          <div className="mb-1 font-medium">CA HT</div>
          <input
            type="number"
            className="w-full rounded border border-slate-300 p-2"
            value={form.ca_ht}
            onChange={(e) => setForm((p) => ({ ...p, ca_ht: Number(e.target.value) }))}
          />
        </label>
        <label className="flex items-center gap-2 text-sm">
          <input
            type="checkbox"
            checked={form.capital_pme}
            onChange={(e) => setForm((p) => ({ ...p, capital_pme: e.target.checked }))}
          />
          Capital detenu >= 75% personnes physiques
        </label>
      </div>
      <button
        type="button"
        onClick={submit}
        className="rounded bg-fiscal-500 px-4 py-2 text-white disabled:opacity-60"
        disabled={loading}
      >
        {loading ? "Calcul en cours..." : "Calculer la liasse"}
      </button>
      {result && (
        <pre className="overflow-auto rounded bg-slate-900 p-4 text-xs text-slate-100">
          {JSON.stringify(result, null, 2)}
        </pre>
      )}
    </div>
  );
}

