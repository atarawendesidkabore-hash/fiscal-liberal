export default function NouveauClientPage() {
  return (
    <section>
      <h1 className="text-2xl font-bold">Nouveau dossier client</h1>
      <form className="mt-4 max-w-lg space-y-3 rounded bg-white p-4 shadow-sm">
        <input className="w-full rounded border p-2" placeholder="Denomination" />
        <input className="w-full rounded border p-2" placeholder="SIREN" />
        <button type="button" className="rounded bg-fiscal-500 px-3 py-2 text-white">
          Creer le dossier
        </button>
      </form>
    </section>
  );
}

