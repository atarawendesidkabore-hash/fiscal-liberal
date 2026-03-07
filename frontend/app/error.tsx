"use client";

import { useEffect } from "react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

type ErrorProps = {
  error: Error & { digest?: string };
  reset: () => void;
};

export default function GlobalError({ error, reset }: ErrorProps) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <html lang="fr">
      <body className="bg-background p-6">
        <main className="mx-auto max-w-xl">
          <Card>
            <CardHeader>
              <CardTitle>Une erreur est survenue</CardTitle>
              <CardDescription>Impossible d'afficher cette page pour le moment.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              <p className="text-sm text-muted-foreground">Vous pouvez reessayer ou revenir a l'accueil.</p>
              <div className="flex gap-2">
                <Button type="button" onClick={reset}>
                  Reessayer
                </Button>
                <Button asChild variant="outline">
                  <a href="/">Retour accueil</a>
                </Button>
              </div>
            </CardContent>
          </Card>
        </main>
      </body>
    </html>
  );
}
