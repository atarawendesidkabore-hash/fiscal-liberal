import Link from "next/link";

const FOOTER_SECTIONS = [
  {
    title: "Produit",
    links: [
      { href: "/fonctionnalites", label: "Fonctionnalites" },
      { href: "/tarification", label: "Tarification" },
      { href: "/demo", label: "Demo gratuite" },
      { href: "/register", label: "Creer un compte" },
      { href: "/login", label: "Se connecter" },
      { href: "/blog", label: "Blog" },
    ],
  },
  {
    title: "Entreprise",
    links: [
      { href: "/a-propos", label: "A propos" },
      { href: "/contact", label: "Contact" },
      { href: "/blog", label: "Actualites" },
    ],
  },
  {
    title: "Legal",
    links: [
      { href: "/mentions-legales", label: "Mentions legales" },
      { href: "/confidentialite", label: "Politique de confidentialite" },
      { href: "/cgv", label: "CGV" },
      { href: "/cgu", label: "CGU" },
    ],
  },
  {
    title: "Support",
    links: [
      { href: "/contact", label: "Assistance" },
      { href: "mailto:support@fiscia.pro", label: "support@fiscia.pro" },
      { href: "tel:+33176340000", label: "01 76 34 00 00" },
    ],
  },
];

export function Footer() {
  return (
    <footer className="border-t border-slate-200 bg-slate-50">
      <div className="mx-auto max-w-7xl px-6 py-16">
        <div className="grid grid-cols-2 md:grid-cols-5 gap-8">
          {/* Brand */}
          <div className="col-span-2 md:col-span-1">
            <Link href="/" className="flex items-center gap-2 mb-4">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary-600 text-white font-bold text-sm">
                F
              </div>
              <span className="font-bold">
                <span className="text-primary-600">FiscIA</span>{" "}
                <span className="text-slate-400 font-normal">Pro</span>
              </span>
            </Link>
            <p className="text-sm text-slate-500 leading-relaxed">
              L&apos;assistant IA des fiscalistes francais. Preparation 2065 + 2033, liasse 2058-A et calcul IS dans un meme flux.
            </p>
            {/* Trust badges */}
            <div className="mt-4 flex flex-wrap gap-2">
              <span className="inline-flex items-center rounded-full bg-green-50 px-2.5 py-1 text-xs font-medium text-green-700 ring-1 ring-green-200 ring-inset">
                RGPD
              </span>
              <span className="inline-flex items-center rounded-full bg-blue-50 px-2.5 py-1 text-xs font-medium text-blue-700 ring-1 ring-blue-200 ring-inset">
                Made in France
              </span>
              <span className="inline-flex items-center rounded-full bg-amber-50 px-2.5 py-1 text-xs font-medium text-amber-700 ring-1 ring-amber-200 ring-inset">
                SSL/TLS
              </span>
            </div>
          </div>

          {/* Link sections */}
          {FOOTER_SECTIONS.map((section) => (
            <div key={section.title}>
              <h3 className="text-sm font-semibold text-slate-900 mb-3">
                {section.title}
              </h3>
              <ul className="space-y-2">
                {section.links.map((link) => (
                  <li key={link.href + link.label}>
                    <Link
                      href={link.href}
                      className="text-sm text-slate-500 hover:text-primary-600 transition-colors"
                    >
                      {link.label}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Bottom bar */}
        <div className="mt-12 pt-8 border-t border-slate-200 flex flex-col md:flex-row items-center justify-between gap-4">
          <p className="text-sm text-slate-500">
            &copy; {new Date().getFullYear()} FiscIA Pro SAS. Tous droits reserves.
          </p>
          <p className="text-xs text-slate-400">
            Reponses indicatives. Toute decision fiscale engageante necessite
            l&apos;analyse personnalisee d&apos;un professionnel qualifie.
          </p>
        </div>
      </div>
    </footer>
  );
}
