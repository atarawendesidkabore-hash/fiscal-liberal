import Link from "next/link";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";

export const revalidate = 3600;

const plans = [
  {
    name: "Starter",
    price: "29 EUR/mois",
    description: "Independants et petites structures",
    features: ["50 calculs/mois", "Recherche CGI", "Veille fiscale"],
    cta: "Commencer"
  },
  {
    name: "Pro",
    price: "79 EUR/mois",
    description: "Cabinets 1 a 5 associes",
    features: ["Calculs illimites", "Liasse 2058-A", "Assistant IA", "Facturation complete"],
    cta: "Choisir Pro",
    highlight: true
  },
  {
    name: "Cabinet",
    price: "199 EUR/mois",
    description: "Structures equipees",
    features: ["Multi-utilisateurs", "Gestion equipe", "API access", "Support prioritaire"],
    cta: "Passer en Cabinet"
  }
];

const comparison = [
  { feature: "Calcul IS", starter: "Oui", pro: "Oui", cabinet: "Oui" },
  { feature: "Liasse 2058-A intelligente", starter: "Limitee", pro: "Complete", cabinet: "Complete" },
  { feature: "Assistant IA fiscal", starter: "Basique", pro: "Avance", cabinet: "Avance" },
  { feature: "Gestion equipe", starter: "Non", pro: "Non", cabinet: "Oui" },
  { feature: "Support", starter: "Email", pro: "Prioritaire", cabinet: "Dedie" }
];

export default function TarificationPage() {
  return (
    <section className="space-y-10">
      <header className="space-y-2 text-center">
        <h1 className="text-3xl font-extrabold">Tarification claire pour cabinets fiscaux</h1>
        <p className="text-muted-foreground">Choisissez la formule qui correspond a votre volume de production.</p>
      </header>

      <div className="grid gap-5 md:grid-cols-3">
        {plans.map((plan) => (
          <Card key={plan.name} className={plan.highlight ? "border-primary shadow-lg" : ""}>
            <CardHeader>
              {plan.highlight ? <Badge className="w-fit">Le plus choisi</Badge> : null}
              <CardTitle>{plan.name}</CardTitle>
              <CardDescription>{plan.description}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              <p className="text-3xl font-extrabold tabular-nums">{plan.price}</p>
              <ul className="space-y-1 text-sm">
                {plan.features.map((feature) => (
                  <li key={feature}>- {feature}</li>
                ))}
              </ul>
            </CardContent>
            <CardFooter>
              <Button asChild className="w-full" variant={plan.highlight ? "default" : "outline"}>
                <Link href="/auth/inscription">{plan.cta}</Link>
              </Button>
            </CardFooter>
          </Card>
        ))}
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Tableau comparatif</CardTitle>
          <CardDescription>Vision rapide des fonctionnalites par plan.</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full min-w-[680px] text-sm">
              <thead>
                <tr className="border-b text-left text-muted-foreground">
                  <th className="py-2">Fonctionnalite</th>
                  <th className="py-2">Starter</th>
                  <th className="py-2">Pro</th>
                  <th className="py-2">Cabinet</th>
                </tr>
              </thead>
              <tbody>
                {comparison.map((row) => (
                  <tr key={row.feature} className="border-b">
                    <td className="py-2 font-medium">{row.feature}</td>
                    <td className="py-2">{row.starter}</td>
                    <td className="py-2">{row.pro}</td>
                    <td className="py-2">{row.cabinet}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </section>
  );
}
