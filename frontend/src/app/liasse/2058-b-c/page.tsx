"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import ProtectedRoute from "@/components/protected-route";
import { useAuth } from "@/lib/auth-context";
import {
  ApiError,
  prepare2058BC,
  type Liasse2058BCInput,
  type Liasse2058BCResult,
  type LiasseInput,
} from "@/lib/api";

const LIASSE_FIELDS = [
  { key: "siren", label: "SIREN", type: "text", placeholder: "123456789", maxLength: 9 },
  { key: "exercice_clos", label: "Exercice clos le", type: "text", placeholder: "2024-12-31" },
  { key: "benefice_comptable", label: "Benefice comptable (EUR)", type: "number" },
  { key: "perte_comptable", label: "Perte comptable (EUR)", type: "number" },
  { key: "wi_is_comptabilise", label: "WI - IS comptabilise (EUR)", type: "number" },
  { key: "wg_amendes_penalites", label: "WG - Amendes et penalites (EUR)", type: "number" },
  { key: "wm_interets_excedentaires", label: "WM - Interets excedentaires (EUR)", type: "number" },
  { key: "wn_reintegrations_diverses", label: "WN - Reintegrations diverses (EUR)", type: "number" },
  { key: "wv_regime_mere_filiale", label: "WV - Regime mere-filiale (EUR)", type: "number" },
  { key: "l8_qp_12pct", label: "L8 - QP frais 12% (EUR)", type: "number" },
] as const;

const ANNEX_FIELDS: Array<{
  key: keyof Liasse2058BCInput;
  label: string;
  description: string;
}> = [
  {
    key: "deficits_reportables_ouverture",
    label: "Deficits reportables a l'ouverture",
    description: "Stock de deficits fiscaux disponibles avant imputation sur l'exercice.",
  },
  {
    key: "moins_values_lt_ouverture",
    label: "Moins-values LT a l'ouverture",
    description: "Suivi long terme repris dans le brouillon 2058-B.",
  },
  {
    key: "moins_values_lt_imputees",
    label: "Moins-values LT imputees",
    description: "Part des moins-values long terme consommee pendant l'exercice.",
  },
  {
    key: "acomptes_verses",
    label: "Acomptes d'IS verses",
    description: "Montant deja paye au titre des acomptes.",
  },
  {
    key: "credits_impot",
    label: "Credits d'impot imputables",
    description: "Credits d'impot a deduire du solde 2058-C.",
  },
  {
    key: "contribution_sociale",
    label: "Contribution additionnelle",
    description: "Contribution ou surtaxe a rajouter au total du.",
  },
  {
    key: "regularisations",
    label: "Regularisations",
    description: "Ajustements manuels a reporter dans le brouillon 2058-C.",
  },
] as const;

type LiasseFormData = Record<(typeof LIASSE_FIELDS)[number]["key"], string>;
type AnnexFormData = Record<keyof Liasse2058BCInput, string>;

export default function Liasse2058BCPage() {
  return (
    <ProtectedRoute>
      <Liasse2058BCForm />
    </ProtectedRoute>
  );
}

