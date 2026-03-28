"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import AIExplanationCard from "@/components/ai-explanation-card";
import {
  calculateLiasse,
  ApiError,
  explainLiasseWithAI,
  getAIStatus,
  type LiasseInput,
  type LiasseResult,
} from "@/lib/api";
import ProtectedRoute from "@/components/protected-route";
import {
  getImportFieldLabel,
  parseImportedLiasseFile,
  type ParsedLiasseImport,
} from "@/lib/liasse-import";

const FIELDS = [
  { key: "siren", label: "SIREN", type: "text", placeholder: "123456789", maxLength: 9 },
  { key: "exercice_clos", label: "Exercice clos le", type: "text", placeholder: "2024-12-31" },
  { key: "benefice_comptable", label: "Benefice comptable (EUR)", type: "number" },
  { key: "perte_comptable", label: "Perte comptable (EUR)", type: "number" },
  { key: "wi_is_comptabilise", label: "WI - IS comptabilise (EUR)", type: "number" },
  { key: "wg_amendes_penalites", label: "WG - Amendes et penalites (EUR)", type: "number" },
  { key: "wm_interets_excedentaires", label: "WM - Interets excedentaires (EUR)", type: "number" },
  { key: "wn_reintegrations_diverses", label: "WN - Reintegrations diverses (EUR)", type: "number" },
  { key: "wv_regime_mere_filiale", label: "WV - Deduction mere-filiale (EUR)", type: "number" },
  { key: "l8_qp_12pct", label: "L8 - QP frais 12% (EUR)", type: "number" },
] as const;

const SAMPLE_IMPORT_FILES = [
  { href: "/examples/fiscia-liasse-demo.json", label: "Exemple JSON" },
  { href: "/examples/fiscia-liasse-demo.csv", label: "Exemple CSV" },
  { href: "/examples/fiscia-liasse-demo.txt", label: "Exemple TXT" },
  { href: "/examples/fiscia-liasse-demo.xlsx", label: "Exemple Excel" },
] as const;

type FormData = Record<string, string>;

export default function LiassePage() {
  return (
    <ProtectedRoute>
      <LiasseForm />
    </ProtectedRoute>
  );
}

