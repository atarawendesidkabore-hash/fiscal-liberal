import Link from "next/link";

import type { CalculationPreview } from "@/lib/types";

type CalculationCardProps = {
  calculation: CalculationPreview;
};

export default function CalculationCard({ calculation }: CalculationCardProps) {
  return (
    <article className="card p-5">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">SIREN</p>
          <p className="tabular-nums text-lg font-bold text-fiscia-900">{calculation.siren}</p>
          <p className="mt-1 text-sm text-slate-600">Cloture: {calculation.exercice_clos}</p>
        </div>
        <span className="rounded-full bg-fiscia-50 px-3 py-1 text-xs font-semibold text-fiscia-700">
          {calculation.regime}
        </span>
      </div>
      <div className="mt-4 flex items-center justify-between">
        <p className="text-sm text-slate-600">IS total</p>
        <p className="tabular-nums text-xl font-extrabold text-slate-900">{calculation.is_total.toLocaleString("fr-FR")} EUR</p>
      </div>
      <div className="mt-4 flex items-center justify-between">
        <p className="text-xs text-slate-500">Sauvegarde: {calculation.created_at}</p>
        <Link href={`/dashboard/calculations/${calculation.id}`} className="btn-secondary">
          Ouvrir
        </Link>
      </div>
    </article>
  );
}


