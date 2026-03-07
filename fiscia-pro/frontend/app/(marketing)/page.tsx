import Link from "next/link";

export default function MarketingHome() {
  return (
    <main className="mx-auto max-w-5xl space-y-8 px-6 py-12">
      <section className="rounded-xl bg-white p-8 shadow-sm">
        <h1 className="text-3xl font-bold text-fiscal-700">FiscIA Pro</h1>
        <p className="mt-3 text-slate-700">
          Assistant IA fiscal pour cabinets francais: liasse 2058-A, calcul IS Art. 219, veille et recherche CGI.
        </p>
        <div className="mt-6 flex gap-3">
          <Link className="rounded bg-fiscal-500 px-4 py-2 text-white" href="/login">
            Se connecter
          </Link>
          <Link className="rounded border border-slate-300 px-4 py-2" href="/tarifs">
            Voir les tarifs
          </Link>
        </div>
      </section>
    </main>
  );
}

