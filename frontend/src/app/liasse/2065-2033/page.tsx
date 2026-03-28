"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useRef, useState } from "react";
import ProtectedRoute from "@/components/protected-route";
import {
  get2065ImportFieldLabel,
  parseImported2065File,
  type ParsedLiasse2065Import,
} from "@/lib/liasse-2065-import";

const SAMPLE_IMPORT_FILES = [
  { href: "/examples/fiscia-2065-2033-demo.json", label: "Exemple JSON" },
  { href: "/examples/fiscia-2065-2033-demo.csv", label: "Exemple CSV" },
  { href: "/examples/fiscia-2065-2033-demo.txt", label: "Exemple TXT" },
  { href: "/examples/fiscia-2065-2033-demo.xlsx", label: "Exemple Excel" },
] as const;

const COMPANY_FIELDS = [
  { key: "siren", label: "SIREN", type: "text", placeholder: "123456789", maxLength: 9 },
  { key: "denomination", label: "Denomination", type: "text", placeholder: "Cabinet Atlas Fiscal" },
  { key: "exercice_ouvert", label: "Exercice ouvert le", type: "date" },
  { key: "exercice_clos", label: "Exercice clos le", type: "date" },
  { key: "ca_ht", label: "CA HT (EUR)", type: "number" },
  { key: "capital_social", label: "Capital social (EUR)", type: "number" },
  { key: "effectif_moyen", label: "Effectif moyen", type: "number" },
] as const;

const PNL_FIELDS = [
  { key: "resultat_comptable", label: "Resultat comptable (EUR)" },
  { key: "achats_marchandises", label: "Achats de marchandises (EUR)" },
  { key: "charges_externes", label: "Charges externes (EUR)" },
  { key: "impots_taxes", label: "Impots et taxes (EUR)" },
  { key: "salaires", label: "Salaires (EUR)" },
  { key: "charges_sociales", label: "Charges sociales (EUR)" },
  { key: "dotations_amortissements", label: "Dotations aux amortissements (EUR)" },
] as const;

const TAX_FIELDS = [
  { key: "reintegrations", label: "Reintegrations fiscales (EUR)" },
  { key: "deductions", label: "Deductions fiscales (EUR)" },
  { key: "deficits_anterieurs", label: "Deficits anterieurs imputables (EUR)" },
] as const;

type FormData = Record<string, string>;

export default function Liasse2065Page() {
  return (
    <ProtectedRoute>
      <Liasse2065Form />
    </ProtectedRoute>
  );
}

