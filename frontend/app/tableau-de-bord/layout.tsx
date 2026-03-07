import Link from "next/link";
import type { ReactNode } from "react";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";

const links = [
  { href: "/tableau-de-bord", label: "Accueil" },
  { href: "/tableau-de-bord/calculs", label: "Calculs" },
  { href: "/tableau-de-bord/liasse", label: "Liasse 2058-A" },
  { href: "/tableau-de-bord/fiscaliste", label: "Assistant IA" },
  { href: "/tableau-de-bord/facturation", label: "Facturation" },
  { href: "/tableau-de-bord/equipe", label: "Equipe" },
  { href: "/tableau-de-bord/reglages", label: "Reglages" }
];

export default function TableauDeBordLayout({ children }: { children: ReactNode }) {
  return (
    <div className="grid gap-6 lg:grid-cols-[260px,1fr]">
      <Card className="h-fit">
        <CardContent className="space-y-4 p-4">
          <div className="space-y-2">
            <p className="text-xs uppercase tracking-wide text-muted-foreground">Navigation cabinet</p>
            <Badge variant="secondary">Plan actif</Badge>
          </div>
          <nav className="flex flex-col gap-1">
            {links.map((link) => (
              <Link key={link.href} href={link.href} className="rounded-md px-3 py-2 text-sm hover:bg-muted">
                {link.label}
              </Link>
            ))}
          </nav>
        </CardContent>
      </Card>
      <div>{children}</div>
    </div>
  );
}

