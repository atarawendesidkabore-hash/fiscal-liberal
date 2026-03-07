"use client";

import Link from "next/link";
import { Menu, X } from "lucide-react";
import { usePathname } from "next/navigation";
import { useState } from "react";

import ThemeToggle from "@/components/theme/ThemeToggle";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { useAuth } from "@/lib/auth";

const navLinks = [
  { href: "/fonctionnalites", label: "Fonctionnalites" },
  { href: "/tarification", label: "Tarification" },
  { href: "/demo", label: "Demo" }
];

export default function Header() {
  const pathname = usePathname();
  const { user, logout, loading } = useAuth();
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <header className="sticky top-0 z-30 border-b bg-background/95 backdrop-blur">
      <div className="container-page flex h-16 items-center justify-between gap-4">
        <div className="flex items-center gap-6">
          <Link href="/" className="text-lg font-extrabold tracking-tight text-fiscia-900 dark:text-blue-200">
            FiscIA Pro
          </Link>
          <nav aria-label="Navigation principale" className="hidden items-center gap-5 md:flex">
            {navLinks.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                aria-current={pathname === link.href ? "page" : undefined}
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

        <div className="hidden items-center gap-2 md:flex">
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

        <div className="flex items-center gap-2 md:hidden">
          <ThemeToggle />
          <Button
            variant="outline"
            size="icon"
            aria-label={mobileOpen ? "Fermer le menu" : "Ouvrir le menu"}
            aria-expanded={mobileOpen}
            aria-controls="mobile-nav"
            onClick={() => setMobileOpen((open) => !open)}
          >
            {mobileOpen ? <X className="h-4 w-4" /> : <Menu className="h-4 w-4" />}
          </Button>
        </div>
      </div>

      {mobileOpen ? (
        <div id="mobile-nav" className="border-t bg-background md:hidden">
          <div className="container-page space-y-3 py-4">
            <nav aria-label="Navigation mobile" className="flex flex-col gap-2">
              {navLinks.map((link) => (
                <Link
                  key={link.href}
                  href={link.href}
                  aria-current={pathname === link.href ? "page" : undefined}
                  className="rounded-md px-3 py-2 text-sm hover:bg-muted"
                  onClick={() => setMobileOpen(false)}
                >
                  {link.label}
                </Link>
              ))}
            </nav>
            <div className="flex flex-col gap-2">
              {user ? (
                <>
                  <Button asChild variant="secondary" onClick={() => setMobileOpen(false)}>
                    <Link href="/tableau-de-bord">Tableau de bord</Link>
                  </Button>
                  <Button
                    type="button"
                    onClick={() => {
                      setMobileOpen(false);
                      void logout();
                    }}
                    disabled={loading}
                  >
                    Deconnexion
                  </Button>
                </>
              ) : (
                <>
                  <Button asChild variant="outline" onClick={() => setMobileOpen(false)}>
                    <Link href="/auth/connexion">Connexion</Link>
                  </Button>
                  <Button asChild onClick={() => setMobileOpen(false)}>
                    <Link href="/auth/inscription">Essai gratuit</Link>
                  </Button>
                </>
              )}
            </div>
          </div>
        </div>
      ) : null}
    </header>
  );
}
