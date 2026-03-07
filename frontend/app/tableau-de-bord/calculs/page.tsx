"use client";

import { useEffect, useMemo, useState } from "react";
import useSWR from "swr";

import CalculationCard from "@/components/calculs/CalculationCard";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import { useToast } from "@/lib/toast";
import { api } from "@/lib/api";
import type { CalculationPreview } from "@/lib/types";

const PAGE_SIZE = 4;

export default function CalculsPage() {
  const [query, setQuery] = useState("");
  const [regime, setRegime] = useState("all");
  const [sortBy, setSortBy] = useState("recent");
  const [page, setPage] = useState(1);
  const { push } = useToast();

  const {
    data: items = [],
    isLoading: loading,
    error
  } = useSWR<CalculationPreview[]>("calculations:list", () => api.listCalculations(), {
    keepPreviousData: true
  });

  useEffect(() => {
    if (error) {
      push({
        title: "Erreur chargement",
        description: error instanceof Error ? error.message : "Impossible de charger",
        variant: "error"
      });
    }
  }, [error, push]);

  const filtered = useMemo(() => {
    const normalized = query.toLowerCase().trim();
    const base = items.filter((item) => {
      const matchesQuery =
        !normalized ||
        item.siren.includes(normalized) ||
        item.regime.toLowerCase().includes(normalized) ||
        item.id.toLowerCase().includes(normalized);
      const matchesRegime = regime === "all" || item.regime === regime;
      return matchesQuery && matchesRegime;
    });

    return [...base].sort((a, b) => {
      if (sortBy === "amount-desc") return b.is_total - a.is_total;
      if (sortBy === "amount-asc") return a.is_total - b.is_total;
      return b.created_at.localeCompare(a.created_at);
    });
  }, [items, query, regime, sortBy]);

  const totalPages = Math.max(Math.ceil(filtered.length / PAGE_SIZE), 1);
  const paginated = filtered.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);

  useEffect(() => {
    setPage(1);
  }, [query, regime, sortBy]);

  useEffect(() => {
    if (page > totalPages) setPage(totalPages);
  }, [page, totalPages]);

  return (
    <section className="space-y-5">
      <Card>
        <CardHeader>
          <CardTitle>Calculs sauvegardes</CardTitle>
          <CardDescription>Recherche, filtrage, tri et pagination de votre historique fiscal.</CardDescription>
        </CardHeader>
        <CardContent className="grid gap-3 md:grid-cols-4">
          <Input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Rechercher (SIREN, reference, regime)" />
          <select className="h-10 rounded-md border bg-background px-3 text-sm" value={regime} onChange={(event) => setRegime(event.target.value)}>
            <option value="all">Tous les regimes</option>
            <option value="PME 15%/25%">PME 15%/25%</option>
            <option value="Taux normal 25%">Taux normal 25%</option>
          </select>
          <select className="h-10 rounded-md border bg-background px-3 text-sm" value={sortBy} onChange={(event) => setSortBy(event.target.value)}>
            <option value="recent">Plus recents</option>
            <option value="amount-desc">IS decroissant</option>
            <option value="amount-asc">IS croissant</option>
          </select>
          <p className="self-center text-right text-sm text-muted-foreground">{filtered.length} resultat(s)</p>
        </CardContent>
      </Card>

      {loading ? (
        <div className="grid gap-4 md:grid-cols-2">
          <Skeleton className="h-48" />
          <Skeleton className="h-48" />
        </div>
      ) : (
        <>
          <div className="grid gap-4 md:grid-cols-2">
            {paginated.length > 0 ? (
              paginated.map((item) => <CalculationCard key={item.id} item={item} />)
            ) : (
              <Card className="md:col-span-2">
                <CardContent className="p-6 text-sm text-muted-foreground">Aucun calcul ne correspond aux filtres selectionnes.</CardContent>
              </Card>
            )}
          </div>
          <div className="flex items-center justify-between">
            <Button variant="outline" disabled={page <= 1} onClick={() => setPage((current) => Math.max(current - 1, 1))}>
              Precedent
            </Button>
            <p className="text-sm text-muted-foreground">
              Page {page} / {totalPages}
            </p>
            <Button variant="outline" disabled={page >= totalPages} onClick={() => setPage((current) => Math.min(current + 1, totalPages))}>
              Suivant
            </Button>
          </div>
        </>
      )}
    </section>
  );
}
