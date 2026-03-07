"use client";

import { CreditCard, Landmark, Smartphone } from "lucide-react";
import { useEffect, useState } from "react";

import ConfirmDialog from "@/components/ui/confirm-dialog";
import UsageMeter from "@/components/facturation/UsageMeter";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useToast } from "@/lib/toast";
import { api } from "@/lib/api";
import type { BillingPlan, InvoiceEvent, UsageSummary } from "@/lib/types";

const paymentMethods = [
  {
    label: "SEPA Direct Debit",
    description: "Prelevement recurrent optimise pour la France.",
    icon: Landmark
  },
  {
    label: "Carte bancaire",
    description: "Visa, Mastercard et cartes professionnelles.",
    icon: CreditCard
  },
  {
    label: "Apple Pay / Google Pay",
    description: "Paiement wallet rapide sur mobile.",
    icon: Smartphone
  }
];

export default function FacturationPage() {
  const [plans, setPlans] = useState<BillingPlan[]>([]);
  const [usage, setUsage] = useState<UsageSummary | null>(null);
  const [invoices, setInvoices] = useState<InvoiceEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [openCancel, setOpenCancel] = useState(false);
  const { push } = useToast();

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
        const message = err instanceof Error ? err.message : "Erreur facturation";
        setError(message);
        push({ title: "Facturation indisponible", description: message, variant: "error" });
      } finally {
        setLoading(false);
      }
    };

    void load();
  }, [push]);

  const subscribe = async (planName: string) => {
    try {
      const origin = window.location.origin;
      const response = await api.billingSubscribe(planName, `${origin}/tableau-de-bord/facturation`, `${origin}/tableau-de-bord/facturation`);
      if (response.checkout_url) {
        window.location.href = response.checkout_url;
        return;
      }
      push({ title: "Session Stripe", description: "URL de paiement absente.", variant: "error" });
    } catch (err) {
      const message = err instanceof Error ? err.message : "Abonnement impossible";
      setError(message);
      push({ title: "Echec souscription", description: message, variant: "error" });
    }
  };

  const cancelSubscription = async () => {
    try {
      await api.billingCancel(true);
      push({ title: "Resiliation planifiee", description: "La resiliation prendra effet en fin de periode.", variant: "success" });
    } catch (err) {
      push({ title: "Resiliation impossible", description: err instanceof Error ? err.message : "Erreur inconnue", variant: "error" });
    } finally {
      setOpenCancel(false);
    }
  };

  return (
    <section className="space-y-5">
      <Card>
        <CardHeader className="flex flex-row items-start justify-between gap-3">
          <div>
            <CardTitle>Facturation</CardTitle>
            <CardDescription>Gestion abonnement, credits et historique des paiements.</CardDescription>
          </div>
          <Button type="button" variant="outline" onClick={() => setOpenCancel(true)}>
            Resilier
          </Button>
        </CardHeader>
      </Card>

      {error ? <p className="rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-700">{error}</p> : null}

      {loading || !usage ? <Skeleton className="h-44" /> : <UsageMeter usage={usage} />}

      <div className="grid gap-4 md:grid-cols-3">
        {plans.map((plan) => (
          <Card key={plan.name} className={plan.name.toLowerCase() === "pro" ? "border-primary shadow-panel" : ""}>
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
                Choisir ce plan
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Moyens de paiement disponibles</CardTitle>
          <CardDescription>Configuration optimisee pour les cabinets francais (EUR).</CardDescription>
        </CardHeader>
        <CardContent className="grid gap-3 md:grid-cols-3">
          {paymentMethods.map((method) => {
            const Icon = method.icon;
            return (
              <div key={method.label} className="rounded-md border bg-muted/40 p-4">
                <div className="mb-2 flex items-center gap-2 text-sm font-semibold">
                  <Icon className="h-4 w-4" />
                  {method.label}
                </div>
                <p className="text-xs text-muted-foreground">{method.description}</p>
              </div>
            );
          })}
        </CardContent>
      </Card>

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

      <ConfirmDialog
        open={openCancel}
        title="Confirmer la resiliation ?"
        description="Votre abonnement restera actif jusqu'a la fin de la periode en cours."
        confirmLabel="Confirmer la resiliation"
        onCancel={() => setOpenCancel(false)}
        onConfirm={() => void cancelSubscription()}
      />
    </section>
  );
}
