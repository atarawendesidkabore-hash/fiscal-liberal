import Link from "next/link";

export default function Footer() {
  return (
    <footer className="border-t bg-background">
      <div className="container-page flex flex-col gap-3 py-8 text-sm text-muted-foreground md:flex-row md:items-center md:justify-between">
        <p>&copy; {new Date().getFullYear()} FiscIA Pro. Solution IA pour fiscalistes francais.</p>
        <div className="flex flex-wrap gap-4" aria-label="Liens de pied de page">
          <Link href="/fonctionnalites">Fonctionnalites</Link>
          <Link href="/tarification">Tarification</Link>
          <Link href="/demo">Demo</Link>
          <a href="mailto:support@fiscia.pro">Support</a>
        </div>
      </div>
    </footer>
  );
}
