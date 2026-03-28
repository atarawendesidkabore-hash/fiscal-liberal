import Link from "next/link";

export function CTABanner({
  title = "Passez de la 2065 a la 2058-A sans ressaisie",
  subtitle = "Importez un export cabinet, completez les retraitements fiscaux et calculez l'IS dans le meme flux.",
  primaryLabel = "Creer un compte",
  primaryHref = "/register",
  secondaryLabel = "Se connecter",
  secondaryHref = "/login",
}: {
  title?: string;
  subtitle?: string;
  primaryLabel?: string;
  primaryHref?: string;
  secondaryLabel?: string;
  secondaryHref?: string;
}) {
  return (
    <section className="bg-primary-600 py-20 px-6">
      <div className="mx-auto max-w-4xl text-center">
        <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
          {title}
        </h2>
        <p className="text-lg text-primary-100 mb-8">{subtitle}</p>
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
          <Link
            href={primaryHref}
            className="rounded-lg bg-white px-8 py-3 text-sm font-semibold text-primary-700 hover:bg-primary-50 transition-colors shadow-lg"
          >
            {primaryLabel}
          </Link>
          <Link
            href={secondaryHref}
            className="rounded-lg border-2 border-white/30 px-8 py-3 text-sm font-semibold text-white hover:bg-white/10 transition-colors"
          >
            {secondaryLabel}
          </Link>
        </div>
        <p className="mt-6 text-sm text-primary-200">
          14 jours d&apos;essai gratuit. Sans engagement. Sans carte bancaire.
        </p>
      </div>
    </section>
  );
}
