"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import ThemeToggle from "@/components/theme/ThemeToggle";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { useAuth } from "@/lib/auth";

const navLinks = [
  { href: "/fonctionnalites", label: "Fonctionnalites" },
  { href: "/tarifs", label: "Tarifs" },
  { href: "/demo", label: "Demo" }
];

export default function Header() {
  const pathname = usePathname();
  const { user, logout, loading } = useAuth();

  return (
    <header className="sticky top-0 z-30 border-b bg-background/95 backdrop-blur">
      <div className="container-page flex h-16 items-center justify-between gap-4">
        <div className="flex items-center gap-6">
          <Link href="/" className="text-lg font-extrabold tracking-tight text-fiscia-900 dark:text-blue-200">
            FiscIA Pro
          </Link>
          <nav className="hidden items-center gap-5 md:flex">
            {navLinks.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                className={cn(
                  "text-sm text-muted-foreground transition hover:text-foreground",
                  pathname === link.href && "font-semibold text-foreground"
                )}
              >
                {link.label}
              </Link>
            ))}
          </nav>
        </div>

        <div className="flex items-center gap-2">
          <ThemeToggle />
          {user ? (
            <>
              <Button asChild variant="secondary">
                <Link href="/tableau-de-bord">Tableau de bord</Link>
              </Button>
              <Button type="button" onClick={() => void logout()} disabled={loading}>
                Deconnexion
              </Button>
            </>
          ) : (
            <>
              <Button asChild variant="outline">
                <Link href="/auth/connexion">Connexion</Link>
              </Button>
              <Button asChild>
                <Link href="/auth/inscription">Essai gratuit</Link>
              </Button>
            </>
          )}
        </div>
      </div>
    </header>
  );
}

