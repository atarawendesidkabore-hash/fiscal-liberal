"use client";

import { useState } from "react";

import LiasseForm from "@/components/liasse/LiasseForm";
import { Card, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { api } from "@/lib/api";
import type { LiasseInput, LiasseResult } from "@/lib/types";

export default function LiassePage() {
  const [result, setResult] = useState<LiasseResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (liasse: LiasseInput, ca: number, capitalPp: boolean) => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.submitLiasse(liasse, ca, capitalPp);
      setResult(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erreur lors du calcul de la liasse.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="space-y-5">
      <Card>
        <CardHeader>
          <CardTitle>Liasse 2058-A</CardTitle>
          <CardDescription>Saisie guidee avec validation dynamique et preview RF.</CardDescription>
        </CardHeader>
      </Card>

      <LiasseForm isLoading={loading} error={error} result={result} onSubmit={handleSubmit} />
    </section>
  );
}

