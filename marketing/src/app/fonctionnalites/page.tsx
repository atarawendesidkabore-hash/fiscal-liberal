import type { Metadata } from "next";
import Link from "next/link";
import { Section, SectionHeader } from "@/components/section";
import { CTABanner } from "@/components/cta-banner";

export const metadata: Metadata = {
  title: "Fonctionnalites",
  description:
    "Calcul IS automatise, liasse 2058-A intelligente, verification Art. 145, recherche CGI instantanee, audit trail et IA locale.",
};

/* ─── Feature deep-dive sections ─── */

const FEATURES = [
  {
    id: "calcul-is",
    eyebrow: "Moteur de calcul",
    title: "Calcul IS — Art. 219 CGI, LFI 2024",
    description:
      "Entrez le chiffre d'affaires et les conditions de detentention du capital. FiscIA determine automatiquement le regime applicable (taux normal 25% ou taux reduit PME 15%) et produit le detail des tranches, l'IS total et les acomptes trimestriels.",
    details: [
      "Taux normal 25% applique a l'integralite du benefice",
      "Taux reduit PME 15% sur les premiers 42 500 EUR si CA HT < 10 M EUR et capital >= 75% PP",
      "Calcul automatique des 4 acomptes trimestriels (15/03, 15/06, 15/09, 15/12)",
      "Gestion du deficit reportable (Art. 209 I — illimite avec plafond 50%)",
      "Report en arriere (Art. 220 quinquies — plafonnd 1 M EUR)",
    ],
    codeExample: `POST /v2/liasse
{
  "liasse": {
    "siren": "987654321",
    "exercice_clos": "2024-12-31",
    "benefice_comptable": 120000,
    "wi_is_comptabilise": 10000,
    "wg_amendes_penalites": 2000
  },
  "ca": 5000000,
  "capital_pp": true
}

// Reponse:
{
  "rf_brut": 132000,
  "is_total": 28875,
  "regime": "PME taux reduit (Art. 219-I-b)",
  "acompte_trimestriel": 7218.75
}`,
  },
  {
    id: "liasse-2058a",
    eyebrow: "Automatisation",
    title: "Liasse 2058-A intelligente",
    description:
      "FiscIA traite chaque ligne de la liasse 2058-A avec les references CGI exactes. Reintegrations et deductions extracomptables sont calculees automatiquement avec verification des conditions d'application.",
    details: [
      "WI — IS comptabilise en charges : reintegration systematique (Art. 213 CGI)",
      "WG — Amendes et penalites fiscales : reintegration (Art. 39-2 CGI)",
      "WM — Interets excedentaires CC associes (Art. 39-1-3 + 212 CGI)",
      "WV — Dividendes regime mere-filiale : deduction (Art. 145 + 216 CGI)",
      "WN — Quote-part 5% frais et charges sur dividendes",
      "L8 — Quote-part 12% PV LT titres participation",
      "5 guardrails automatiques verifiant chaque sortie",
    ],
    codeExample: null,
  },
  {
    id: "art-145",
    eyebrow: "Verification",
    title: "Art. 145 CGI — Regime mere-filiale",
    description:
      "Verification automatique des 6 conditions cumulatives du regime mere-filiale. Si une seule condition manque, le systeme bloque l'application du regime et alerte le fiscaliste.",
    details: [
      "Condition 1 : Participation >= 5% du capital social",
      "Condition 2 : Detention >= 2 ans",
      "Condition 3 : Titres nominatifs",
      "Condition 4 : Pleine propriete (non demembres)",
      "Condition 5 : Filiale soumise a l'IS de plein droit ou sur option",
      "Condition 6 : Filiale hors paradis fiscal / ETNC",
      "Calcul automatique de la deduction WV et de la QP 5% WN",
    ],
    codeExample: `POST /mere
{
  "pct_capital": 7.0,
  "annees_detention": 3,
  "nominatif": true,
  "pleine_propriete": true,
  "filiale_is": true,
  "paradis_fiscal": false,
  "dividende_brut": 50000
}

// Reponse:
{
  "eligible": true,
  "conditions": { "1": true, "2": true, ... },
  "deduction_wv": 50000,
  "reintegration_wn_qp5": 2500,
  "impact_rf_net": -47500
}`,
  },
  {
    id: "recherche-cgi",
    eyebrow: "Recherche",
    title: "Recherche CGI instantanee",
    description:
      "Trouvez n'importe quel article du Code General des Impots en moins de 2 secondes. Recherche par numero d'article, par mot-cle ou par thematique fiscale. Chaque resultat inclut le texte complet, la version applicable et le score de pertinence.",
    details: [
      "Recherche fuzzy par mot-cle (ex: 'taux reduit PME')",
      "Recherche exacte par numero d'article (ex: '219')",
      "Score de pertinence pour chaque resultat",
      "Version LFI 2024 integree",
      "Mise a jour automatique lors des changements legislatifs",
    ],
    codeExample: null,
  },
  {
    id: "assistant-ia",
    eyebrow: "Intelligence artificielle",
    title: "Assistant IA fiscal",
    description:
      "Posez des questions fiscales en langage naturel. L'IA repond avec les articles CGI exacts, les calculs detailles et les mises en garde necessaires. Optionnellement hebergeable en local (zero donnees transmises).",
    details: [
      "4 modes specialises : IS, Liasse, Mere-filiale, General",
      "Chaque reponse cite les articles CGI applicables",
      "Disclaimer automatique : 'Reponse indicative, validation professionnelle requise'",
      "IA locale optionnelle via Ollama (modele Mistral 7B fine-tune)",
      "Logs d'utilisation et audit trail complets",
    ],
    codeExample: `POST /v2/ai/explain
{
  "prompt": "Comment traiter les dividendes recus d'une filiale a 7% en regime mere-filiale ?",
  "mode": "mere"
}

// Reponse:
{
  "response": "Les 6 conditions de l'Art. 145 CGI sont ...",
  "mode": "mere",
  "model": "fiscia-fiscal-is-v3",
  "disclaimer": "Reponse indicative generee par IA locale."
}`,
  },
  {
    id: "audit-trail",
    eyebrow: "Conformite",
    title: "Audit trail et traabilite",
    description:
      "Chaque calcul, chaque recherche, chaque modification est tracee et horodatee. Exportez l'historique complet pour vos audits ou vos obligations de documentation fiscale.",
    details: [
      "Chaque operation enregistree avec user, IP, timestamp",
      "Export GDPR (Art. 20) : toutes vos donnees en un clic",
      "Droit a l'effacement (Art. 17) : suppression complete sur demande",
      "Suivi des consentements (data_processing, marketing, analytics)",
      "Politique de retention configurable (defaut : 3 ans)",
      "Role-based access control (Admin, Fiscaliste, Client)",
    ],
    codeExample: null,
  },
];

