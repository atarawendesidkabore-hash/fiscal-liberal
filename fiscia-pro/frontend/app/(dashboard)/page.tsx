export default function DashboardHomePage() {
  return (
    <section className="space-y-4">
      <h1 className="text-2xl font-bold">Dashboard fiscal</h1>
      <div className="grid gap-3 md:grid-cols-3">
        <div className="rounded bg-white p-4 shadow-sm">
          <p className="text-sm text-slate-500">Liasses en cours</p>
          <p className="text-2xl font-semibold">0</p>
        </div>
        <div className="rounded bg-white p-4 shadow-sm">
          <p className="text-sm text-slate-500">Alertes veille</p>
          <p className="text-2xl font-semibold">0</p>
        </div>
        <div className="rounded bg-white p-4 shadow-sm">
          <p className="text-sm text-slate-500">Requetes IA mois</p>
          <p className="text-2xl font-semibold">0</p>
        </div>
      </div>
    </section>
  );
}

