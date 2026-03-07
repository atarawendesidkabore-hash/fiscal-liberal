"use client";

import { useMemo } from "react";
import { useForm } from "react-hook-form";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

type DemoData = {
  rf: string;
  ca: string;
  capitalPp: boolean;
};

export default function DemoPage() {
  const { register, watch } = useForm<DemoData>({
    defaultValues: { rf: "100000", ca: "6500000", capitalPp: true },
    mode: "onChange"
  });

  const values = watch();

  const result = useMemo(() => {
    const rf = Number(values.rf || 0);
    const ca = Number(values.ca || 0);
    const pme = Boolean(values.capitalPp) && ca < 10_000_000;
    const is = pme ? Math.min(rf, 42500) * 0.15 + Math.max(rf - 42500, 0) * 0.25 : rf * 0.25;
    return { pme, is };
  }, [values]);

  return (
    <section className="grid gap-6 lg:grid-cols-[1.4fr,1fr]">
      <Card>
        <CardHeader>
          <CardTitle>Demo calcul IS</CardTitle>
          <CardDescription>Simulation locale (non sauvegardee) pour decouvrir l'interface.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <div className="space-y-2">
              <Label htmlFor="rf">Resultat fiscal</Label>
              <Input id="rf" type="number" {...register("rf")} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="ca">CA HT</Label>
              <Input id="ca" type="number" {...register("ca")} />
            </div>
          </div>
          <label className="inline-flex items-center gap-2 text-sm text-muted-foreground">
            <input type="checkbox" {...register("capitalPp")} />
            Capital detenu {"\u003e="} 75% personnes physiques
          </label>
          <Button type="button" disabled>
            Simulation en direct
          </Button>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Resultat demo</CardTitle>
          <CardDescription>Affichage instantane</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          <Badge variant={result.pme ? "success" : "secondary"}>{result.pme ? "Regime PME" : "Regime normal"}</Badge>
          <p className="text-sm text-muted-foreground">IS estime</p>
          <p className="text-3xl font-extrabold tabular-nums">{result.is.toLocaleString("fr-FR")} EUR</p>
          <p className="text-xs text-muted-foreground">Pour passer en production, connectez-vous pour lancer un vrai calcul avec audit RGPD.</p>
        </CardContent>
      </Card>
    </section>
  );
}

