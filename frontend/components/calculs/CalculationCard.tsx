import Link from "next/link";
import { FileText } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import type { CalculationPreview } from "@/lib/types";

type CalculationCardProps = {
  item: CalculationPreview;
};

export default function CalculationCard({ item }: CalculationCardProps) {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-start justify-between gap-3">
          <div>
            <CardTitle className="text-lg">SIREN {item.siren}</CardTitle>
            <CardDescription>Cloture {item.exercice_clos}</CardDescription>
          </div>
          <Badge variant={item.regime.toLowerCase().includes("pme") ? "success" : "secondary"}>{item.regime}</Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-2 text-sm">
        <div className="flex items-center justify-between">
          <span className="text-muted-foreground">IS total</span>
          <span className="font-semibold tabular-nums">{item.is_total.toLocaleString("fr-FR")} EUR</span>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-muted-foreground">Derniere mise a jour</span>
          <span>{item.created_at}</span>
        </div>
      </CardContent>
      <CardFooter className="justify-between">
        <div className="flex items-center gap-2 text-xs text-muted-foreground">
          <FileText className="h-3.5 w-3.5" />
          Analyse IA disponible
        </div>
        <Button asChild variant="outline" size="sm">
          <Link href={`/tableau-de-bord/calculs/${item.id}`}>Voir</Link>
        </Button>
      </CardFooter>
    </Card>
  );
}

