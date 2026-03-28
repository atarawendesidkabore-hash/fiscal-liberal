import Link from "next/link";
import { Section, SectionHeader } from "@/components/section";
import { CTABanner } from "@/components/cta-banner";

/* ─── Feature icons (inline SVG for zero-dependency) ─── */
function IconCalculator() {
  return (
    <svg className="h-8 w-8 text-primary-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 15.75V18m-7.5-6.75h.008v.008H8.25v-.008zm0 2.25h.008v.008H8.25v-.008zm0 2.25h.008v.008H8.25v-.008zm0 2.25h.008v.008H8.25v-.008zm2.25-4.5h.008v.008H10.5v-.008zm0 2.25h.008v.008H10.5v-.008zm0 2.25h.008v.008H10.5v-.008zm2.25-6.75h.008v.008H12.75v-.008zm0 2.25h.008v.008H12.75v-.008zm0 2.25h.008v.008H12.75v-.008zm0 2.25h.008v.008H12.75v-.008zm2.25-4.5h.008v.008H15v-.008zm0 2.25h.008v.008H15v-.008zM15 18h.008v.008H15V18zM4.5 4.5h15A1.5 1.5 0 0121 6v12a1.5 1.5 0 01-1.5 1.5h-15A1.5 1.5 0 013 18V6a1.5 1.5 0 011.5-1.5z" />
    </svg>
  );
}

function IconDocument() {
  return (
    <svg className="h-8 w-8 text-primary-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
    </svg>
  );
}

function IconShield() {
  return (
    <svg className="h-8 w-8 text-primary-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z" />
    </svg>
  );
}

function IconSearch() {
  return (
    <svg className="h-8 w-8 text-primary-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z" />
    </svg>
  );
}

function IconClock() {
  return (
    <svg className="h-8 w-8 text-primary-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
  );
}

function IconLock() {
  return (
    <svg className="h-8 w-8 text-primary-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M16.5 10.5V6.75a4.5 4.5 0 10-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 002.25-2.25v-6.75a2.25 2.25 0 00-2.25-2.25H6.75a2.25 2.25 0 00-2.25 2.25v6.75a2.25 2.25 0 002.25 2.25z" />
    </svg>
  );
}

/* ─── Data ─── */

const FEATURES = [
  {
    icon: <IconDocument />,
    title: "Preparation 2065 + 2033",
    description:
      "Pre-remplissez le dossier IS a partir d'un export cabinet. Controle rapide, annexes attendues et brouillon telechargeable avant passage en liasse fiscale.",
  },
  {
    icon: <IconSearch />,
    title: "Import Excel, PDF et CSV",
    description:
      "Glissez-deposez vos fichiers JSON, CSV, TXT, Excel ou PDF. Les champs reconnus remplissent automatiquement le dossier fiscal.",
  },
  {
    icon: <IconCalculator />,
    title: "Liasse 2058-A intelligente",
    description:
      "Reintegrations et deductions ligne par ligne : WI, WG, WM, WN, WV, L8, avec pre-remplissage depuis le dossier 2065 + 2033.",
  },
  {
    icon: <IconClock />,
    title: "Workflow continu vers l'IS",
    description:
      "Passez de la preparation 2065/2033 au calcul IS sans ressaisie. Le resultat comptable, le CA et les informations societes suivent automatiquement.",
  },
  {
    icon: <IconShield />,
    title: "Art. 145 mere-filiale",
    description:
      "Verification automatique des 6 conditions cumulatives. Quote-part de frais et charges et alertes de coherence sur les dossiers sensibles.",
  },
  {
    icon: <IconLock />,
    title: "Securite et conformite",
    description:
      "Donnees hebergees en France. Chiffrement de bout en bout. Conforme RGPD. IA locale optionnelle : zero donnee transmise a l'exterieur.",
  },
];

