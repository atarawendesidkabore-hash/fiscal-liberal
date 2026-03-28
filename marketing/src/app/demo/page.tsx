"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Section, SectionHeader } from "@/components/section";

/* ─── IS Calculator Logic (client-side replica) ─── */

function calcIS(rf: number, ca: number, capitalPP: boolean) {
  const PME_THRESHOLD = 42500;
  const RATE_REDUCED = 0.15;
  const RATE_NORMAL = 0.25;

  const isPME = ca < 10_000_000 && capitalPP;
  let t15 = 0;
  let t25 = 0;

  if (isPME && rf > 0) {
    const base15 = Math.min(rf, PME_THRESHOLD);
    t15 = base15 * RATE_REDUCED;
    t25 = Math.max(0, rf - PME_THRESHOLD) * RATE_NORMAL;
  } else {
    t25 = Math.max(0, rf) * RATE_NORMAL;
  }

  const isTotal = t15 + t25;
  const acompte = isTotal / 4;
  const regime = isPME && rf > 0 ? "PME taux reduit (Art. 219-I-b)" : "Normal (Art. 219-I)";

  return { rf, isTotal, t15, t25, acompte, regime, isPME };
}

function fmt(n: number) {
  return new Intl.NumberFormat("fr-FR", {
    style: "currency",
    currency: "EUR",
    minimumFractionDigits: 2,
  }).format(n);
}

/* ─── Demo page ─── */

