import type { Metadata } from "next";
import { Section, SectionHeader } from "@/components/section";
import { CTABanner } from "@/components/cta-banner";

export const metadata: Metadata = {
  title: "A propos",
  description:
    "L'equipe derriere FiscIA Pro : des ingenieurs et des fiscalistes qui automatisent l'IS francais.",
};

const TEAM = [
  {
    name: "Thomas Lefebvre",
    role: "CEO & Co-fondateur",
    bio: "Ancien fiscaliste chez Deloitte. 12 ans d'experience en IS. Diplome HEC Paris.",
  },
  {
    name: "Sarah Nguyen",
    role: "CTO & Co-fondatrice",
    bio: "Ingenieure IA. Ex-Google DeepMind. Experte en NLP applique au juridique.",
  },
  {
    name: "Marc Dubois",
    role: "Lead Developer",
    bio: "Architecte Python/FastAPI. 8 ans de fintech. Expert securite et conformite.",
  },
  {
    name: "Camille Roux",
    role: "Head of Product",
    bio: "UX designer. Ex-Alan. Specialiste des outils SaaS pour professions reglementees.",
  },
  {
    name: "Antoine Mercier",
    role: "Fiscal Lead",
    bio: "Expert-comptable et commissaire aux comptes. Membre de l'Ordre. 15 ans de pratique.",
  },
  {
    name: "Julie Martin",
    role: "Customer Success",
    bio: "Accompagne les cabinets dans leur adoption. Ancienne collaboratrice en cabinet comptable.",
  },
];

const VALUES = [
  {
    title: "Precision",
    description: "Chaque calcul cite ses sources CGI. Chaque resultat est verifiable. Zero approximation.",
    icon: (
      <svg className="h-8 w-8 text-primary-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    ),
  },
  {
    title: "Confidentialite",
    description: "Hebergement francais. IA locale optionnelle. Zero donnee transmise a l'exterieur si vous le souhaitez.",
    icon: (
      <svg className="h-8 w-8 text-primary-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M16.5 10.5V6.75a4.5 4.5 0 10-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 002.25-2.25v-6.75a2.25 2.25 0 00-2.25-2.25H6.75a2.25 2.25 0 00-2.25 2.25v6.75a2.25 2.25 0 002.25 2.25z" />
      </svg>
    ),
  },
  {
    title: "Humilite",
    description: "FiscIA aide, ne remplace pas. Chaque reponse porte un disclaimer. La validation professionnelle reste indispensable.",
    icon: (
      <svg className="h-8 w-8 text-primary-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" />
      </svg>
    ),
  },
  {
    title: "Transparence",
    description: "Tarification claire. Pas de frais caches. Code source auditable pour les clients Cabinet.",
    icon: (
      <svg className="h-8 w-8 text-primary-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M2.036 12.322a1.012 1.012 0 010-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178z" />
        <path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
      </svg>
    ),
  },
];

const TIMELINE = [
  { year: "2023", event: "Idee nee d'une frustration : 3h/semaine perdues a chercher des articles CGI" },
  { year: "2024 T1", event: "Premier prototype du moteur IS. Tests avec 5 cabinets beta." },
  { year: "2024 T2", event: "Lancement de la liasse 2058-A automatisee et de la verification Art. 145" },
  { year: "2024 T3", event: "Integration de l'IA locale (Ollama). Conformite RGPD complete." },
  { year: "2024 T4", event: "Lancement public. 50+ cabinets utilisateurs." },
  { year: "2025", event: "API REST, multi-cabinet, integrations QuickBooks et Xero." },
];

export default function AProposPage() {
  return (
    <>
      {/* ── Mission ── */}
      <Section className="bg-gradient-to-b from-primary-50 to-white pt-12">
        <div className="mx-auto max-w-3xl text-center">
          <p className="text-sm font-semibold uppercase tracking-wider text-primary-600 mb-2">
            Notre mission
          </p>
          <h1 className="text-3xl md:text-4xl font-bold tracking-tight mb-6">
            Donner aux fiscalistes francais les outils qu&apos;ils meritent
          </h1>
          <p className="text-lg text-slate-600 leading-relaxed">
            21 611 experts-comptables en France. La plupart utilisent encore Excel, Legifrance
            et leurs notes manuscrites pour determiner l&apos;IS de leurs clients.
            Nous construisons l&apos;outil qui leur fait gagner 2 a 4 heures par semaine
            — avec la precision et la conformite qu&apos;exige la fiscalite francaise.
          </p>
        </div>
      </Section>

      {/* ── Values ── */}
      <Section>
        <SectionHeader
          eyebrow="Nos valeurs"
          title="Ce qui guide chaque ligne de code"
        />
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-8">
          {VALUES.map((v) => (
            <div key={v.title} className="text-center">
              <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-primary-50 mb-4">
                {v.icon}
              </div>
              <h3 className="font-semibold mb-2">{v.title}</h3>
              <p className="text-sm text-slate-500 leading-relaxed">{v.description}</p>
            </div>
          ))}
        </div>
      </Section>

      {/* ── Team ── */}
      <Section className="bg-slate-50">
        <SectionHeader
          eyebrow="L'equipe"
          title="Des fiscalistes et des ingenieurs"
          subtitle="Nous combinons l'expertise fiscale terrain et l'innovation technologique."
        />
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-8">
          {TEAM.map((member) => (
            <div
              key={member.name}
              className="bg-white rounded-xl border border-slate-200 p-6 hover:shadow-md transition-shadow"
            >
              <div className="flex h-16 w-16 items-center justify-center rounded-full bg-primary-100 text-primary-700 font-bold text-xl mb-4">
                {member.name.split(" ").map((n) => n[0]).join("")}
              </div>
              <h3 className="font-semibold text-slate-900">{member.name}</h3>
              <p className="text-sm text-primary-600 font-medium">{member.role}</p>
              <p className="text-sm text-slate-500 mt-2 leading-relaxed">{member.bio}</p>
            </div>
          ))}
        </div>
      </Section>

      {/* ── Timeline ── */}
      <Section>
        <SectionHeader
          eyebrow="Notre parcours"
          title="De l'idee au produit"
        />
        <div className="max-w-2xl mx-auto">
          <div className="relative border-l-2 border-primary-200 pl-8 space-y-8">
            {TIMELINE.map((item) => (
              <div key={item.year} className="relative">
                <div className="absolute -left-[41px] flex h-5 w-5 items-center justify-center rounded-full bg-primary-600">
                  <div className="h-2 w-2 rounded-full bg-white" />
                </div>
                <p className="text-sm font-bold text-primary-600">{item.year}</p>
                <p className="text-slate-600 leading-relaxed">{item.event}</p>
              </div>
            ))}
          </div>
        </div>
      </Section>

      <CTABanner
        title="Rejoignez l'aventure FiscIA Pro"
        subtitle="Essai gratuit de 14 jours, sans engagement."
      />
    </>
  );
}