function LiasseForm() {
  const router = useRouter();
  const { token } = useAuth();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const initial: FormData = {};
  FIELDS.forEach((f) => (initial[f.key] = ""));
  initial.siren = "";
  initial.exercice_clos = "2024-12-31";

  const [form, setForm] = useState<FormData>(initial);
  const [ca, setCa] = useState("5000000");
  const [capitalPP, setCapitalPP] = useState(true);
  const [save, setSave] = useState(true);
  const [result, setResult] = useState<LiasseResult | null>(null);
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const [importing, setImporting] = useState(false);
  const [importNotice, setImportNotice] = useState("");
  const [importError, setImportError] = useState("");
  const [aiAvailable, setAiAvailable] = useState<boolean | null>(null);
  const [aiModel, setAiModel] = useState("");
  const [aiLoading, setAiLoading] = useState(false);
  const [aiError, setAiError] = useState("");
  const [aiResponse, setAiResponse] = useState("");
  const [aiDisclaimer, setAiDisclaimer] = useState("");

  useEffect(() => {
    const rawPrefill = localStorage.getItem("fiscia_2058a_prefill");
    if (!rawPrefill) {
      return;
    }

    try {
      const parsed = JSON.parse(rawPrefill) as {
        siren?: string;
        exercice_clos?: string;
        benefice_comptable?: string;
        perte_comptable?: string;
        ca?: string;
        capital_pp?: boolean;
        source?: string;
      };

      setForm((prev) => ({
        ...prev,
        siren: parsed.siren || prev.siren,
        exercice_clos: parsed.exercice_clos || prev.exercice_clos,
        benefice_comptable: parsed.benefice_comptable || prev.benefice_comptable,
        perte_comptable: parsed.perte_comptable || prev.perte_comptable,
      }));

      if (parsed.ca) {
        setCa(parsed.ca);
      }
      if (typeof parsed.capital_pp === "boolean") {
        setCapitalPP(parsed.capital_pp);
      }

      setImportError("");
      setImportNotice(
        parsed.source === "2065-2033"
          ? "Brouillon 2065 + 2033 charge. Completez les retraitements puis calculez l'IS."
          : "Prefill charge dans la liasse."
      );
    } catch {
      // Ignore invalid local draft payloads.
    } finally {
      localStorage.removeItem("fiscia_2058a_prefill");
    }
  }, []);

  useEffect(() => {
    if (!token) {
      return;
    }

    getAIStatus(token)
      .then((status) => {
        setAiAvailable(status.available);
        setAiModel(status.model);
      })
      .catch(() => {
        setAiAvailable(false);
      });
  }, [token]);

  function update(key: string, value: string) {
    setForm((prev) => ({ ...prev, [key]: value }));
  }

  function buildLiassePayload(): LiasseInput {
    return {
      siren: form.siren,
      exercice_clos: form.exercice_clos,
      benefice_comptable: Number(form.benefice_comptable) || 0,
      perte_comptable: Number(form.perte_comptable) || 0,
      wi_is_comptabilise: Number(form.wi_is_comptabilise) || 0,
      wg_amendes_penalites: Number(form.wg_amendes_penalites) || 0,
      wm_interets_excedentaires: Number(form.wm_interets_excedentaires) || 0,
      wn_reintegrations_diverses: Number(form.wn_reintegrations_diverses) || 0,
      wv_regime_mere_filiale: Number(form.wv_regime_mere_filiale) || 0,
      l8_qp_12pct: Number(form.l8_qp_12pct) || 0,
    };
  }

  function applyImportedValues(imported: ParsedLiasseImport) {
    setForm((prev) => ({ ...prev, ...imported.importedFormValues }));

    if (imported.ca) {
      setCa(imported.ca);
    }
    if (typeof imported.capitalPP === "boolean") {
      setCapitalPP(imported.capitalPP);
    }
    if (typeof imported.save === "boolean") {
      setSave(imported.save);
    }

    const preview = imported.matchedFieldKeys
      .slice(0, 4)
      .map((field) => getImportFieldLabel(field))
      .join(", ");
    const extraCount = Math.max(imported.matchedFieldKeys.length - 4, 0);
    const details = extraCount > 0 ? `${preview} + ${extraCount} autre(s)` : preview;

    setImportError("");
    setImportNotice(
      `${imported.fileName} importe. ${imported.matchedFieldKeys.length} champ(s) reconnu(s) : ${details}.`
    );
  }

  async function importFile(file: File | null) {
    if (!file) {
      return;
    }

    setImporting(true);
    setImportNotice("");
    setImportError("");

    try {
      const imported = await parseImportedLiasseFile(file);
      applyImportedValues(imported);
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Impossible d'importer ce fichier.";
      setImportError(message);
    } finally {
      setImporting(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    }
  }

  function handleDragOver(e: React.DragEvent<HTMLDivElement>) {
    e.preventDefault();
    setDragActive(true);
  }

  function handleDragLeave(e: React.DragEvent<HTMLDivElement>) {
    e.preventDefault();
    if (e.currentTarget.contains(e.relatedTarget as Node | null)) {
      return;
    }
    setDragActive(false);
  }

  async function handleDrop(e: React.DragEvent<HTMLDivElement>) {
    e.preventDefault();
    setDragActive(false);
    await importFile(e.dataTransfer.files?.[0] || null);
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setResult(null);
    setSubmitting(true);
    setAiError("");
    setAiResponse("");
    setAiDisclaimer("");

    try {
      const res = await calculateLiasse(token!, buildLiassePayload(), Number(ca), capitalPP, save);
      setResult(res);
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError("Erreur lors du calcul");
      }
    } finally {
      setSubmitting(false);
    }
  }

  async function handleExplainWithAI() {
    setAiLoading(true);
    setAiError("");

    try {
      const response = await explainLiasseWithAI(
        token!,
        buildLiassePayload(),
        Number(ca),
        capitalPP
      );
      setAiResponse(response.response);
      setAiDisclaimer(response.disclaimer);
    } catch (err) {
      if (err instanceof ApiError) {
        setAiError(err.message);
      } else {
        setAiError("Impossible d'obtenir l'explication IA pour le moment.");
      }
    } finally {
      setAiLoading(false);
    }
  }

  function handleContinueTo2058BC() {
    const payload = {
      liasse: {
        ...form,
      },
      ca,
      capital_pp: capitalPP,
      source: "2058-a",
    };

    localStorage.setItem("fiscia_2058bc_prefill", JSON.stringify(payload));
    router.push("/liasse/2058-b-c");
  }

  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">Liasse 2058-A - Determination du RF</h1>

      <div
        onDragOver={handleDragOver}
        onDragEnter={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={`mb-6 rounded-xl border-2 border-dashed p-6 transition ${
          dragActive
            ? "border-blue-400 bg-blue-500/10"
            : "border-slate-700 bg-slate-900/70"
        }`}
      >
        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div>
            <p className="text-sm font-semibold uppercase tracking-wide text-blue-400">
              Import rapide
            </p>
            <h2 className="mt-1 text-lg font-semibold text-white">
              Glissez-deposez un fichier dans le calculateur
            </h2>
            <p className="mt-2 text-sm text-slate-400">
              Formats acceptes : JSON, CSV, TXT, Excel et PDF. Les champs reconnus
              remplissent automatiquement la liasse, le CA et l&apos;option capital PP.
            </p>
          </div>

          <div className="flex shrink-0 flex-col gap-3 sm:flex-row">
            <button
              type="button"
              onClick={() => fileInputRef.current?.click()}
              disabled={importing}
              className="rounded-lg border border-slate-600 px-4 py-2 text-sm font-medium text-white transition hover:border-blue-400 hover:text-blue-300 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {importing ? "Import en cours..." : "Choisir un fichier"}
            </button>
            <div className="rounded-lg bg-slate-800 px-4 py-2 text-xs text-slate-400">
              Exemples : `.xlsx`, `.xls`, `.pdf`, `siren`, `benefice comptable`, `WI`, `CA`
            </div>
          </div>
        </div>

        <div className="mt-4 flex flex-wrap items-center gap-2 text-xs text-slate-400">
          <span>Telecharger des fichiers de test :</span>
          {SAMPLE_IMPORT_FILES.map((sample) => (
            <a
              key={sample.href}
              href={sample.href}
              download
              className="rounded-full border border-slate-700 px-3 py-1 text-slate-200 transition hover:border-blue-400 hover:text-blue-300"
            >
              {sample.label}
            </a>
          ))}
        </div>

        <input
          ref={fileInputRef}
          type="file"
          accept=".json,.csv,.txt,.xlsx,.xls,.xlsm,.xlsb,.pdf"
          className="hidden"
          onChange={(e) => {
            void importFile(e.target.files?.[0] || null);
          }}
        />
      </div>

      {importNotice && (
        <div className="mb-4 rounded-lg border border-green-800 bg-green-900/20 p-3 text-sm text-green-300">
          {importNotice}
        </div>
      )}

      {importError && (
        <div className="mb-4 rounded-lg border border-amber-700 bg-amber-900/20 p-3 text-sm text-amber-200">
          {importError}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="bg-slate-900 border border-slate-800 rounded-lg p-6">
          <h2 className="text-lg font-semibold text-blue-400 mb-4">Identification</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {FIELDS.slice(0, 2).map((f) => (
              <div key={f.key}>
                <label className="block text-sm text-slate-400 mb-1">{f.label}</label>
                <input
                  type={f.type}
                  required
                  value={form[f.key]}
                  onChange={(e) => update(f.key, e.target.value)}
                  placeholder={"placeholder" in f ? f.placeholder : ""}
                  maxLength={"maxLength" in f ? f.maxLength : undefined}
                  className="w-full bg-slate-800 border border-slate-700 rounded px-3 py-2 text-white focus:border-blue-500 focus:outline-none"
                />
              </div>
            ))}
          </div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-lg p-6">
          <h2 className="text-lg font-semibold text-blue-400 mb-4">
            Reintegrations et deductions
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {FIELDS.slice(2).map((f) => (
              <div key={f.key}>
                <label className="block text-sm text-slate-400 mb-1">{f.label}</label>
                <input
                  type="number"
                  step="0.01"
                  value={form[f.key]}
                  onChange={(e) => update(f.key, e.target.value)}
                  className="w-full bg-slate-800 border border-slate-700 rounded px-3 py-2 text-white focus:border-blue-500 focus:outline-none"
                  placeholder="0"
                />
              </div>
            ))}
          </div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-lg p-6">
          <h2 className="text-lg font-semibold text-blue-400 mb-4">Parametres IS</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm text-slate-400 mb-1">CA HT (EUR)</label>
              <input
                type="number"
                required
                value={ca}
                onChange={(e) => setCa(e.target.value)}
                className="w-full bg-slate-800 border border-slate-700 rounded px-3 py-2 text-white focus:border-blue-500 focus:outline-none"
              />
            </div>
            <div className="flex items-center gap-2 pt-6">
              <input
                type="checkbox"
                id="capital_pp"
                checked={capitalPP}
                onChange={(e) => setCapitalPP(e.target.checked)}
                className="rounded"
              />
              <label htmlFor="capital_pp" className="text-sm text-slate-300">
                Capital &ge; 75% personnes physiques
              </label>
            </div>
            <div className="flex items-center gap-2 pt-6">
              <input
                type="checkbox"
                id="save"
                checked={save}
                onChange={(e) => setSave(e.target.checked)}
                className="rounded"
              />
              <label htmlFor="save" className="text-sm text-slate-300">
                Sauvegarder le calcul
              </label>
            </div>
          </div>
        </div>

        {error && (
          <div className="bg-red-900/30 border border-red-800 text-red-300 text-sm rounded p-3">
            {error}
          </div>
        )}

        <button
          type="submit"
          disabled={submitting}
          className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-800 disabled:cursor-not-allowed text-white py-3 rounded-lg font-medium transition text-lg"
        >
          {submitting ? "Calcul en cours..." : "Calculer l'IS"}
        </button>
      </form>

      {result && (
        <>
          <ResultPanel result={result} onContinueTo2058BC={handleContinueTo2058BC} />
          <div className="mt-6">
            <AIExplanationCard
              title="Expliquer la 2058-A avec l'IA"
              description="Obtenez une lecture ligne par ligne des retraitements, des articles CGI mobilises et des points de vigilance avant de passer en 2058-B / 2058-C."
              available={aiAvailable}
              model={aiModel}
              loading={aiLoading}
              error={aiError}
              response={aiResponse}
              disclaimer={aiDisclaimer}
              onExplain={handleExplainWithAI}
            />
          </div>
        </>
      )}
    </div>
  );
}

function ResultPanel({
  result,
  onContinueTo2058BC,
}: {
  result: LiasseResult;
  onContinueTo2058BC: () => void;
}) {
  const fmt = (n: number) =>
    new Intl.NumberFormat("fr-FR", { style: "currency", currency: "EUR" }).format(n);

  return (
    <div className="mt-8 bg-slate-900 border border-green-800 rounded-lg p-6">
      <h2 className="text-lg font-semibold text-green-400 mb-4">Resultat du calcul</h2>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div>
          <div className="text-xs text-slate-500 uppercase">RF Brut</div>
          <div className="text-xl font-bold">{fmt(result.rf_brut)}</div>
        </div>
        <div>
          <div className="text-xs text-slate-500 uppercase">RF Net</div>
          <div className="text-xl font-bold">{fmt(result.rf_net)}</div>
        </div>
        <div>
          <div className="text-xs text-slate-500 uppercase">IS Total</div>
          <div className="text-xl font-bold text-blue-400">{fmt(result.is_total)}</div>
        </div>
        <div>
          <div className="text-xs text-slate-500 uppercase">Acompte trim.</div>
          <div className="text-xl font-bold">{fmt(result.acompte_trimestriel)}</div>
        </div>
      </div>

      <div className="mb-4">
        <span className="text-sm text-slate-400">Regime : </span>
        <span className="text-sm font-medium text-green-400">{result.regime}</span>
      </div>

      {Object.keys(result.details).length > 0 && (
        <div className="mb-4">
          <div className="text-sm text-slate-400 mb-2">Detail des ajustements :</div>
          <div className="grid grid-cols-2 gap-2">
            {Object.entries(result.details).map(([key, val]) => (
              <div key={key} className="flex justify-between text-sm bg-slate-800 rounded px-3 py-1.5">
                <span className="text-slate-400">{key}</span>
                <span className="font-mono">{fmt(val)}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {result.saved_id && (
        <div className="text-xs text-slate-500 mt-4">
          Calcul sauvegarde — ID : {result.saved_id}
        </div>
      )}

      <div className="mt-5 flex flex-col gap-3 sm:flex-row">
        <button
          type="button"
          onClick={onContinueTo2058BC}
          className="rounded-lg border border-blue-700 px-4 py-2 text-sm font-medium text-blue-300 transition hover:border-blue-500 hover:text-white"
        >
          Continuer vers 2058-B / 2058-C
        </button>
      </div>

      <div className="text-xs text-slate-600 mt-3 italic">{result.disclaimer}</div>
    </div>
  );
}
