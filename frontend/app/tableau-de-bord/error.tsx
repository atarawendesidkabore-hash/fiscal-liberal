"use client";

import { useEffect } from "react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

type ErrorProps = {
  error: Error & { digest?: string };
  reset: () => void;
};

export default function DashboardError({ error, reset }: ErrorProps) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <section className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>Erreur du tableau de bord</CardTitle>
          <CardDescription>La vue demandee n&apos;a pas pu etre chargee.</CardDescription>
        </CardHeader>
        <CardContent className="flex gap-2">
          <Button type="button" onClick={reset}>
            Recharger la page
          </Button>
          <Button asChild variant="outline">
            <a href="/tableau-de-bord">Retour au tableau de bord</a>
          </Button>
        </CardContent>
      </Card>
    </section>
  );
}