export default function FonctionnalitesPage() {
  return (
    <>
      <Section className="bg-gradient-to-b from-primary-50 to-white pt-12">
        <SectionHeader
          eyebrow="Fonctionnalites"
          title="Chaque outil dont un fiscaliste a besoin"
          subtitle="De la saisie de la liasse au calcul final, en passant par la recherche CGI et l'IA fiscale."
        />
      </Section>

      {FEATURES.map((feature, i) => (
        <Section
          key={feature.id}
          id={feature.id}
          className={i % 2 === 0 ? "bg-white" : "bg-slate-50"}
        >
          <div className="grid md:grid-cols-2 gap-16 items-start">
            {/* Text */}
            <div className={i % 2 !== 0 ? "md:order-2" : ""}>
              <p className="text-sm font-semibold uppercase tracking-wider text-primary-600 mb-2">
                {feature.eyebrow}
              </p>
              <h2 className="text-2xl md:text-3xl font-bold tracking-tight mb-4">
                {feature.title}
              </h2>
              <p className="text-slate-600 leading-relaxed mb-6">
                {feature.description}
              </p>
              <ul className="space-y-3">
                {feature.details.map((d) => (
                  <li key={d} className="flex items-start gap-2 text-sm text-slate-600">
                    <svg className="h-5 w-5 text-green-500 shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
                    </svg>
                    {d}
                  </li>
                ))}
              </ul>
            </div>

            {/* Code example or illustration */}
            <div className={i % 2 !== 0 ? "md:order-1" : ""}>
              {feature.codeExample ? (
                <div className="rounded-xl border border-slate-200 bg-slate-950 shadow-lg overflow-hidden">
                  <div className="flex items-center gap-2 px-4 py-3 bg-slate-900 border-b border-slate-800">
                    <div className="h-2.5 w-2.5 rounded-full bg-red-500" />
                    <div className="h-2.5 w-2.5 rounded-full bg-yellow-500" />
                    <div className="h-2.5 w-2.5 rounded-full bg-green-500" />
                    <span className="ml-2 text-xs text-slate-500 font-mono">API Example</span>
                  </div>
                  <pre className="p-6 text-sm text-slate-300 overflow-x-auto font-mono leading-relaxed">
                    {feature.codeExample}
                  </pre>
                </div>
              ) : (
                <div className="rounded-xl bg-gradient-to-br from-primary-100 to-primary-50 border border-primary-200 p-12 flex items-center justify-center min-h-[300px]">
                  <div className="text-center">
                    <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-primary-600 mb-4">
                      <svg className="h-8 w-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.455 2.456L21.75 6l-1.036.259a3.375 3.375 0 00-2.455 2.456z" />
                      </svg>
                    </div>
                    <p className="text-lg font-semibold text-primary-900">{feature.title}</p>
                    <p className="text-sm text-primary-600 mt-1">Interface interactive dans l&apos;application</p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </Section>
      ))}

      {/* ── Quick navigation ── */}
      <Section className="bg-slate-900" dark>
        <SectionHeader
          eyebrow="Navigation rapide"
          title="Accedez directement a chaque fonctionnalite"
        />
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4 max-w-4xl mx-auto">
          {FEATURES.map((f) => (
            <Link
              key={f.id}
              href={`#${f.id}`}
              className="flex items-center gap-3 rounded-lg bg-slate-800 border border-slate-700 px-4 py-3 hover:bg-slate-700 transition-colors"
            >
              <svg className="h-5 w-5 text-primary-400 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 4.5L21 12m0 0l-7.5 7.5M21 12H3" />
              </svg>
              <span className="text-sm font-medium text-white">{f.title}</span>
            </Link>
          ))}
        </div>
      </Section>

      <CTABanner />
    </>
  );
}
