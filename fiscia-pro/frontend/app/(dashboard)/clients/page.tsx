import Link from "next/link";

export default function ClientsPage() {
  return (
    <section className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Dossiers clients</h1>
        <Link href="/clients/nouveau" className="rounded bg-fiscal-500 px-3 py-2 text-white">
          Nouveau dossier
        </Link>
      </div>
      <div className="rounded bg-white p-4 text-sm shadow-sm">Aucun dossier pour le moment.</div>
    </section>
  );
}

