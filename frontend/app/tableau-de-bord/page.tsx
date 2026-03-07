"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import type { CalculationPreview, UsageSummary } from "@/lib/types";

export default function TableauDeBordPage() {
  const { user, loading: authLoading } = useAuth();
  const [usage, setUsage] = useState<UsageSummary | null>(null);
  const [recent, setRecent] = useState<CalculationPreview[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const [usageData, calculations] = await Promise.all([api.billingUsage(), api.listCalculations()]);
        setUsage(usageData.usage);
        setRecent(calculations.slice(0, 3));
      } finally {
        setLoading(false);
      }
    };
    void load();
  }, []);

  return (
    <section className="space-y-5">
      <Card>
        <CardHeader>
          <CardTitle>Bienvenue sur FiscIA Pro</CardTitle>
          <CardDescription>Pilotage fiscal centralise pour votre cabinet.</CardDescription>
        </CardHeader>
        <CardContent className="grid gap-4 md:grid-cols-3">
          {authLoading ? (
            <>
              <Skeleton className="h-16" />
              <Skeleton className="h-16" />
              <Skeleton className="h-16" />
            </>
          ) : (
            <>
              <Info label="Utilisateur" value={user?.email ?? "-"} />
              <Info label="Role" value={user?.role ?? "-"} />
              <Info label="Cabinet" value={`#${user?.firm_id ?? "-"}`} />
            </>
          )}
        </CardContent>
      </Card>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardContent className="p-5">
            <p className="text-sm text-muted-foreground">Statut abonnement</p>
            <div className="mt-2 flex items-center gap-2">
              <Badge variant="success">Actif</Badge>
              <span className="text-sm">Renouvellement automatique</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-5">
            <p className="text-sm text-muted-foreground">Credits utilises</p>
            <p className="mt-2 text-3xl font-extrabold tabular-nums">{loading ? "..." : usage?.credits_used ?? 0}</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-5">
            <p className="text-sm text-muted-foreground">Actions rapides</p>
            <div className="mt-2 flex flex-wrap gap-2">
              <Button asChild size="sm">
                <Link href="/tableau-de-bord/liasse">Nouvelle liasse</Link>
              </Button>
              <Button asChild variant="outline" size="sm">
                <Link href="/tableau-de-bord/calculs">Historique</Link>
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Activite recente</CardTitle>
          <CardDescription>Derniers calculs enregistres.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          {loading ? (
            <>
              <Skeleton className="h-10" />
              <Skeleton className="h-10" />
              <Skeleton className="h-10" />
            </>
          ) : recent.length === 0 ? (
            <p className="text-sm text-muted-foreground">Aucun calcul recent.</p>
          ) : (
            recent.map((item) => (
              <div key={item.id} className="flex items-center justify-between rounded-md border bg-muted/30 px-3 py-2">
                <div>
                  <p className="text-sm font-medium">SIREN {item.siren}</p>
                  <p className="text-xs text-muted-foreground">{item.created_at}</p>
                </div>
                <div className="text-right">
                  <p className="text-sm font-semibold tabular-nums">{item.is_total.toLocaleString("fr-FR")} EUR</p>
                  <p className="text-xs text-muted-foreground">{item.regime}</p>
                </div>
              </div>
            ))
          )}
        </CardContent>
      </Card>
    </section>
  );
}

function Info({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-md border bg-muted/50 p-3">
      <p className="text-xs text-muted-foreground">{label}</p>
      <p className="mt-1 font-semibold">{value}</p>
    </div>
  );
}
