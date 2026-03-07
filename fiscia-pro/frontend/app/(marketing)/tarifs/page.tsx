const tiers = [
  { name: "Starter", price: "49 EUR/mois", desc: "Independant / petite structure" },
  { name: "Pro", price: "149 EUR/mois", desc: "Cabinet 1-5 associes" },
  { name: "Cabinet", price: "399 EUR/mois", desc: "Cabinet structure 5-20 associes" }
];

export default function TarifsPage() {
  return (
    <main className="mx-auto max-w-4xl px-6 py-10">
      <h1 className="mb-6 text-2xl font-bold">Tarifs FiscIA Pro</h1>
      <div className="grid gap-4 md:grid-cols-3">
        {tiers.map((tier) => (
          <article key={tier.name} className="rounded-lg bg-white p-4 shadow-sm">
            <h2 className="font-semibold">{tier.name}</h2>
            <p className="mt-1 text-xl text-fiscal-700">{tier.price}</p>
            <p className="mt-2 text-sm text-slate-600">{tier.desc}</p>
          </article>
        ))}
      </div>
    </main>
  );
}

