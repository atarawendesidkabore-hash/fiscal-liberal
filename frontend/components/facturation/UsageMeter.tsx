import { AlertTriangle, CheckCircle2 } from "lucide-react";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import type { UsageSummary } from "@/lib/types";

type UsageMeterProps = {
  usage: UsageSummary;
};

export default function UsageMeter({ usage }: UsageMeterProps) {
  const percent = usage.unlimited ? 0 : Math.min(Math.round((usage.credits_used / Math.max(usage.credits_total, 1)) * 100), 100);
  const remainingLow = !usage.unlimited && usage.credits_remaining <= 10;

  return (
    <Card>
      <CardHeader>
        <CardTitle>Consommation credits</CardTitle>
        <CardDescription>Periode fiscale {usage.period}</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {usage.unlimited ? (
          <div className="flex items-center gap-2 rounded-md bg-emerald-50 p-3 text-sm text-emerald-700">
            <CheckCircle2 className="h-4 w-4" />
            Formule illimitee active
          </div>
        ) : (
          <>
            <div className="h-3 overflow-hidden rounded-full bg-muted">
              <div className="h-full bg-primary transition-all" style={{ width: `${percent}%` }} />
            </div>
            <div className="grid grid-cols-3 gap-3 text-sm">
              <Metric label="Total" value={usage.credits_total.toString()} />
              <Metric label="Utilises" value={usage.credits_used.toString()} />
              <Metric label="Restants" value={usage.credits_remaining.toString()} />
            </div>
            {remainingLow ? (
              <div className="flex items-center gap-2 rounded-md border border-amber-300 bg-amber-50 p-3 text-sm text-amber-800">
                <AlertTriangle className="h-4 w-4" />
                Credits bas. Pensez a upgrader votre abonnement.
              </div>
            ) : null}
          </>
        )}
      </CardContent>
    </Card>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-md border bg-background p-3 text-center">
      <p className="text-xs text-muted-foreground">{label}</p>
      <p className="text-lg font-semibold tabular-nums">{value}</p>
    </div>
  );
}

