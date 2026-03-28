"use client";

import { useState } from "react";
import Link from "next/link";
import type { Metadata } from "next";
import { Section, SectionHeader } from "@/components/section";
import { CTABanner } from "@/components/cta-banner";

/* ─── Pricing tiers ─── */

const TIERS = [
  {
    name: "Starter",
    price: 29,
    period: "/mois",
    description: "Pour le fiscaliste independant",
    highlight: false,
    features: [
      "1 utilisateur",
      "50 calculs IS / mois",
      "Liasse 2058-A manuelle",
      "Recherche CGI illimitee",
      "Historique 90 jours",
      "Support email",
    ],
    excluded: [
      "Assistant IA",
      "Art. 145 automatique",
      "Export GDPR",
      "API access",
      "Multi-cabinet",
    ],
    cta: "Demarrer l'essai",
  },
  {
    name: "Pro",
    price: 79,
    period: "/mois",
    description: "Pour le cabinet de 1 a 5 associes",
    highlight: true,
    badge: "Le plus populaire",
    features: [
      "5 utilisateurs",
      "Calculs IS illimites",
      "Liasse 2058-A automatisee",
      "Recherche CGI illimitee",
      "Assistant IA fiscal",
      "Art. 145 automatique",
      "Historique illimite",
      "Export GDPR",
      "Support prioritaire",
    ],
    excluded: ["API access", "Multi-cabinet"],
    cta: "Choisir Pro",
  },
  {
    name: "Cabinet",
    price: 199,
    period: "/mois",
    description: "Pour les cabinets de 6 a 20 associes",
    highlight: false,
    features: [
      "20 utilisateurs",
      "Calculs IS illimites",
      "Liasse 2058-A automatisee",
      "Recherche CGI illimitee",
      "Assistant IA fiscal avance",
      "Art. 145 automatique",
      "Historique illimite",
      "Export GDPR complet",
      "API REST / webhook",
      "Multi-cabinet",
      "Onboarding dedie",
      "Support telephonique",
    ],
    excluded: [],
    cta: "Contacter les ventes",
  },
];

const COMPARISON_ROWS = [
  { feature: "Utilisateurs", starter: "1", pro: "5", cabinet: "20" },
  { feature: "Calculs IS / mois", starter: "50", pro: "Illimite", cabinet: "Illimite" },
  { feature: "Liasse 2058-A", starter: "Manuelle", pro: "Automatisee", cabinet: "Automatisee" },
  { feature: "Recherche CGI", starter: true, pro: true, cabinet: true },
  { feature: "Assistant IA fiscal", starter: false, pro: true, cabinet: true },
  { feature: "Art. 145 automatique", starter: false, pro: true, cabinet: true },
  { feature: "Historique", starter: "90 jours", pro: "Illimite", cabinet: "Illimite" },
  { feature: "Export GDPR", starter: false, pro: true, cabinet: true },
  { feature: "API REST", starter: false, pro: false, cabinet: true },
  { feature: "Multi-cabinet", starter: false, pro: false, cabinet: true },
  { feature: "Support", starter: "Email", pro: "Prioritaire", cabinet: "Telephonique" },
  { feature: "Onboarding", starter: "Docs", pro: "Webinar", cabinet: "Dedie" },
];

const FAQ = [
  {
    q: "Puis-je changer de formule a tout moment ?",
    a: "Oui, vous pouvez upgrader ou downgrader votre abonnement a tout moment. Le changement prend effet a la prochaine periode de facturation. Les calculs deja effectues restent accessibles.",
  },
  {
    q: "Y a-t-il un engagement de duree ?",
    a: "Non. Tous les abonnements sont mensuels, sans engagement. Nous proposons egalement une tarification annuelle avec 2 mois offerts (paiement annuel).",
  },
  {
    q: "Que se passe-t-il apres l'essai gratuit ?",
    a: "Apres 14 jours, votre compte passe en mode lecture seule. Vos donnees sont conservees 30 jours. Vous pouvez reactiver a tout moment en choisissant une formule.",
  },
  {
    q: "Les donnees de mes clients sont-elles en securite ?",
    a: "Absolument. Toutes les donnees sont hebergees en France (Scaleway Paris), chiffrees AES-256 au repos et TLS 1.3 en transit. Nous sommes conformes RGPD avec export et suppression des donnees a la demande.",
  },
  {
    q: "Proposez-vous des tarifs pour les grands cabinets ?",
    a: "Oui. Pour les cabinets de plus de 20 associes ou les groupes, contactez notre equipe commerciale pour un devis personnalise avec SLA et support dedie.",
  },
  {
    q: "L'IA locale signifie quoi exactement ?",
    a: "FiscIA Pro peut fonctionner avec un modele d'IA heberge directement sur votre serveur (via Ollama). Aucune donnee client ne quitte votre infrastructure. C'est une option de la formule Cabinet.",
  },
];