function Liasse2058BCForm() {
  const { token } = useAuth();

  const initialLiasse = LIASSE_FIELDS.reduce((acc, field) => {
    acc[field.key] = "";
    return acc;
  }, {} as LiasseFormData);
  initialLiasse.exercice_clos = "2024-12-31";

  const initialAnnexes = ANNEX_FIELDS.reduce((acc, field) => {
    acc[field.key] = "0";
    return acc;
  }, {} as AnnexFormData);

  const [liasseForm, setLiasseForm] = useState<LiasseFormData>(initialLiasse);
  const [annexForm, setAnnexForm] = useState<AnnexFormData>(initialAnnexes);
  const [ca, setCa] = useState("0");
  const [capitalPP, setCapitalPP] = useState(true);
  const [notice, setNotice] = useState("");
  const [error, setError] = useState("");
  const [result, setResult] = useState<Liasse2058BCResult | null>(null);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    const rawPrefill = localStorage.getItem("fiscia_2058bc_prefill");
    if (!rawPrefill) {
      return;
    }

    try {
      const parsed = JSON.parse(rawPrefill) as {
        liasse?: Partial<LiasseFormData>;
        ca?: string;
        capital_pp?: boolean;
        source?: string;
      };

      if (parsed.liasse) {
        setLiasseForm((prev) => ({ ...prev, ...parsed.liasse }));
      }
      if (parsed.ca) {
        setCa(parsed.ca);
      }
      if (typeof parsed.capital_pp === "boolean") {
        setCapitalPP(parsed.capital_pp);
      }

      setNotice(
        parsed.source === "resultats"
          ? "Dossier charge depuis la page Resultats. Completez les annexes puis preparez 2058-B / 2058-C."
          : "Dossier charge depuis la liasse 2058-A. Completez les annexes puis preparez 2058-B / 2058-C."
      );
    } catch {
      setNotice("");
    } finally {
      localStorage.removeItem("fiscia_2058bc_prefill");
    }
  }, []);

  function updateLiasse(key: keyof LiasseFormData, value: string) {
    setLiasseForm((prev) => ({ ...prev, [key]: value }));
  }

  function updateAnnexe(key: keyof AnnexFormData, value: string) {
    setAnnexForm((prev) => ({ ...prev, [key]: value }));
  }

  function parseNumber(value: string) {
    const parsed = Number(value);
    return Number.isFinite(parsed) ? parsed : 0;
  }

  function buildLiassePayload(): LiasseInput {
    return {
      siren: liasseForm.siren,
      exercice_clos: liasseForm.exercice_clos,
      benefice_comptable: parseNumber(liasseForm.benefice_comptable),
      perte_comptable: parseNumber(liasseForm.perte_comptable),
      wi_is_comptabilise: parseNumber(liasseForm.wi_is_comptabilise),
      wg_amendes_penalites: parseNumber(liasseForm.wg_amendes_penalites),
      wm_interets_excedentaires: parseNumber(liasseForm.wm_interets_excedentaires),
      wn_reintegrations_diverses: parseNumber(liasseForm.wn_reintegrations_diverses),
      wv_regime_mere_filiale: parseNumber(liasseForm.wv_regime_mere_filiale),
      l8_qp_12pct: parseNumber(liasseForm.l8_qp_12pct),
    };
  }

  function buildAnnexPayload(): Liasse2058BCInput {
    return {
      deficits_reportables_ouverture: parseNumber(annexForm.deficits_reportables_ouverture),
      moins_values_lt_ouverture: parseNumber(annexForm.moins_values_lt_ouverture),
      moins_values_lt_imputees: parseNumber(annexForm.moins_values_lt_imputees),
      acomptes_verses: parseNumber(annexForm.acomptes_verses),
      credits_impot: parseNumber(annexForm.credits_impot),
      contribution_sociale: parseNumber(annexForm.contribution_sociale),
      regularisations: parseNumber(annexForm.regularisations),
    };
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    setError("");

    try {
      const response = await prepare2058BC(
        token!,
        buildLiassePayload(),
        parseNumber(ca),
        capitalPP,
        buildAnnexPayload()
      );
      setResult(response);
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError("Erreur lors de la preparation 2058-B / 2058-C");
      }
    } finally {
      setSubmitting(false);
    }
  }

  const canSubmit =
    liasseForm.siren.trim().length === 9 &&
    Boolean(liasseForm.exercice_clos) &&
    parseNumber(ca) > 0;

  return (
    <div className="mx-auto max-w-6xl">
      <div className="mb-6 flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <div className="mb-2 inline-flex rounded-full border border-blue-700 bg-blue-950/40 px-3 py-1 text-xs font-medium text-blue-300">
            Nouveau module
          </div>
          <h1 className="text-2xl font-bold text-white">Preparation 2058-B / 2058-C</h1>
          <p className="mt-2 max-w-3xl text-sm text-slate-400">
            Preparez le brouillon des reports, deficits et du solde d&apos;IS a partir du
            dossier 2058-A deja saisi dans FiscIA Pro.
          </p>
        </div>

        <div className="flex gap-3">
          <Link
            href="/liasse"
            className="rounded-lg border border-slate-700 px-4 py-2 text-sm text-slate-300 transition hover:border-blue-500 hover:text-white"
          >
            Retour au 2058-A
          </Link>
          <Link
            href="/dashboard"
            className="rounded-lg border border-slate-700 px-4 py-2 text-sm text-slate-300 transition hover:border-blue-500 hover:text-white"
          >
            Tableau de bord
          </Link>
        </div>
      </div>

      {notice && (
        <div className="mb-4 rounded-lg border border-green-800 bg-green-900/20 p-3 text-sm text-green-300">
          {notice}
        </div>
      )}

      {error && (
        <div className="mb-4 rounded-lg border border-red-800 bg-red-900/20 p-3 text-sm text-red-300">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="rounded-lg border border-slate-800 bg-slate-900 p-6">
          <h2 className="mb-4 text-lg font-semibold text-blue-400">Base 2058-A</h2>
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            {LIASSE_FIELDS.map((field) => (
              <div key={field.key}>
                <label className="mb-1 block text-sm text-slate-400">{field.label}</label>
                <input
                  type={field.type}
                  step={field.type === "number" ? "0.01" : undefined}
                  value={liasseForm[field.key]}
                  onChange={(e) => updateLiasse(field.key, e.target.value)}
                  placeholder={"placeholder" in field ? field.placeholder : ""}
                  maxLength={"maxLength" in field ? field.maxLength : undefined}
                  className="w-full rounded border border-slate-700 bg-slate-800 px-3 py-2 text-white focus:border-blue-500 focus:outline-none"
                />
              </div>
            ))}
          </div>
        </div>

        <div className="rounded-lg border border-slate-800 bg-slate-900 p-6">
          <h2 className="mb-4 text-lg font-semibold text-blue-400">Parametres annexes</h2>
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            <div>
              <label className="mb-1 block text-sm text-slate-400">CA HT (EUR)</label>
              <input
                type="number"
                step="0.01"
                value={ca}
                onChange={(e) => setCa(e.target.value)}
                className="w-full rounded border border-slate-700 bg-slate-800 px-3 py-2 text-white focus:border-blue-500 focus:outline-none"
              />
            </div>

            <label className="mt-7 flex items-center gap-2 text-sm text-slate-300">
              <input
                type="checkbox"
                checked={capitalPP}
                onChange={(e) => setCapitalPP(e.target.checked)}
                className="rounded"
              />
              Capital detenu a 75% minimum par des personnes physiques
            </label>

            {ANNEX_FIELDS.map((field) => (
              <div key={field.key}>
                <label className="mb-1 block text-sm text-slate-400">{field.label}</label>
                <input
                  type="number"
                  step="0.01"
                  value={annexForm[field.key]}
                  onChange={(e) => updateAnnexe(field.key, e.target.value)}
                  className="w-full rounded border border-slate-700 bg-slate-800 px-3 py-2 text-white focus:border-blue-500 focus:outline-none"
                />
                <p className="mt-1 text-xs text-slate-500">{field.description}</p>
              </div>
            ))}
          </div>
        </div>

        <button
          type="submit"
          disabled={!canSubmit || submitting}
          className="w-full rounded-lg bg-blue-600 py-3 text-lg font-medium text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-blue-900/70"
        >
          {submitting ? "Preparation en cours..." : "Preparer 2058-B / 2058-C"}
        </button>
      </form>

      {result && <ResultPanel result={result} />}
    </div>
  );
}

function ResultPanel({ result }: { result: Liasse2058BCResult }) {
  const fmt = (n: number) =>
    new Intl.NumberFormat("fr-FR", { style: "currency", currency: "EUR" }).format(n);
  const table2058B = result.tableau_2058b;
  const table2058C = result.tableau_2058c;

  return (
    <div className="mt-8 space-y-6">
      <div className="rounded-lg border border-green-800 bg-slate-900 p-6">
        <h2 className="mb-4 text-lg font-semibold text-green-400">Synthese de preparation</h2>
        <p className="text-sm text-slate-300">
          Regime retenu : <span className="font-medium text-green-400">{result.regime}</span>
        </p>
        <div className="mt-4 grid grid-cols-1 gap-4 md:grid-cols-3">
          <MetricCard
            label="Base imposable"
            value={fmt(table2058C["base_imposable_is"])}
          />
          <MetricCard label="IS total" value={fmt(table2058C["is_total"])} />
          <MetricCard label="Solde a payer" value={fmt(table2058C["solde_a_payer"])} />
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <TableCard
          title="Brouillon 2058-B"
          rows={[
            ["Resultat fiscal brut", fmt(table2058B["resultat_fiscal_brut"])],
            ["Deficits ouverture", fmt(table2058B["deficits_reportables_ouverture"])],
            ["Deficits imputes", fmt(table2058B["deficits_imputes_exercice"])],
            ["Deficit exercice", fmt(table2058B["deficit_exercice"])],
            ["Deficits cloture", fmt(table2058B["deficits_reportables_cloture"])],
            ["MVLT ouverture", fmt(table2058B["moins_values_lt_ouverture"])],
            ["MVLT imputees", fmt(table2058B["moins_values_lt_imputees"])],
            ["MVLT cloture", fmt(table2058B["moins_values_lt_cloture"])],
            ["Base apres reports", fmt(table2058B["base_imposable_apres_reports"])],
          ]}
        />

        <TableCard
          title="Brouillon 2058-C"
          rows={[
            ["Base imposable IS", fmt(table2058C["base_imposable_is"])],
            ["Tranche 15%", fmt(table2058C["tranche_15pct"])],
            ["Tranche 25%", fmt(table2058C["tranche_25pct"])],
            ["IS total", fmt(table2058C["is_total"])],
            ["Contribution additionnelle", fmt(table2058C["contribution_sociale"])],
            ["Regularisations", fmt(table2058C["regularisations"])],
            ["Total du", fmt(table2058C["total_du"])],
            ["Acomptes verses", fmt(table2058C["acomptes_verses"])],
            ["Credits d'impot", fmt(table2058C["credits_impot"])],
            ["Total imputations", fmt(table2058C["total_imputations"])],
            ["Solde a payer", fmt(table2058C["solde_a_payer"])],
            ["Creance restante", fmt(table2058C["creance_restante"])],
          ]}
        />
      </div>

      <div className="rounded-lg border border-slate-800 bg-slate-900 p-6">
        <h3 className="mb-3 text-base font-semibold text-blue-300">Points d'attention</h3>
        <div className="space-y-2 text-sm text-slate-300">
          {result.notes.map((note) => (
            <div key={note} className="rounded bg-slate-800 px-3 py-2">
              {note}
            </div>
          ))}
        </div>
        <div className="mt-4 text-xs italic text-slate-500">{result.disclaimer}</div>
      </div>
    </div>
  );
}

function MetricCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg border border-slate-800 bg-slate-950/70 p-4">
      <div className="text-xs uppercase tracking-wide text-slate-500">{label}</div>
      <div className="mt-2 text-xl font-bold text-white">{value}</div>
    </div>
  );
}

function TableCard({ title, rows }: { title: string; rows: Array<[string, string]> }) {
  return (
    <div className="rounded-lg border border-slate-800 bg-slate-900 p-6">
      <h3 className="mb-4 text-lg font-semibold text-blue-300">{title}</h3>
      <div className="space-y-2">
        {rows.map(([label, value]) => (
          <div
            key={label}
            className="flex items-center justify-between rounded bg-slate-800 px-3 py-2 text-sm"
          >
            <span className="text-slate-400">{label}</span>
            <span className="font-mono text-white">{value}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
