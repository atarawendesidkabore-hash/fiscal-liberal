import Link from "next/link";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";

const valueProps = [
  "Calcul IS conforme Art. 219 CGI",
  "Assistant 2058-A avec controles ligne par ligne",
  "Facturation Stripe et gestion credits",
  "RGPD by design et journalisation des actions"
];

const testimonials = [
  {
    name: "Cabinet Martin & Associes",
    quote: "Nous avons reduit de 40% le temps passe sur les recherches CGI hebdomadaires.",
    role: "Expert-comptable"
  },
  {
    name: "Fiscal Conseil Ouest",
    quote: "La saisie 2058-A guidee a diminue les erreurs de production sur les dossiers PME.",
    role: "Fiscaliste senior"
  }
];

export default function HomePage() {
  return (
    <section className="space-y-10">
      <div className="rounded-2xl border bg-gradient-to-r from-fiscia-900 via-fiscia-700 to-fiscia-600 p-8 text-white shadow-xl md:p-12">
        <Badge variant="secondary" className="bg-white/20 text-white">SaaS fiscal francais</Badge>
        <h1 className="mt-4 max-w-3xl text-4xl font-extrabold tracking-tight md:text-5xl">
          L'interface IA professionnelle pour fiscalistes et experts-comptables.
        </h1>
        <p className="mt-4 max-w-2xl text-blue-100">
          FiscIA Pro centralise calculs IS, liasse 2058-A, assistant fiscal et facturation cabinet sur une interface fiable.
        </p>
        <div className="mt-7 flex flex-wrap gap-3">
          <Button asChild size="lg" className="bg-white text-fiscia-900 hover:bg-slate-100">
            <Link href="/auth/inscription">Demarrer gratuitement</Link>
          </Button>
          <Button asChild size="lg" variant="outline" className="border-white/50 bg-transparent text-white hover:bg-white/10">
            <Link href="/demo">Voir la demo</Link>
          </Button>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        {valueProps.map((item) => (
          <Card key={item}>
            <CardContent className="p-5 text-sm font-medium">{item}</CardContent>
          </Card>
        ))}
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        {testimonials.map((testimonial) => (
          <Card key={testimonial.name}>
            <CardContent className="space-y-3 p-6">
              <p className="text-sm text-muted-foreground">"{testimonial.quote}"</p>
              <div>
                <p className="font-semibold">{testimonial.name}</p>
                <p className="text-xs text-muted-foreground">{testimonial.role}</p>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </section>
  );
}

