"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { api } from "@/lib/api";
import type { CalculationDetail } from "@/lib/types";

export default function CalculDetailPage() {
  const params = useParams<{ id: string }>();
  const idParam = params?.id;
  const id = Array.isArray(idParam) ? idParam[0] : idParam || "";

  const [item, setItem] = useState<CalculationDetail | null>(null);
  const [iaExplanation, setIaExplanation] = useState<string>("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const found = await api.calculationById(id);
        setItem(found);
        if (found) {
          try {
            const ai = await api.searchCgi("article 219 taux is pme");
            const first = ai.results[0];
            setIaExplanation(
              first
                ? `${found.ai_explanation}\n\nReference: ${first.article} - ${first.title}`
                : found.ai_explanation || ""
            );
          } catch {
            setIaExplanation(found.ai_explanation || "");
          }
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : "Erreur de chargement du calcul.");
      } finally {
        setLoading(false);
      }
    };
    void load();
  }, [id]);

  if (loading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-24" />
        <Skeleton className="h-64" />
      </div>
    );
  }

  if (!item) {
    return (
      <p className="rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-700">
        {error ?? "Calcul introuvable."}
      </p>
    );
  }

  return (
    <section id="export-zone" className="space-y-5">
      <Card>
        <CardHeader>
          <CardTitle>Calcul {item.id}</CardTitle>
          <CardDescription>Vue detaillee avec explication IA.</CardDescription>
        </CardHeader>
        <CardContent className="flex flex-wrap items-center gap-2">
          <Badge variant="secondary">SIREN {item.siren}</Badge>
          <Badge>{item.regime}</Badge>
          <Button variant="outline" onClick={() => window.print()}>
            Export PDF
          </Button>
        </CardContent>
      </Card>

      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Resultat fiscal</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-sm">
            <Line label="IS total" value={`${item.is_total.toLocaleString("fr-FR")} EUR`} />
            <Line label="Exercice" value={item.exercice_clos} />
            <Line label="Date creation" value={item.created_at} />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Explication IA</CardTitle>
            <CardDescription>Generee automatiquement a partir de vos donnees.</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="whitespace-pre-wrap text-sm text-muted-foreground">{iaExplanation || "Aucune explication disponible."}</p>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Lignes 2058-A</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b text-left text-muted-foreground">
                  <th className="pb-2">Code</th>
                  <th className="pb-2 text-right">Montant</th>
                </tr>
              </thead>
              <tbody>
                {(item.lignes || []).map((line) => (
                  <tr key={line.code} className="border-b">
                    <td className="py-2">{line.code}</td>
                    <td className="py-2 text-right tabular-nums">{line.montant.toLocaleString("fr-FR")} EUR</td>
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

function Line({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between">
      <span className="text-muted-foreground">{label}</span>
      <span className="font-semibold tabular-nums">{value}</span>
    </div>
  );
}

