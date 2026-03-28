"use client";

type AIExplanationCardProps = {
  title: string;
  description: string;
  available: boolean | null;
  model?: string;
  loading: boolean;
  error: string;
  response: string;
  disclaimer?: string;
  onExplain: () => void;
  buttonLabel?: string;
};

export default function AIExplanationCard({
  title,
  description,
  available,
  model,
  loading,
  error,
  response,
  disclaimer,
  onExplain,
  buttonLabel = "Expliquer avec l'IA",
}: AIExplanationCardProps) {
  const isUnavailable = available === false;

  return (
    <div className="rounded-lg border border-blue-900/60 bg-slate-900 p-6">
      <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
        <div>
          <div className="mb-2 inline-flex rounded-full border border-blue-700/60 bg-blue-950/40 px-3 py-1 text-xs font-medium text-blue-300">
            IA fiscale
          </div>
          <h3 className="text-lg font-semibold text-white">{title}</h3>
          <p className="mt-2 max-w-2xl text-sm text-slate-400">{description}</p>
          <p className="mt-3 text-xs text-slate-500">
            {available === null
              ? "Verification de la disponibilite de l'IA locale..."
              : isUnavailable
                ? "IA locale non disponible pour le moment."
                : `Modele actif : ${model || "IA locale"}`}
          </p>
        </div>

        <button
          type="button"
          onClick={onExplain}
          disabled={loading || isUnavailable}
          className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-blue-900/70 disabled:text-slate-300"
        >
          {loading ? "Analyse IA en cours..." : buttonLabel}
        </button>
      </div>

      {error && (
        <div className="mt-4 rounded-lg border border-red-800 bg-red-900/20 p-3 text-sm text-red-300">
          {error}
        </div>
      )}

      {response && (
        <div className="mt-4 rounded-lg border border-slate-800 bg-slate-950/70 p-4">
          <div className="mb-2 text-xs uppercase tracking-wide text-blue-300">Analyse</div>
          <div className="whitespace-pre-wrap text-sm leading-6 text-slate-200">{response}</div>
          {disclaimer && <div className="mt-3 text-xs italic text-slate-500">{disclaimer}</div>}
        </div>
      )}
    </div>
  );
}