const USE_CASES = [
  {
    quote:
      "Importer un export cabinet, cadrer la 2065 + 2033, puis envoyer les donnees essentielles dans la 2058-A pour finaliser le resultat fiscal.",
    name: "Cabinets PME",
    role: "Cycle de preparation IS",
    location: "De la saisie a la revue",
  },
  {
    quote:
      "Tester plusieurs dossiers clients a partir de fichiers Excel, verifier les retraitements fiscaux et produire un calcul IS plus vite.",
    name: "Fiscalistes independants",
    role: "Revue et simulation",
    location: "Import multi-formats",
  },
  {
    quote:
      "Monter une offre moderne autour de la liasse fiscale francaise avec un front public clair et un back-office deja operationnel pour les dossiers IS.",
    name: "Cabinets en transformation",
    role: "Offre fiscale augmentee",
    location: "Acquisition + execution",
  },
];

const STATS = [
  { value: "22 000+", label: "experts-comptables en France" },
  { value: "3,5 M", label: "structures accompagnees" },
  { value: "1,16 M", label: "creations d'entreprises en 2025" },
  { value: "10 %", label: "entreprises de 10+ salaries utilisant l'IA" },
];

/* ─── Page ─── */

export default function HomePage() {
  return (
    <>
      {/* ── Hero ── */}
      <section className="relative overflow-hidden bg-gradient-to-b from-primary-50 to-white pt-20 pb-32 px-6">
        <div className="mx-auto max-w-7xl text-center relative z-10">
          {/* Badge */}
          <div className="inline-flex items-center rounded-full bg-primary-100 px-4 py-1.5 text-sm font-medium text-primary-700 mb-8">
            <span className="mr-2">&#9889;</span>
            Nouveau : import Excel/PDF + preparation 2065 et 2033
          </div>

          <h1 className="text-4xl sm:text-5xl md:text-6xl font-bold tracking-tight text-slate-900 leading-tight">
            L&apos;assistant IA des{" "}
            <span className="text-primary-600">fiscalistes francais</span>
          </h1>

          <p className="mt-6 text-lg md:text-xl text-slate-600 max-w-3xl mx-auto leading-relaxed">
            Preparation 2065 + 2033, liasse 2058-A automatisee, import de fichiers
            Excel/PDF et verification Art. 145. <strong>Un meme flux</strong> pour
            passer de la preparation du dossier au calcul IS.
          </p>

          <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link
              href="/register"
              className="rounded-lg bg-primary-600 px-8 py-3.5 text-base font-semibold text-white hover:bg-primary-700 transition-colors shadow-lg shadow-primary-600/25"
            >
              Creer un compte — 14 jours
            </Link>
            <Link
              href="/login"
              className="rounded-lg border border-slate-300 bg-white px-8 py-3.5 text-base font-semibold text-slate-700 hover:bg-slate-50 transition-colors"
            >
              Se connecter
            </Link>
          </div>

          <p className="mt-4 text-sm text-slate-400">
            Sans carte bancaire. Configuration en 2 minutes.
          </p>
        </div>

        {/* Hero visual — mock terminal */}
        <div className="mx-auto mt-16 max-w-4xl relative z-10">
          <div className="rounded-xl border border-slate-200 bg-slate-950 shadow-2xl overflow-hidden">
            <div className="flex items-center gap-2 px-4 py-3 bg-slate-900 border-b border-slate-800">
              <div className="h-3 w-3 rounded-full bg-red-500" />
              <div className="h-3 w-3 rounded-full bg-yellow-500" />
              <div className="h-3 w-3 rounded-full bg-green-500" />
              <span className="ml-3 text-xs text-slate-500 font-mono">FiscIA Pro — Dossier fiscal 2025</span>
            </div>
            <div className="p-6 font-mono text-sm leading-relaxed">
              <p className="text-slate-500">
                <span className="text-green-400">$</span> fiscia import cabinet-atlas-2025.xlsx
              </p>
              <div className="mt-4 space-y-1">
                <p className="text-slate-400">━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</p>
                <p className="text-white">PREPARATION 2065 + 2033 — Exercice 2025</p>
                <p className="text-slate-400">━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</p>
                <p className="text-slate-300">Fichier detecte          : <span className="text-blue-400">2065 / 2033</span></p>
                <p className="text-slate-300">Champs reconnus          : <span className="text-green-400">SIREN, CA HT, resultat comptable</span></p>
                <p className="text-slate-300">Regime applique          : <span className="text-blue-400">Reel simplifie</span></p>
                <p className="text-slate-400 mt-2">RF avant deficits : <span className="text-green-400">240 900 EUR</span></p>
                <p className="text-slate-400">Deficits anterieurs : <span className="text-green-400">50 000 EUR</span></p>
                <p className="text-white mt-2 font-bold">Pont 2058-A pret    :              <span className="text-yellow-400">oui</span></p>
                <p className="text-slate-400 mt-2">Modules actifs : import Excel/PDF, 2065 + 2033, 2058-A</p>
                <p className="text-slate-400">Action suivante : calculer l'IS et sauvegarder le dossier</p>
                <p className="text-slate-400">━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</p>
              </div>
            </div>
          </div>
        </div>

        {/* Background decoration */}
        <div className="absolute inset-0 -z-0 overflow-hidden">
          <div className="absolute -top-1/2 -right-1/4 w-[800px] h-[800px] rounded-full bg-primary-100/50 blur-3xl" />
          <div className="absolute -bottom-1/2 -left-1/4 w-[600px] h-[600px] rounded-full bg-blue-100/50 blur-3xl" />
        </div>
      </section>

      {/* ── Social proof stats ── */}
      <section className="border-y border-slate-200 bg-slate-50 py-12 px-6">
        <div className="mx-auto max-w-7xl grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
          {STATS.map((stat) => (
            <div key={stat.label}>
              <div className="text-3xl font-bold text-primary-600">{stat.value}</div>
              <div className="mt-1 text-sm text-slate-500">{stat.label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* ── Problem → Agitation → Solution ── */}
      <Section>
        <div className="grid md:grid-cols-2 gap-16 items-center">
          <div>
            <p className="text-sm font-semibold uppercase tracking-wider text-red-500 mb-2">
              Le probleme
            </p>
            <h2 className="text-3xl font-bold tracking-tight mb-6">
              Le volume fiscal augmente plus vite que les workflows des cabinets
            </h2>
            <div className="space-y-4 text-slate-600 leading-relaxed">
              <p>
                En France, <strong>plus de 22 000 experts-comptables</strong> accompagnent{" "}
                <strong>environ 3,5 millions de structures</strong>. En parallele, le nombre
                de creations d&apos;entreprises a encore atteint un record en 2025.
              </p>
              <p>
                Le sujet n&apos;est plus seulement de calculer l&apos;IS : il faut absorber plus de
                dossiers, importer plus de formats, mieux cadrer les retraitements et garder une
                piste d&apos;audit exploitable.
              </p>
            </div>
          </div>
          <div>
            <p className="text-sm font-semibold uppercase tracking-wider text-primary-600 mb-2">
              La solution
            </p>
            <h2 className="text-3xl font-bold tracking-tight mb-6">
              Un flux unique de la 2065 au calcul IS
            </h2>
            <div className="space-y-4 text-slate-600 leading-relaxed">
              <p>
                Importez un export cabinet, pre-remplissez la preparation 2065 + 2033,
                poussez les donnees essentielles vers la 2058-A, puis calculez l&apos;IS dans
                le meme environnement.
              </p>
              <p>
                <strong>Vos equipes avancent plus vite</strong> : moins de ressaisie,
                plus de coherence entre les modules, et une page publique qui montre
                enfin les vraies capacites actuelles du produit.
              </p>
            </div>
          </div>
        </div>
      </Section>

      {/* ── Features grid ── */}
      <Section className="bg-slate-50">
        <SectionHeader
          eyebrow="Fonctionnalites"
          title="Tout ce dont un fiscaliste a besoin"
          subtitle="De l'import cabinet au calcul final de l'IS, FiscIA Pro couvre maintenant la preparation 2065 + 2033 et la liasse 2058-A."
        />
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-8">
          {FEATURES.map((f) => (
            <div
              key={f.title}
              className="bg-white rounded-xl border border-slate-200 p-8 hover:shadow-lg transition-shadow"
            >
              <div className="mb-4">{f.icon}</div>
              <h3 className="text-lg font-semibold mb-2">{f.title}</h3>
              <p className="text-sm text-slate-500 leading-relaxed">{f.description}</p>
            </div>
          ))}
        </div>
        <div className="mt-12 text-center">
          <Link
            href="/fonctionnalites"
            className="text-primary-600 font-semibold hover:underline"
          >
            Explorer toutes les fonctionnalites &rarr;
          </Link>
        </div>
      </Section>

      {/* ── Testimonials ── */}
      <Section>
        <SectionHeader
          eyebrow="Cas d'usage"
          title="Les nouveaux flux mis en avant sur la home"
          subtitle="La page publique presente maintenant les cas concrets deja disponibles dans FiscIA Pro."
        />
        <div className="grid md:grid-cols-3 gap-8">
          {USE_CASES.map((t) => (
            <div
              key={t.name}
              className="bg-slate-50 rounded-xl border border-slate-200 p-8"
            >
              {/* Stars */}
              <div className="flex gap-1 mb-4 text-yellow-400">
                {[...Array(5)].map((_, i) => (
                  <svg key={i} className="h-5 w-5 fill-current" viewBox="0 0 20 20">
                    <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                  </svg>
                ))}
              </div>
              <p className="text-slate-600 leading-relaxed mb-6 italic">
                &ldquo;{t.quote}&rdquo;
              </p>
              <div>
                <p className="font-semibold text-slate-900">{t.name}</p>
                <p className="text-sm text-slate-500">{t.role}</p>
                <p className="text-sm text-slate-400">{t.location}</p>
              </div>
            </div>
          ))}
        </div>
      </Section>

      {/* ── Trust badges ── */}
      <section className="bg-slate-50 border-y border-slate-200 py-16 px-6">
        <div className="mx-auto max-w-5xl">
          <p className="text-center text-sm font-semibold uppercase tracking-wider text-slate-400 mb-8">
            Securite et conformite
          </p>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
            <div>
              <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-green-100 mb-3">
                <svg className="h-7 w-7 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z" />
                </svg>
              </div>
              <p className="font-semibold text-sm">Conforme RGPD</p>
              <p className="text-xs text-slate-500 mt-1">Export et suppression des donnees</p>
            </div>
            <div>
              <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-blue-100 mb-3">
                <svg className="h-7 w-7 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M3 3v1.5M3 21v-6m0 0l2.77-.693a9 9 0 016.208.682l.108.054a9 9 0 006.086.71l3.114-.732a48.524 48.524 0 01-.005-10.499l-3.11.732a9 9 0 01-6.085-.711l-.108-.054a9 9 0 00-6.208-.682L3 4.5M3 15V4.5" />
                </svg>
              </div>
              <p className="font-semibold text-sm">Heberge en France</p>
              <p className="text-xs text-slate-500 mt-1">Datacenter Scaleway, Paris</p>
            </div>
            <div>
              <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-amber-100 mb-3">
                <svg className="h-7 w-7 text-amber-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M16.5 10.5V6.75a4.5 4.5 0 10-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 002.25-2.25v-6.75a2.25 2.25 0 00-2.25-2.25H6.75a2.25 2.25 0 00-2.25 2.25v6.75a2.25 2.25 0 002.25 2.25z" />
                </svg>
              </div>
              <p className="font-semibold text-sm">Chiffrement SSL/TLS</p>
              <p className="text-xs text-slate-500 mt-1">AES-256 au repos, TLS 1.3 en transit</p>
            </div>
            <div>
              <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-purple-100 mb-3">
                <svg className="h-7 w-7 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M8.25 7.5V6.108c0-1.135.845-2.098 1.976-2.192.373-.03.748-.057 1.123-.08M15.75 18H18a2.25 2.25 0 002.25-2.25V6.108c0-1.135-.845-2.098-1.976-2.192a48.424 48.424 0 00-1.123-.08M15.75 18.75v-1.875a3.375 3.375 0 00-3.375-3.375h-1.5a1.125 1.125 0 01-1.125-1.125v-1.5A3.375 3.375 0 006.375 7.5H6" />
                </svg>
              </div>
              <p className="font-semibold text-sm">Audit trail complet</p>
              <p className="text-xs text-slate-500 mt-1">Chaque operation tracee et horodatee</p>
            </div>
          </div>
        </div>
      </section>

      {/* ── CTA ── */}
      <CTABanner />
    </>
  );
}
