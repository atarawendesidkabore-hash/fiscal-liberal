"use client";

import { useMemo, useState } from "react";
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
  const [usageCount, setUsageCount] = useState(0);
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

  const runDemo = () => {
    setUsageCount((current) => Math.min(current + 1, 5));
  };

  return (
    <section className="grid gap-6 lg:grid-cols-[1.4fr,1fr]">
      <Card>
        <CardHeader>
          <CardTitle>Demo calcul IS</CardTitle>
          <CardDescription>Simulation limitee a 5 executions pour decouvrir FiscIA Pro.</CardDescription>
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
            Capital detenu {">="} 75% personnes physiques
          </label>

          <div className="flex flex-wrap items-center gap-2">
            <Button type="button" onClick={runDemo} disabled={usageCount >= 5}>
              Lancer la simulation
            </Button>
            <Badge variant={usageCount >= 5 ? "destructive" : "secondary"}>Usage demo: {usageCount}/5</Badge>
          </div>
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
          <p className="text-xs text-muted-foreground">Pour des calculs reellement sauvegardes et exportables, creez un compte.</p>
        </CardContent>
      </Card>
    </section>
  );
}