function Check() {
  return (
    <svg className="h-5 w-5 text-green-500 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
    </svg>
  );
}

function Cross() {
  return (
    <svg className="h-5 w-5 text-slate-300 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
    </svg>
  );
}

function CellValue({ val }: { val: boolean | string }) {
  if (val === true) return <Check />;
  if (val === false) return <Cross />;
  return <span className="text-sm text-slate-700">{val}</span>;
}

export default function TarificationPage() {
  const [annuel, setAnnuel] = useState(false);
  const [hoursPerWeek, setHoursPerWeek] = useState(3);
  const hourlyRate = 150;

  const annualSavings = hoursPerWeek * hourlyRate * 48;
  const monthlySavings = Math.round(annualSavings / 12);

  return (
    <>
      {/* ── Hero ── */}
      <Section className="bg-gradient-to-b from-primary-50 to-white pt-12">
        <SectionHeader
          eyebrow="Tarification"
          title="Simple, transparent, sans surprise"
          subtitle="14 jours d'essai gratuit sur toutes les formules. Sans carte bancaire."
        />

        {/* Toggle */}
        <div className="flex items-center justify-center gap-3 mb-12">
          <span className={`text-sm font-medium ${!annuel ? "text-slate-900" : "text-slate-400"}`}>
            Mensuel
          </span>
          <button
            onClick={() => setAnnuel(!annuel)}
            className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
              annuel ? "bg-primary-600" : "bg-slate-300"
            }`}
          >
            <span
              className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                annuel ? "translate-x-6" : "translate-x-1"
              }`}
            />
          </button>
          <span className={`text-sm font-medium ${annuel ? "text-slate-900" : "text-slate-400"}`}>
            Annuel <span className="text-green-600 font-semibold">(-17%)</span>
          </span>
        </div>

        {/* Pricing cards */}
        <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
          {TIERS.map((tier) => (
            <div
              key={tier.name}
              className={`rounded-2xl p-8 ${
                tier.highlight
                  ? "bg-primary-600 text-white ring-4 ring-primary-600 ring-offset-2 shadow-2xl relative"
                  : "bg-white border border-slate-200 shadow-sm"
              }`}
            >
              {tier.highlight && (
                <span className="absolute -top-3 left-1/2 -translate-x-1/2 rounded-full bg-yellow-400 px-3 py-0.5 text-xs font-bold text-yellow-900">
                  {(tier as { badge?: string }).badge}
                </span>
              )}
              <h3 className={`text-lg font-semibold ${tier.highlight ? "" : "text-slate-900"}`}>
                {tier.name}
              </h3>
              <p className={`mt-1 text-sm ${tier.highlight ? "text-primary-100" : "text-slate-500"}`}>
                {tier.description}
              </p>
              <div className="mt-6">
                <span className="text-4xl font-bold">
                  {annuel ? Math.round(tier.price * 10 / 12) : tier.price} EUR
                </span>
                <span className={`text-sm ${tier.highlight ? "text-primary-200" : "text-slate-400"}`}>
                  {tier.period}
                </span>
              </div>
              {annuel && (
                <p className={`mt-1 text-xs ${tier.highlight ? "text-primary-200" : "text-slate-400"}`}>
                  Facture {tier.price * 10} EUR/an
                </p>
              )}
              <Link
                href="/demo"
                className={`mt-6 block w-full rounded-lg py-2.5 text-center text-sm font-semibold transition-colors ${
                  tier.highlight
                    ? "bg-white text-primary-700 hover:bg-primary-50"
                    : "bg-primary-600 text-white hover:bg-primary-700"
                }`}
              >
                {tier.cta}
              </Link>
              <ul className="mt-6 space-y-3">
                {tier.features.map((f) => (
                  <li key={f} className="flex items-start gap-2 text-sm">
                    <svg
                      className={`h-5 w-5 shrink-0 ${tier.highlight ? "text-green-300" : "text-green-500"}`}
                      fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}
                    >
                      <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
                    </svg>
                    {f}
                  </li>
                ))}
                {tier.excluded.map((f) => (
                  <li key={f} className={`flex items-start gap-2 text-sm line-through ${
                    tier.highlight ? "text-primary-300" : "text-slate-300"
                  }`}>
                    <svg
                      className="h-5 w-5 shrink-0"
                      fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}
                    >
                      <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                    {f}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </Section>

      {/* ── Value calculator ── */}
      <Section className="bg-slate-50">
        <SectionHeader
          eyebrow="Calculez votre ROI"
          title="Combien economisez-vous avec FiscIA Pro ?"
        />
        <div className="max-w-xl mx-auto bg-white rounded-xl border border-slate-200 p-8">
          <label className="block text-sm font-medium text-slate-700 mb-2">
            Heures perdues par semaine sur la recherche CGI et les calculs manuels
          </label>
          <input
            type="range"
            min={1}
            max={8}
            value={hoursPerWeek}
            onChange={(e) => setHoursPerWeek(Number(e.target.value))}
            className="w-full accent-primary-600"
          />
          <div className="flex justify-between text-xs text-slate-400 mt-1">
            <span>1h</span>
            <span>8h</span>
          </div>
          <div className="mt-6 text-center">
            <p className="text-sm text-slate-500">
              A {hourlyRate} EUR/h de taux horaire moyen, vous perdez :
            </p>
            <p className="text-4xl font-bold text-red-600 mt-2">
              {annualSavings.toLocaleString("fr-FR")} EUR/an
            </p>
            <p className="text-sm text-slate-400 mt-1">
              soit {monthlySavings.toLocaleString("fr-FR")} EUR/mois pour {hoursPerWeek}h/semaine
            </p>
            <div className="mt-4 p-4 bg-green-50 rounded-lg border border-green-200">
              <p className="text-sm text-green-800">
                Avec FiscIA Pro a <strong>79 EUR/mois</strong>, votre ROI est de{" "}
                <strong>{Math.round((monthlySavings - 79) / 79 * 100)}%</strong> des le premier mois.
              </p>
            </div>
          </div>
        </div>
      </Section>

      {/* ── Comparison table ── */}
      <Section>
        <SectionHeader
          eyebrow="Comparatif"
          title="Toutes les fonctionnalites en detail"
        />
        <div className="overflow-x-auto">
          <table className="w-full max-w-4xl mx-auto text-left">
            <thead>
              <tr className="border-b-2 border-slate-200">
                <th className="py-3 pr-6 text-sm font-semibold text-slate-900 w-1/3">Fonctionnalite</th>
                <th className="py-3 px-4 text-sm font-semibold text-slate-900 text-center">Starter</th>
                <th className="py-3 px-4 text-sm font-semibold text-primary-600 text-center">Pro</th>
                <th className="py-3 px-4 text-sm font-semibold text-slate-900 text-center">Cabinet</th>
              </tr>
            </thead>
            <tbody>
              {COMPARISON_ROWS.map((row) => (
                <tr key={row.feature} className="border-b border-slate-100">
                  <td className="py-3 pr-6 text-sm text-slate-700">{row.feature}</td>
                  <td className="py-3 px-4 text-center"><CellValue val={row.starter} /></td>
                  <td className="py-3 px-4 text-center bg-primary-50/50"><CellValue val={row.pro} /></td>
                  <td className="py-3 px-4 text-center"><CellValue val={row.cabinet} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Section>

      {/* ── FAQ ── */}
      <Section className="bg-slate-50">
        <SectionHeader
          eyebrow="Questions frequentes"
          title="Tout ce que vous devez savoir"
        />
        <div className="max-w-3xl mx-auto space-y-6">
          {FAQ.map((item) => (
            <details
              key={item.q}
              className="group bg-white rounded-xl border border-slate-200 overflow-hidden"
            >
              <summary className="flex items-center justify-between cursor-pointer p-6 text-sm font-semibold text-slate-900 hover:text-primary-600">
                {item.q}
                <svg className="h-5 w-5 text-slate-400 group-open:rotate-180 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 8.25l-7.5 7.5-7.5-7.5" />
                </svg>
              </summary>
              <div className="px-6 pb-6 text-sm text-slate-600 leading-relaxed">
                {item.a}
              </div>
            </details>
          ))}
        </div>
      </Section>

      <CTABanner />
    </>
  );
}
