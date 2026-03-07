"use client";

import { useEffect, useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import type { UsageSummary } from "@/lib/types";

export default function TableauDeBordPage() {
  const { user, loading: authLoading } = useAuth();
  const [usage, setUsage] = useState<UsageSummary | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const data = await api.billingUsage();
        setUsage(data.usage);
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
            <p className="mt-2 text-3xl font-extrabold tabular-nums">
              {loading ? "..." : usage?.credits_used ?? 0}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-5">
            <p className="text-sm text-muted-foreground">Actions rapides</p>
            <div className="mt-2 flex flex-wrap gap-2">
              <Button asChild size="sm">
                <a href="/tableau-de-bord/liasse">Nouvelle liasse</a>
              </Button>
              <Button asChild variant="outline" size="sm">
                <a href="/tableau-de-bord/calculs">Historique</a>
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
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

