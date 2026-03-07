import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

const features = [
  {
    title: "Calcul IS intelligent",
    description: "Moteur conforme Art. 219 CGI, gestion taux 15% / 25%, simulation acomptes.",
    screenshot: "Vue calculateur IS"
  },
  {
    title: "Liasse 2058-A guidee",
    description: "Saisie structuree des lignes critiques avec alertes contextuelles et preview RF.",
    screenshot: "Formulaire 2058-A interactif"
  },
  {
    title: "Assistant fiscal IA",
    description: "Questions libres sur CGI, regimes speciaux, mere-filiale et risques de conformité.",
    screenshot: "Chat fiscaliste"
  },
  {
    title: "Facturation et credits",
    description: "Pilotage Stripe en temps reel: abonnements, consommation credits, factures.",
    screenshot: "Dashboard facturation"
  }
];

export default function FonctionnalitesPage() {
  return (
    <section className="space-y-8">
      <header className="space-y-2">
        <h1 className="text-3xl font-extrabold">Fonctionnalites</h1>
        <p className="text-muted-foreground">Une interface complete pour la production fiscale quotidienne.</p>
      </header>

      <div className="grid gap-5 md:grid-cols-2">
        {features.map((feature) => (
          <Card key={feature.title}>
            <CardHeader>
              <CardTitle>{feature.title}</CardTitle>
              <CardDescription>{feature.description}</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="rounded-lg border border-dashed bg-muted/50 p-6 text-sm text-muted-foreground">{feature.screenshot}</div>
            </CardContent>
          </Card>
        ))}
      </div>
    </section>
  );
}

