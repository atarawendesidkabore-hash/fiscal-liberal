"use client";

import { useEffect, useState, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";
import AIExplanationCard from "@/components/ai-explanation-card";
import { useAuth } from "@/lib/auth-context";
import {
  ApiError,
  explainWithAI,
  getAIStatus,
  getSavedLiasse,
  type SavedLiasseDetail,
} from "@/lib/api";
import ProtectedRoute from "@/components/protected-route";

export default function ResultatsPage() {
  return (
    <ProtectedRoute>
      <Suspense fallback={<div className="text-slate-400 text-center py-12">Chargement...</div>}>
        <ResultatsContent />
      </Suspense>
    </ProtectedRoute>
  );
}

function ResultatsContent() {
  const { token } = useAuth();
  const searchParams = useSearchParams();
  const id = searchParams.get("id");

  const [record, setRecord] = useState<SavedLiasseDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [aiAvailable, setAiAvailable] = useState<boolean | null>(null);
  const [aiModel, setAiModel] = useState("");
  const [aiLoading, setAiLoading] = useState(false);
  const [aiError, setAiError] = useState("");
  const [aiResponse, setAiResponse] = useState("");
  const [aiDisclaimer, setAiDisclaimer] = useState("");

  useEffect(() => {
    if (!token || !id) return;
    getSavedLiasse(token, id)
      .then(setRecord)
      .catch(() => setError("Calcul non trouve"))
      .finally(() => setLoading(false));
  }, [token, id]);

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

  const fmt = (n: number) =>
    new Intl.NumberFormat("fr-FR", { style: "currency", currency: "EUR" }).format(n);

  if (!id) {
    return (
      <div className="text-center py-16">
        <p className="text-slate-500">Aucun calcul selectionne</p>
        <Link href="/dashboard" className="text-blue-400 hover:underline mt-2 inline-block">
          Retour au tableau de bord
        </Link>
      </div>
    );
  }

  if (loading) {
    return <div className="text-slate-400 text-center py-12">Chargement...</div>;
  }

  if (error || !record) {
    return (
      <div className="text-center py-16">
        <p className="text-red-400">{error || "Calcul non trouve"}</p>
        <Link href="/dashboard" className="text-blue-400 hover:underline mt-2 inline-block">
          Retour au tableau de bord
        </Link>
      </div>
    );
  }

  const result = record.result_data as Record<string, number | string | Record<string, number>>;
  const input = record.input_data as Record<string, string | number>;
  const resultMeta = (result.meta || {}) as { ca?: number; capital_pp?: boolean };

  async function handleExplainWithAI() {
    if (!token || !record) {
      return;
    }

    setAiLoading(true);
    setAiError("");

    const prompt = [
      "Analyse ce dossier fiscal sauvegarde FiscIA Pro.",
      `SIREN: ${record.siren}`,
      `Exercice clos: ${record.exercice_clos}`,
      `Donnees 2058-A: ${JSON.stringify(input)}`,
      `Resultat calcule: ${JSON.stringify(result)}`,
      "Explique les principaux retraitements, les points de vigilance, les articles CGI mobilises et les prochaines etapes vers 2058-B / 2058-C.",
    ].join("\n");

    try {
      const response = await explainWithAI(token, prompt, "liasse");
      setAiResponse(response.response);
      setAiDisclaimer(response.disclaimer);
    } catch (err) {
      if (err instanceof ApiError) {
        setAiError(err.message);
      } else {
        setAiError("Impossible d'obtenir l'analyse IA du calcul sauvegarde.");
      }
    } finally {
      setAiLoading(false);
    }
  }

  function handleContinueTo2058BC() {
    if (!record) {
      return;
    }

    const liassePrefill = Object.fromEntries(
      Object.entries(input).map(([key, value]) => [key, String(value ?? "")])
    );

    localStorage.setItem(
      "fiscia_2058bc_prefill",
      JSON.stringify({
        liasse: liassePrefill,
        ca: resultMeta.ca ? String(resultMeta.ca) : "0",
        capital_pp: Boolean(resultMeta.capital_pp),
        source: "resultats",
      })
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Detail du calcul</h1>
        <Link
          href="/dashboard"
          className="text-sm text-slate-400 hover:text-white transition"
        >
          Retour au tableau de bord
        </Link>
      </div>

      {/* Header info */}
      <div className="bg-slate-900 border border-slate-800 rounded-lg p-6 mb-6">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <div className="text-xs text-slate-500 uppercase">SIREN</div>
            <div className="font-mono text-lg">{record.siren}</div>
          </div>
          <div>
            <div className="text-xs text-slate-500 uppercase">Exercice</div>
            <div className="text-lg">{record.exercice_clos}</div>
          </div>
          <div>
            <div className="text-xs text-slate-500 uppercase">Cree le</div>
            <div className="text-lg">
              {record.created_at
                ? new Date(record.created_at).toLocaleDateString("fr-FR")
                : "—"}
            </div>
          </div>
          <div>
            <div className="text-xs text-slate-500 uppercase">ID</div>
            <div className="text-xs font-mono text-slate-500 break-all">{record.id}</div>
          </div>
        </div>
      </div>

      {/* Results */}
      <div className="bg-slate-900 border border-green-800 rounded-lg p-6 mb-6">
        <h2 className="text-lg font-semibold text-green-400 mb-4">Resultat IS</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
          <div>
            <div className="text-xs text-slate-500 uppercase">RF Brut</div>
            <div className="text-xl font-bold">{fmt(result.rf_brut as number)}</div>
          </div>
          <div>
            <div className="text-xs text-slate-500 uppercase">RF Net</div>
            <div className="text-xl font-bold">{fmt(result.rf_net as number)}</div>
          </div>
          <div>
            <div className="text-xs text-slate-500 uppercase">IS Total</div>
            <div className="text-xl font-bold text-blue-400">
              {fmt(result.is_total as number)}
            </div>
          </div>
          <div>
            <div className="text-xs text-slate-500 uppercase">Acompte trim.</div>
            <div className="text-xl font-bold">
              {fmt(result.acompte_trimestriel as number)}
            </div>
          </div>
        </div>
        <div>
          <span className="text-sm text-slate-400">Regime : </span>
          <span className="text-sm font-medium text-green-400">
            {result.regime as string}
          </span>
        </div>
      </div>

      {/* Input data */}
      <div className="bg-slate-900 border border-slate-800 rounded-lg p-6 mb-6">
        <h2 className="text-lg font-semibold text-blue-400 mb-4">Donnees saisies</h2>
        <div className="grid grid-cols-2 gap-2">
          {Object.entries(input).map(([key, val]) => (
            <div
              key={key}
              className="flex justify-between text-sm bg-slate-800 rounded px-3 py-2"
            >
              <span className="text-slate-400">{key}</span>
              <span className="font-mono">
                {typeof val === "number" ? fmt(val) : String(val)}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Details breakdown */}
      {result.details && typeof result.details === "object" && (
        <div className="bg-slate-900 border border-slate-800 rounded-lg p-6">
          <h2 className="text-lg font-semibold text-blue-400 mb-4">
            Detail des ajustements
          </h2>
          <div className="grid grid-cols-2 gap-2">
            {Object.entries(result.details as Record<string, number>).map(([key, val]) => (
              <div
                key={key}
                className="flex justify-between text-sm bg-slate-800 rounded px-3 py-2"
              >
                <span className="text-slate-400">{key}</span>
                <span className="font-mono">{fmt(val)}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="mt-6 flex flex-col gap-3 sm:flex-row">
        <Link
          href="/liasse/2058-b-c"
          onClick={handleContinueTo2058BC}
          className="rounded-lg border border-blue-700 px-4 py-2 text-sm font-medium text-blue-300 transition hover:border-blue-500 hover:text-white"
        >
          Continuer vers 2058-B / 2058-C
        </Link>
      </div>

      <div className="mt-6">
        <AIExplanationCard
          title="Expliquer ce calcul sauvegarde avec l'IA"
          description="Demandez a l'IA fiscale de relire le dossier, d'expliquer la logique 2058-A et de pointer les zones a confirmer avant cloture."
          available={aiAvailable}
          model={aiModel}
          loading={aiLoading}
          error={aiError}
          response={aiResponse}
          disclaimer={aiDisclaimer}
          onExplain={handleExplainWithAI}
        />
      </div>

      <div className="text-xs text-slate-600 mt-6 italic">{record.disclaimer}</div>
    </div>
  );
}
