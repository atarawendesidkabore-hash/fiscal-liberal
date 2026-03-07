type Props = { params: { id: string } };

export default function ClientDetailPage({ params }: Props) {
  return (
    <section>
      <h1 className="text-2xl font-bold">Dossier client {params.id}</h1>
      <p className="mt-2 text-sm text-slate-600">Vue detaillee a connecter aux donnees backend.</p>
    </section>
  );
}

