import Link from "next/link";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";

const plans = [
  {
    name: "Starter",
    price: "29",
    description: "Pour independants et petites structures",
    features: ["50 calculs / mois", "Recherche CGI", "Veille fiscale"],
    cta: "Choisir Starter"
  },
  {
    name: "Pro",
    price: "79",
    description: "Pour cabinets 1 a 5 associes",
    features: ["Calculs illimites", "Liasse 2058-A complete", "Assistant fiscal IA"],
    cta: "Choisir Pro",
    highlight: true
  },
  {
    name: "Cabinet",
    price: "199",
    description: "Pour structures multi-equipes",
    features: ["Utilisateurs multiples", "API & integrations", "Support prioritaire"],
    cta: "Choisir Cabinet"
  }
];

export default function TarifsPage() {
  return (
    <section className="space-y-8">
      <header className="space-y-2 text-center">
        <h1 className="text-3xl font-extrabold">Tarifs FiscIA Pro</h1>
        <p className="text-muted-foreground">Trois offres simples adaptees a la realite des cabinets fiscaux.</p>
      </header>

      <div className="grid gap-5 md:grid-cols-3">
        {plans.map((plan) => (
          <Card key={plan.name} className={plan.highlight ? "border-primary shadow-lg" : ""}>
            <CardHeader>
              {plan.highlight ? <Badge className="w-fit">Plan recommande</Badge> : null}
              <CardTitle>{plan.name}</CardTitle>
              <CardDescription>{plan.description}</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-4xl font-extrabold tabular-nums">{plan.price}€</p>
              <p className="text-sm text-muted-foreground">/ mois</p>
              <ul className="mt-4 space-y-2 text-sm">
                {plan.features.map((feature) => (
                  <li key={feature}>• {feature}</li>
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
    </section>
  );
}

