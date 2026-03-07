"use client";

import { useEffect, useMemo, useState } from "react";

import CalculationCard from "@/components/calculs/CalculationCard";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import { api } from "@/lib/api";
import type { CalculationPreview } from "@/lib/types";

export default function CalculsPage() {
  const [items, setItems] = useState<CalculationPreview[]>([]);
  const [loading, setLoading] = useState(true);
  const [query, setQuery] = useState("");

  useEffect(() => {
    const load = async () => {
      const rows = await api.listCalculations();
      setItems(rows);
      setLoading(false);
    };
    void load();
  }, []);

  const filtered = useMemo(() => {
    const normalized = query.toLowerCase().trim();
    if (!normalized) return items;
    return items.filter(
      (item) =>
        item.siren.includes(normalized) ||
        item.regime.toLowerCase().includes(normalized) ||
        item.id.toLowerCase().includes(normalized)
    );
  }, [items, query]);

  return (
    <section className="space-y-5">
      <Card>
        <CardHeader>
          <CardTitle>Calculs sauvegardes</CardTitle>
          <CardDescription>Filtrez par SIREN, regime ou reference interne.</CardDescription>
        </CardHeader>
        <CardContent>
          <Input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Rechercher un calcul..." />
        </CardContent>
      </Card>

      {loading ? (
        <div className="grid gap-4 md:grid-cols-2">
          <Skeleton className="h-48" />
          <Skeleton className="h-48" />
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2">
          {filtered.map((item) => (
            <CalculationCard key={item.id} item={item} />
          ))}
        </div>
      )}
    </section>
  );
}

