import type { UsageSummary } from "@/lib/types";

type UsageMeterProps = {
  usage: UsageSummary;
};

export default function UsageMeter({ usage }: UsageMeterProps) {
  const percent = usage.unlimited
    ? 0
    : Math.min(Math.round((usage.credits_used / Math.max(usage.credits_total, 1)) * 100), 100);

  return (
    <div className="card p-5">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-bold text-fiscia-900">Credits de calcul</h3>
        <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-700">{usage.period}</span>
      </div>

      {usage.unlimited ? (
        <p className="mt-3 text-sm text-slate-700">Plan illimite actif. Utilisation sans blocage.</p>
      ) : (
        <>
          <div className="mt-4 h-3 overflow-hidden rounded-full bg-slate-200">
            <div className="h-full rounded-full bg-fiscia-600 transition-all" style={{ width: `${percent}%` }} />
          </div>
          <p className="mt-3 text-sm text-slate-700">
            {usage.credits_used} / {usage.credits_total} calculs utilises ({percent}%)
          </p>
          <p className="text-sm text-slate-500">Restants: {usage.credits_remaining}</p>
        </>
      )}
    </div>
  );
}