export default function DemoPage() {
  const router = useRouter();
  // IS Calculator state
  const [benefice, setBenefice] = useState(120000);
  const [isCompta, setIsCompta] = useState(10000);
  const [amendes, setAmendes] = useState(2000);
  const [interets, setInterets] = useState(3000);
  const [ca, setCa] = useState(5000000);
  const [capitalPP, setCapitalPP] = useState(true);

  // Email capture
  const [email, setEmail] = useState("");

  // Calculation
  const rfBrut = benefice + isCompta + amendes + interets;
  const result = calcIS(rfBrut, ca, capitalPP);

  // Comparison: manual vs FiscIA
  const manualMinutes = 45;
  const fisciaSeconds = 3;

  return (
    <>
      <Section className="bg-gradient-to-b from-primary-50 to-white pt-12">
        <SectionHeader
          eyebrow="Demo interactive"
          title="Testez FiscIA Pro en direct"
          subtitle="Modifiez les valeurs ci-dessous et observez le calcul IS en temps reel. Aucun compte requis."
        />
      </Section>

      {/* ── Live calculator ── */}
      <Section>
        <div className="grid lg:grid-cols-2 gap-12">
          {/* Input form */}
          <div>
            <h3 className="text-lg font-semibold mb-6">Donnees de la liasse 2058-A</h3>
            <div className="space-y-5">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">
                  Benefice comptable (ligne XN)
                </label>
                <div className="relative">
                  <input
                    type="number"
                    value={benefice}
                    onChange={(e) => setBenefice(Number(e.target.value))}
                    className="w-full rounded-lg border border-slate-300 px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                  />
                  <span className="absolute right-3 top-1/2 -translate-y-1/2 text-sm text-slate-400">EUR</span>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">
                  IS comptabilise en charges (WI) — Art. 213 CGI
                </label>
                <div className="relative">
                  <input
                    type="number"
                    value={isCompta}
                    onChange={(e) => setIsCompta(Number(e.target.value))}
                    className="w-full rounded-lg border border-slate-300 px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                  />
                  <span className="absolute right-3 top-1/2 -translate-y-1/2 text-sm text-slate-400">EUR</span>
                </div>
                <p className="text-xs text-red-500 mt-1">+ Reintegration obligatoire</p>
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">
                  Amendes et penalites (WG) — Art. 39-2 CGI
                </label>
                <div className="relative">
                  <input
                    type="number"
                    value={amendes}
                    onChange={(e) => setAmendes(Number(e.target.value))}
                    className="w-full rounded-lg border border-slate-300 px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                  />
                  <span className="absolute right-3 top-1/2 -translate-y-1/2 text-sm text-slate-400">EUR</span>
                </div>
                <p className="text-xs text-red-500 mt-1">+ Reintegration obligatoire</p>
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">
                  Interets excedentaires CC (WM) — Art. 212 CGI
                </label>
                <div className="relative">
                  <input
                    type="number"
                    value={interets}
                    onChange={(e) => setInterets(Number(e.target.value))}
                    className="w-full rounded-lg border border-slate-300 px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                  />
                  <span className="absolute right-3 top-1/2 -translate-y-1/2 text-sm text-slate-400">EUR</span>
                </div>
                <p className="text-xs text-red-500 mt-1">+ Reintegration obligatoire</p>
              </div>

              <hr className="border-slate-200" />

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">
                  Chiffre d&apos;affaires HT
                </label>
                <div className="relative">
                  <input
                    type="number"
                    value={ca}
                    onChange={(e) => setCa(Number(e.target.value))}
                    className="w-full rounded-lg border border-slate-300 px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                  />
                  <span className="absolute right-3 top-1/2 -translate-y-1/2 text-sm text-slate-400">EUR</span>
                </div>
              </div>

              <div className="flex items-center gap-3">
                <input
                  type="checkbox"
                  id="capitalPP"
                  checked={capitalPP}
                  onChange={(e) => setCapitalPP(e.target.checked)}
                  className="h-4 w-4 rounded border-slate-300 text-primary-600 focus:ring-primary-500"
                />
                <label htmlFor="capitalPP" className="text-sm text-slate-700">
                  Capital detenu &ge; 75% par des personnes physiques
                </label>
              </div>
            </div>
          </div>

          {/* Results */}
          <div>
            <h3 className="text-lg font-semibold mb-6">Resultat IS — Exercice 2024</h3>

            <div className="rounded-xl border border-slate-200 bg-slate-50 overflow-hidden">
              {/* Regime badge */}
              <div className={`px-6 py-3 text-sm font-semibold ${result.isPME ? "bg-green-100 text-green-800" : "bg-slate-200 text-slate-700"}`}>
                {result.regime}
              </div>

              <div className="p-6 space-y-4">
                {/* RF brut */}
                <div className="flex justify-between text-sm">
                  <span className="text-slate-500">Resultat fiscal brut</span>
                  <span className="font-mono font-semibold">{fmt(result.rf)}</span>
                </div>

                <hr className="border-slate-200" />

                {/* Tranches */}
                {result.isPME && result.t15 > 0 && (
                  <div className="flex justify-between text-sm">
                    <span className="text-slate-500">
                      Tranche 15% (42 500 EUR)
                    </span>
                    <span className="font-mono text-green-600">{fmt(result.t15)}</span>
                  </div>
                )}
                <div className="flex justify-between text-sm">
                  <span className="text-slate-500">
                    Tranche 25% ({fmt(Math.max(0, result.rf - (result.isPME ? 42500 : 0)))})
                  </span>
                  <span className="font-mono">{fmt(result.t25)}</span>
                </div>

                <hr className="border-slate-200" />

                {/* IS total */}
                <div className="flex justify-between items-center">
                  <span className="text-lg font-bold">IS TOTAL DU</span>
                  <span className="text-2xl font-bold text-primary-600 font-mono">
                    {fmt(result.isTotal)}
                  </span>
                </div>

                {/* Acomptes */}
                <div className="bg-white rounded-lg border border-slate-200 p-4">
                  <p className="text-sm font-medium text-slate-700 mb-2">Acomptes trimestriels</p>
                  <div className="grid grid-cols-2 gap-2">
                    {["15/03", "15/06", "15/09", "15/12"].map((date) => (
                      <div key={date} className="flex justify-between text-xs bg-slate-50 rounded px-3 py-2">
                        <span className="text-slate-500">{date}</span>
                        <span className="font-mono">{fmt(result.acompte)}</span>
                      </div>
                    ))}
                  </div>
                </div>

                <p className="text-xs text-slate-400 italic">
                  Reponse indicative. Toute decision fiscale engageante necessite l&apos;analyse
                  personnalisee d&apos;un professionnel qualifie.
                </p>
              </div>
            </div>

            {/* Speed comparison */}
            <div className="mt-6 rounded-xl border border-slate-200 bg-white p-6">
              <h4 className="text-sm font-semibold text-slate-900 mb-4">Comparaison de temps</h4>
              <div className="space-y-3">
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-slate-500">Calcul manuel</span>
                    <span className="font-semibold text-red-600">{manualMinutes} minutes</span>
                  </div>
                  <div className="h-3 bg-slate-100 rounded-full overflow-hidden">
                    <div className="h-full bg-red-400 rounded-full" style={{ width: "100%" }} />
                  </div>
                </div>
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-slate-500">FiscIA Pro</span>
                    <span className="font-semibold text-green-600">{fisciaSeconds} secondes</span>
                  </div>
                  <div className="h-3 bg-slate-100 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-green-400 rounded-full"
                      style={{ width: `${(fisciaSeconds / 60 / manualMinutes) * 100}%`, minWidth: "8px" }}
                    />
                  </div>
                </div>
              </div>
              <p className="mt-3 text-sm text-slate-500">
                <strong className="text-green-600">{Math.round(manualMinutes * 60 / fisciaSeconds)}x plus rapide</strong>{" "}
                que le calcul manuel
              </p>
            </div>
          </div>
        </div>
      </Section>

      {/* ── Email capture ── */}
      <Section className="bg-primary-600" dark>
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="text-3xl font-bold text-white mb-4">
            Acces complet pendant 14 jours
          </h2>
          <p className="text-primary-100 mb-8">
            La demo ci-dessus ne montre qu&apos;une fraction des capacites de FiscIA Pro.
            Creez un compte gratuit pour acceder a l&apos;IA fiscale, la recherche CGI
            et l&apos;automatisation complete de la 2058-A.
          </p>

          <form
            onSubmit={(e) => {
              e.preventDefault();
              const query = email.trim()
                ? `?email=${encodeURIComponent(email.trim())}`
                : "";
              router.push(`/register${query}`);
            }}
            className="flex flex-col sm:flex-row gap-3 max-w-md mx-auto"
          >
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="votre@email-pro.fr"
              required
              className="flex-1 rounded-lg px-4 py-3 text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-white"
            />
            <button
              type="submit"
              className="rounded-lg bg-white px-6 py-3 text-sm font-semibold text-primary-700 hover:bg-primary-50 transition-colors whitespace-nowrap"
            >
              Creer mon compte
            </button>
          </form>

          <p className="mt-4 text-xs text-primary-300">
            Sans carte bancaire. Vous serez redirige vers l'inscription complete.
          </p>
          <p className="mt-3 text-sm text-primary-100">
            Deja un compte ?{" "}
            <Link href="/login" className="font-semibold text-white underline decoration-white/40 underline-offset-4">
              Connectez-vous ici
            </Link>
          </p>
        </div>
      </Section>
    </>
  );
}
