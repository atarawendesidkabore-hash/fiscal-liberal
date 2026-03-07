type Props = { params: { id: string } };

export default function LiasseDetailPage({ params }: Props) {
  return (
    <section>
      <h1 className="text-2xl font-bold">Liasse {params.id}</h1>
      <p className="mt-2 text-sm text-slate-600">Detail liasse existante (a connecter au backend).</p>
    </section>
  );
}

