"use client";

import { useEffect, useState } from "react";

import UsageDisplay from "@/components/facturation/UsageDisplay";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { api } from "@/lib/api";
import type { BillingPlan, InvoiceEvent, UsageSummary } from "@/lib/types";

export default function FacturationPage() {
  const [plans, setPlans] = useState<BillingPlan[]>([]);
  const [usage, setUsage] = useState<UsageSummary | null>(null);
  const [invoices, setInvoices] = useState<InvoiceEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const load = async () => {
      try {
        const [plansResponse, usageResponse, invoicesResponse] = await Promise.all([
          api.billingPlans(),
          api.billingUsage(),
          api.billingInvoices()
        ]);
        setPlans(plansResponse.plans);
        setUsage(usageResponse.usage);
        setInvoices(invoicesResponse.invoices);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Erreur facturation");
      } finally {
        setLoading(false);
      }
    };

    void load();
  }, []);

  const subscribe = async (planName: string) => {
    try {
      const origin = window.location.origin;
      const response = await api.billingSubscribe(planName, `${origin}/tableau-de-bord/facturation`, `${origin}/tableau-de-bord/facturation`);
      if (response.checkout_url) window.location.href = response.checkout_url;
    } catch (err) {
      setError(err instanceof Error ? err.message : "Abonnement impossible");
    }
  };

  return (
    <section className="space-y-5">
      <Card>
        <CardHeader>
          <CardTitle>Facturation</CardTitle>
          <CardDescription>Gestion abonnement, credits et historique des paiements.</CardDescription>
        </CardHeader>
      </Card>

      {error ? <p className="rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-700">{error}</p> : null}

      {loading || !usage ? <Skeleton className="h-44" /> : <UsageDisplay usage={usage} />}

      <div className="grid gap-4 md:grid-cols-3">
        {plans.map((plan) => (
          <Card key={plan.name}>
            <CardHeader>
              <CardTitle className="flex items-center justify-between text-lg uppercase">
                {plan.name}
                {plan.unlimited ? <Badge variant="secondary">Illimite</Badge> : null}
              </CardTitle>
              <CardDescription>{plan.price} EUR / mois</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              <p className="text-sm text-muted-foreground">
                {plan.unlimited ? "Calculs illimites" : `${plan.calculation_limit} calculs inclus`}
              </p>
              <Button className="w-full" onClick={() => void subscribe(plan.name)}>
                Souscrire
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Historique factures</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b text-left text-muted-foreground">
                  <th className="pb-2">Evenement</th>
                  <th className="pb-2">Type</th>
                  <th className="pb-2 text-right">Montant</th>
                  <th className="pb-2">Statut</th>
                </tr>
              </thead>
              <tbody>
                {invoices.map((invoice) => (
                  <tr key={invoice.stripe_event_id} className="border-b">
                    <td className="py-2 font-mono text-xs">{invoice.stripe_event_id}</td>
                    <td className="py-2">{invoice.type}</td>
                    <td className="py-2 text-right tabular-nums">{invoice.amount.toLocaleString("fr-FR")} EUR</td>
                    <td className="py-2">{invoice.status}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </section>
  );
}

