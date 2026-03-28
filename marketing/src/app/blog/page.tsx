import type { Metadata } from "next";
import Link from "next/link";
import { Section, SectionHeader } from "@/components/section";

export const metadata: Metadata = {
  title: "Blog",
  description:
    "Actualites fiscales, guides pratiques et analyses pour les experts-comptables et fiscalistes francais.",
};

const ARTICLES = [
  {
    slug: "lfi-2025-ce-qui-change-pour-lis",
    title: "LFI 2025 : ce qui change pour l'IS des PME",
    excerpt:
      "Le projet de loi de finances 2025 prevoit des ajustements sur le seuil PME et le taux reduit. Analyse des impacts pour les cabinets.",
    category: "Legislation",
    date: "15 janvier 2025",
    readTime: "6 min",
  },
  {
    slug: "5-erreurs-liasse-2058a",
    title: "5 erreurs frequentes sur la liasse 2058-A",
    excerpt:
      "De l'oubli de la reintegration de l'IS comptabilise a la mauvaise application du regime mere-filiale, voici les pieges les plus courants.",
    category: "Guide pratique",
    date: "8 janvier 2025",
    readTime: "8 min",
  },
  {
    slug: "ia-fiscale-opportunite-ou-menace",
    title: "IA fiscale : opportunite ou menace pour les cabinets ?",
    excerpt:
      "L'intelligence artificielle transforme la profession. Comment les cabinets de 1 a 20 associes peuvent en tirer parti sans risque.",
    category: "Tribune",
    date: "20 decembre 2024",
    readTime: "5 min",
  },
  {
    slug: "regime-mere-filiale-guide-complet",
    title: "Regime mere-filiale Art. 145 CGI : le guide complet",
    excerpt:
      "Les 6 conditions cumulatives, la quote-part 5%, les cas particuliers. Tout ce que vous devez savoir en un seul article.",
    category: "Guide pratique",
    date: "12 decembre 2024",
    readTime: "12 min",
  },
  {
    slug: "temoignage-cabinet-duval",
    title: "Temoignage : comment le Cabinet Duval a gagne 10h/mois",
    excerpt:
      "Marie-Claire Duval, expert-comptable a Lyon, partage son experience apres 6 mois d'utilisation de FiscIA Pro.",
    category: "Etude de cas",
    date: "5 decembre 2024",
    readTime: "4 min",
  },
  {
    slug: "securite-donnees-cabinet-comptable",
    title: "Securite des donnees en cabinet comptable : les bonnes pratiques",
    excerpt:
      "RGPD, chiffrement, hebergement : ce que chaque cabinet doit savoir pour proteger les donnees de ses clients.",
    category: "Securite",
    date: "28 novembre 2024",
    readTime: "7 min",
  },
];

const CATEGORIES = ["Tous", "Legislation", "Guide pratique", "Tribune", "Etude de cas", "Securite"];

function CategoryBadge({ category }: { category: string }) {
  const colors: Record<string, string> = {
    "Legislation": "bg-blue-50 text-blue-700 ring-blue-200",
    "Guide pratique": "bg-green-50 text-green-700 ring-green-200",
    "Tribune": "bg-purple-50 text-purple-700 ring-purple-200",
    "Etude de cas": "bg-amber-50 text-amber-700 ring-amber-200",
    "Securite": "bg-red-50 text-red-700 ring-red-200",
  };

  return (
    <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ring-1 ring-inset ${colors[category] || "bg-slate-50 text-slate-700 ring-slate-200"}`}>
      {category}
    </span>
  );
}

export default function BlogPage() {
  return (
    <>
      <Section className="bg-gradient-to-b from-primary-50 to-white pt-12">
        <SectionHeader
          eyebrow="Blog"
          title="Actualites fiscales et guides pratiques"
          subtitle="Restez informe des evolutions legislatives et decouvrez comment optimiser vos travaux fiscaux."
        />

        {/* Category filter (static for now — would be interactive with state) */}
        <div className="flex flex-wrap justify-center gap-2 mb-12">
          {CATEGORIES.map((cat) => (
            <button
              key={cat}
              className={`rounded-full px-4 py-1.5 text-sm font-medium transition-colors ${
                cat === "Tous"
                  ? "bg-primary-600 text-white"
                  : "bg-white text-slate-600 border border-slate-200 hover:border-primary-300 hover:text-primary-600"
              }`}
            >
              {cat}
            </button>
          ))}
        </div>
      </Section>

      <Section>
        {/* Featured article */}
        <div className="mb-16">
          <div className="rounded-2xl bg-gradient-to-r from-primary-600 to-primary-800 p-8 md:p-12 text-white">
            <CategoryBadge category={ARTICLES[0].category} />
            <h2 className="text-2xl md:text-3xl font-bold mt-4 mb-3">
              <Link href={`/blog/${ARTICLES[0].slug}`} className="hover:underline">
                {ARTICLES[0].title}
              </Link>
            </h2>
            <p className="text-primary-100 mb-4 max-w-2xl leading-relaxed">
              {ARTICLES[0].excerpt}
            </p>
            <div className="flex items-center gap-4 text-sm text-primary-200">
              <span>{ARTICLES[0].date}</span>
              <span>&middot;</span>
              <span>{ARTICLES[0].readTime} de lecture</span>
            </div>
          </div>
        </div>

        {/* Article grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {ARTICLES.slice(1).map((article) => (
            <article
              key={article.slug}
              className="bg-white rounded-xl border border-slate-200 overflow-hidden hover:shadow-lg transition-shadow"
            >
              {/* Colored top bar */}
              <div className="h-1 bg-gradient-to-r from-primary-500 to-primary-600" />
              <div className="p-6">
                <div className="mb-3">
                  <CategoryBadge category={article.category} />
                </div>
                <h3 className="font-semibold text-slate-900 mb-2 leading-snug">
                  <Link href={`/blog/${article.slug}`} className="hover:text-primary-600 transition-colors">
                    {article.title}
                  </Link>
                </h3>
                <p className="text-sm text-slate-500 leading-relaxed mb-4">
                  {article.excerpt}
                </p>
                <div className="flex items-center justify-between text-xs text-slate-400">
                  <span>{article.date}</span>
                  <span>{article.readTime} de lecture</span>
                </div>
              </div>
            </article>
          ))}
        </div>

        {/* Newsletter CTA */}
        <div className="mt-16 rounded-2xl bg-slate-50 border border-slate-200 p-8 md:p-12 text-center">
          <h3 className="text-xl font-bold mb-2">Restez informe</h3>
          <p className="text-sm text-slate-500 mb-6">
            Recevez les nouveaux articles et les alertes legislatives directement dans votre boite mail.
            1 email par semaine maximum.
          </p>
          <form className="flex flex-col sm:flex-row gap-3 max-w-md mx-auto">
            <input
              type="email"
              placeholder="votre@email-pro.fr"
              className="flex-1 rounded-lg border border-slate-300 px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
            <button
              type="submit"
              className="rounded-lg bg-primary-600 px-6 py-2.5 text-sm font-semibold text-white hover:bg-primary-700 transition-colors whitespace-nowrap"
            >
              S&apos;abonner
            </button>
          </form>
          <p className="mt-3 text-xs text-slate-400">
            Desabonnement en un clic. Conforme RGPD.
          </p>
        </div>
      </Section>
    </>
  );
}