function Liasse2065Form() {
  const router = useRouter();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const initial: FormData = {};
  [...COMPANY_FIELDS, ...PNL_FIELDS, ...TAX_FIELDS].forEach((field) => {
    initial[field.key] = "";
  });
  initial.exercice_ouvert = "2024-01-01";
  initial.exercice_clos = "2024-12-31";
  initial.ca_ht = "3500000";
  initial.capital_social = "50000";
  initial.effectif_moyen = "12";

  const [form, setForm] = useState<FormData>(initial);
  const [regimeImposition, setRegimeImposition] = useState("reel_simplifie");
  const [capitalPP, setCapitalPP] = useState(true);
  const [capitalLibere, setCapitalLibere] = useState(true);
  const [dragActive, setDragActive] = useState(false);
  const [importing, setImporting] = useState(false);
  const [importNotice, setImportNotice] = useState("");
  const [importError, setImportError] = useState("");

  function update(key: string, value: string) {
    setForm((prev) => ({ ...prev, [key]: value }));
  }

  function parseNumber(value: string) {
    const parsed = Number(value);
    return Number.isFinite(parsed) ? parsed : 0;
  }

  const caHT = parseNumber(form.ca_ht);
  const resultatComptable = parseNumber(form.resultat_comptable);
  const reintegrations = parseNumber(form.reintegrations);
  const deductions = parseNumber(form.deductions);
  const deficitsAnterieurs = parseNumber(form.deficits_anterieurs);
  const resultatFiscalAvantDeficits = resultatComptable + reintegrations - deductions;
  const resultatFiscalApresDeficits = resultatFiscalAvantDeficits - deficitsAnterieurs;

  const annexesAttendues =
    regimeImposition === "reel_normal"
      ? ["2065-SD", "2050 a 2057", "2058-A a 2058-C", "2059-A a 2059-G"]
      : ["2065-SD", "2033-A a 2033-G", "2058-A a 2058-C", "2059-A/B"];

  const alerts: string[] = [];
  if (form.siren && form.siren.length !== 9) {
    alerts.push("Le SIREN doit contenir 9 chiffres.");
  }
  if (!form.denomination.trim()) {
    alerts.push("Ajoutez une denomination pour preparer la 2065.");
  }
  if (form.exercice_ouvert && form.exercice_clos && form.exercice_ouvert > form.exercice_clos) {
    alerts.push("La date d'ouverture doit preceder la date de cloture.");
  }
  if (caHT <= 0) {
    alerts.push("Le CA HT doit etre renseigne pour cadrer la liasse.");
  }
  if (!capitalLibere) {
    alerts.push("Capital non entierement libere : pensez a verifier les consequences fiscales.");
  }

  function applyImportedValues(imported: ParsedLiasse2065Import) {
    setForm((prev) => ({ ...prev, ...imported.importedFormValues }));

    if (imported.importedFormValues.regime_imposition) {
      setRegimeImposition(imported.importedFormValues.regime_imposition);
    }
    if (typeof imported.capitalPP === "boolean") {
      setCapitalPP(imported.capitalPP);
    }
    if (typeof imported.capitalLibere === "boolean") {
      setCapitalLibere(imported.capitalLibere);
    }

    const preview = imported.matchedFieldKeys
      .slice(0, 4)
      .map((field) => get2065ImportFieldLabel(field))
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
      const imported = await parseImported2065File(file);
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

  function handleDownloadJson() {
    const payload = {
      siren: form.siren,
      denomination: form.denomination,
      exercice_ouvert: form.exercice_ouvert,
      exercice_clos: form.exercice_clos,
      regime_imposition: regimeImposition,
      ca_ht: caHT,
      capital_social: parseNumber(form.capital_social),
      effectif_moyen: parseNumber(form.effectif_moyen),
      capital_pp: capitalPP,
      capital_libere: capitalLibere,
      resultat_comptable: resultatComptable,
      achats_marchandises: parseNumber(form.achats_marchandises),
      charges_externes: parseNumber(form.charges_externes),
      impots_taxes: parseNumber(form.impots_taxes),
      salaires: parseNumber(form.salaires),
      charges_sociales: parseNumber(form.charges_sociales),
      dotations_amortissements: parseNumber(form.dotations_amortissements),
      reintegrations,
      deductions,
      deficits_anterieurs: deficitsAnterieurs,
    };

    const blob = new Blob([JSON.stringify(payload, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = "fiscia-2065-2033-draft.json";
    anchor.click();
    URL.revokeObjectURL(url);
  }

  function handleContinueTo2058A() {
    const payload = {
      siren: form.siren,
      exercice_clos: form.exercice_clos,
      benefice_comptable: resultatComptable > 0 ? String(resultatComptable) : "",
      perte_comptable: resultatComptable < 0 ? String(Math.abs(resultatComptable)) : "",
      ca: form.ca_ht,
      capital_pp: capitalPP,
      source: "2065-2033",
    };

    localStorage.setItem("fiscia_2058a_prefill", JSON.stringify(payload));
    router.push("/liasse");
  }

  const canContinueTo2058A =
    form.siren.trim().length === 9 &&
    Boolean(form.exercice_clos) &&
    Boolean(form.resultat_comptable) &&
    caHT > 0;

  const fmt = (value: number) =>
    new Intl.NumberFormat("fr-FR", { style: "currency", currency: "EUR" }).format(value);

  return (
    <div className="max-w-6xl mx-auto">
      <div className="mb-6 flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <div className="mb-2 inline-flex rounded-full border border-blue-700 bg-blue-900/30 px-3 py-1 text-xs font-medium text-blue-300">
            Beta roadmap en cours
          </div>
          <h1 className="text-2xl font-bold">Preparation 2065 + 2033</h1>
          <p className="mt-2 max-w-3xl text-sm text-slate-400">
            Commencez votre dossier IS, importez un fichier cabinet puis basculez vers la
            liasse 2058-A pour finaliser les retraitements fiscaux.
          </p>
        </div>

        <div className="flex gap-3">
          <Link
            href="/dashboard"
            className="rounded-lg border border-slate-700 px-4 py-2 text-sm text-slate-300 transition hover:border-slate-500 hover:text-white"
          >
            Tableau de bord
          </Link>
          <Link
            href="/liasse"
            className="rounded-lg border border-slate-700 px-4 py-2 text-sm text-slate-300 transition hover:border-blue-400 hover:text-blue-300"
          >
            Aller au 2058-A
          </Link>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-4 mb-6">
        <SummaryCard label="CA HT" value={fmt(caHT)} tone="blue" />
        <SummaryCard
          label="Resultat comptable"
          value={fmt(resultatComptable)}
          tone={resultatComptable >= 0 ? "green" : "amber"}
        />
        <SummaryCard
          label="RF avant deficits"
          value={fmt(resultatFiscalAvantDeficits)}
          tone={resultatFiscalAvantDeficits >= 0 ? "green" : "amber"}
        />
        <SummaryCard
          label="RF apres deficits"
          value={fmt(resultatFiscalApresDeficits)}
          tone={resultatFiscalApresDeficits >= 0 ? "green" : "amber"}
        />
      </div>

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
              Import 2065 / 2033
            </p>
            <h2 className="mt-1 text-lg font-semibold text-white">
              Glissez un export cabinet pour pre-remplir le dossier
            </h2>
            <p className="mt-2 text-sm text-slate-400">
              Formats acceptes : JSON, CSV, TXT et Excel. Les champs reconnus
              remplissent automatiquement la 2065, les indicateurs 2033 et les options
              capitalistiques.
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
            <button
              type="button"
              onClick={handleDownloadJson}
              className="rounded-lg border border-slate-600 px-4 py-2 text-sm font-medium text-slate-200 transition hover:border-slate-400 hover:text-white"
            >
              Exporter le brouillon JSON
            </button>
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
          accept=".json,.csv,.txt,.xlsx,.xls,.xlsm,.xlsb"
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

      <div className="grid grid-cols-1 gap-6 xl:grid-cols-[1.7fr_0.9fr]">
        <div className="space-y-6">
          <section className="rounded-lg border border-slate-800 bg-slate-900 p-6">
            <div className="mb-4 flex items-center justify-between">
              <h2 className="text-lg font-semibold text-blue-400">Bloc 2065</h2>
              <select
                value={regimeImposition}
                onChange={(e) => setRegimeImposition(e.target.value)}
                className="rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-white focus:border-blue-500 focus:outline-none"
              >
                <option value="reel_simplifie">Regime reel simplifie</option>
                <option value="reel_normal">Regime reel normal</option>
              </select>
            </div>

            <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
              {COMPANY_FIELDS.map((field) => (
                <div key={field.key}>
                  <label className="mb-1 block text-sm text-slate-400">{field.label}</label>
                  <input
                    type={field.type}
                    value={form[field.key]}
                    onChange={(e) => update(field.key, e.target.value)}
                    placeholder={"placeholder" in field ? field.placeholder : ""}
                    maxLength={"maxLength" in field ? field.maxLength : undefined}
                    className="w-full rounded border border-slate-700 bg-slate-800 px-3 py-2 text-white focus:border-blue-500 focus:outline-none"
                  />
                </div>
              ))}
            </div>

            <div className="mt-4 grid grid-cols-1 gap-4 md:grid-cols-2">
              <CheckboxField
                id="capital_pp_2065"
                label="Capital >= 75% personnes physiques"
                checked={capitalPP}
                onChange={setCapitalPP}
              />
              <CheckboxField
                id="capital_libere_2065"
                label="Capital entierement libere"
                checked={capitalLibere}
                onChange={setCapitalLibere}
              />
            </div>
          </section>

          <section className="rounded-lg border border-slate-800 bg-slate-900 p-6">
            <h2 className="mb-4 text-lg font-semibold text-blue-400">Bloc 2033 - compte de resultat</h2>
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
              {PNL_FIELDS.map((field) => (
                <div key={field.key}>
                  <label className="mb-1 block text-sm text-slate-400">{field.label}</label>
                  <input
                    type="number"
                    step="0.01"
                    value={form[field.key]}
                    onChange={(e) => update(field.key, e.target.value)}
                    className="w-full rounded border border-slate-700 bg-slate-800 px-3 py-2 text-white focus:border-blue-500 focus:outline-none"
                    placeholder="0"
                  />
                </div>
              ))}
            </div>
          </section>

          <section className="rounded-lg border border-slate-800 bg-slate-900 p-6">
            <h2 className="mb-4 text-lg font-semibold text-blue-400">Pont fiscal vers 2058-A</h2>
            <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
              {TAX_FIELDS.map((field) => (
                <div key={field.key}>
                  <label className="mb-1 block text-sm text-slate-400">{field.label}</label>
                  <input
                    type="number"
                    step="0.01"
                    value={form[field.key]}
                    onChange={(e) => update(field.key, e.target.value)}
                    className="w-full rounded border border-slate-700 bg-slate-800 px-3 py-2 text-white focus:border-blue-500 focus:outline-none"
                    placeholder="0"
                  />
                </div>
              ))}
            </div>

            <div className="mt-4 flex flex-col gap-3 md:flex-row">
              <button
                type="button"
                onClick={handleContinueTo2058A}
                disabled={!canContinueTo2058A}
                className="rounded-lg bg-blue-600 px-4 py-3 text-sm font-medium text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-blue-900"
              >
                Continuer vers la liasse 2058-A
              </button>
              <p className="text-sm text-slate-500">
                Ce bouton pre-remplit le 2058-A avec le SIREN, la cloture, le resultat
                comptable, le CA et l'option capital PP.
              </p>
            </div>
          </section>
        </div>

        <aside className="space-y-6">
          <section className="rounded-lg border border-slate-800 bg-slate-900 p-6">
            <h2 className="mb-4 text-lg font-semibold text-white">Annexes attendues</h2>
            <div className="flex flex-wrap gap-2">
              {annexesAttendues.map((annexe) => (
                <span
                  key={annexe}
                  className="rounded-full border border-slate-700 bg-slate-800 px-3 py-1 text-xs text-slate-300"
                >
                  {annexe}
                </span>
              ))}
            </div>
          </section>

          <section className="rounded-lg border border-slate-800 bg-slate-900 p-6">
            <h2 className="mb-4 text-lg font-semibold text-white">Controle rapide</h2>
            {alerts.length === 0 ? (
              <div className="rounded-lg border border-green-800 bg-green-900/20 p-3 text-sm text-green-300">
                Dossier coherent pour une premiere preparation 2065/2033.
              </div>
            ) : (
              <div className="space-y-2">
                {alerts.map((alert) => (
                  <div
                    key={alert}
                    className="rounded-lg border border-amber-700 bg-amber-900/20 p-3 text-sm text-amber-200"
                  >
                    {alert}
                  </div>
                ))}
              </div>
            )}
          </section>

          <section className="rounded-lg border border-slate-800 bg-slate-900 p-6">
            <h2 className="mb-4 text-lg font-semibold text-white">Lecture fiscale</h2>
            <div className="space-y-3 text-sm text-slate-300">
              <MetricRow label="Resultat comptable" value={fmt(resultatComptable)} />
              <MetricRow label="+ Reintegrations" value={fmt(reintegrations)} />
              <MetricRow label="- Deductions" value={fmt(deductions)} />
              <MetricRow
                label="RF avant deficits"
                value={fmt(resultatFiscalAvantDeficits)}
                accent="text-blue-400"
              />
              <MetricRow label="- Deficits anterieurs" value={fmt(deficitsAnterieurs)} />
              <MetricRow
                label="RF apres deficits"
                value={fmt(resultatFiscalApresDeficits)}
                accent={
                  resultatFiscalApresDeficits >= 0 ? "text-green-400" : "text-amber-300"
                }
              />
            </div>
          </section>
        </aside>
      </div>
    </div>
  );
}

function SummaryCard({
  label,
  value,
  tone,
}: {
  label: string;
  value: string;
  tone: "blue" | "green" | "amber";
}) {
  const toneClass =
    tone === "green" ? "text-green-400" : tone === "amber" ? "text-amber-300" : "text-blue-400";

  return (
    <div className="rounded-lg border border-slate-800 bg-slate-900 p-5">
      <div className="text-xs uppercase text-slate-500">{label}</div>
      <div className={`mt-2 text-2xl font-bold ${toneClass}`}>{value}</div>
    </div>
  );
}

function CheckboxField({
  id,
  label,
  checked,
  onChange,
}: {
  id: string;
  label: string;
  checked: boolean;
  onChange: (next: boolean) => void;
}) {
  return (
    <div className="flex items-center gap-3 rounded-lg border border-slate-800 bg-slate-950/50 px-4 py-3">
      <input
        id={id}
        type="checkbox"
        checked={checked}
        onChange={(e) => onChange(e.target.checked)}
        className="rounded"
      />
      <label htmlFor={id} className="text-sm text-slate-300">
        {label}
      </label>
    </div>
  );
}

function MetricRow({
  label,
  value,
  accent,
}: {
  label: string;
  value: string;
  accent?: string;
}) {
  return (
    <div className="flex items-center justify-between rounded-lg bg-slate-800 px-3 py-2">
      <span className="text-slate-400">{label}</span>
      <span className={`font-mono ${accent || "text-white"}`}>{value}</span>
    </div>
  );
}
