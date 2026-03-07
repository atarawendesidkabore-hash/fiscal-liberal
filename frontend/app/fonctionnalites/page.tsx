import Image from "next/image";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export const revalidate = 3600;

const features = [
  {
    title: "Calcul IS intelligent",
    description: "Moteur conforme Art. 219 CGI, gestion automatique des tranches 15% et 25%, simulation des acomptes.",
    screenshot: "Apercu calculateur IS"
  },
  {
    title: "Liasse 2058-A guidee",
    description: "Saisie structuree des lignes critiques avec alertes metier, controle de coherence et estimation immediate.",
    screenshot: "Apercu formulaire 2058-A"
  },
  {
    title: "Assistant fiscal IA",
    description: "Reponses rapides sur CGI, regimes speciaux, mere-filiale et obligations de conformite.",
    screenshot: "Apercu assistant IA"
  },
  {
    title: "Facturation et credits",
    description: "Suivi en temps reel des abonnements, consommation credits, factures et moyens de paiement.",
    screenshot: "Apercu tableau de facturation"
  }
];

export default function FonctionnalitesPage() {
  return (
    <section className="space-y-8">
      <header className="space-y-3">
        <Badge variant="secondary" className="w-fit">
          Fonctionnalites produit
        </Badge>
        <h1 className="text-3xl font-extrabold">Fonctionnalites</h1>
        <p className="max-w-3xl text-muted-foreground">
          Une interface complete pour les experts-comptables et fiscalistes qui veulent produire plus vite, avec une meilleure fiabilite.
        </p>
      </header>

      <div className="overflow-hidden rounded-xl border bg-card p-2">
        <Image
          src="/images/feature-ui.svg"
          alt="Apercu des ecrans fonctionnalites FiscIA Pro"
          width={900}
          height={560}
          className="h-auto w-full rounded-lg"
          sizes="(max-width: 1024px) 100vw, 900px"
        />
      </div>

      <div className="grid gap-5 md:grid-cols-2">
        {features.map((feature) => (
          <Card key={feature.title}>
            <CardHeader>
              <CardTitle>{feature.title}</CardTitle>
              <CardDescription>{feature.description}</CardDescription>
            </CardHeader>
            <CardContent>
              <div
                className="rounded-lg border border-dashed bg-gradient-to-br from-blue-50 to-blue-100/40 p-6 text-sm text-muted-foreground dark:from-slate-900 dark:to-slate-800"
                role="img"
                aria-label={feature.screenshot}
              >
                {feature.screenshot}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </section>
  );
}
