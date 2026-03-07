import Link from "next/link";
import { ReactNode } from "react";

const links = [
  { href: "/", label: "Landing" },
  { href: "/liasse", label: "Liasse 2058-A" },
  { href: "/is-calcul", label: "Calcul IS" },
  { href: "/recherche", label: "Recherche CGI" },
  { href: "/veille", label: "Veille" },
  { href: "/assistant", label: "Assistant" },
  { href: "/clients", label: "Clients" },
  { href: "/parametres", label: "Parametres" }
];

export default function DashboardLayout({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen md:grid md:grid-cols-[220px_1fr]">
      <aside className="border-r bg-white p-4">
        <h2 className="mb-4 font-bold text-fiscal-700">FiscIA Pro</h2>
        <nav className="space-y-2 text-sm">
          {links.map((link) => (
            <Link key={link.href} href={link.href} className="block rounded px-2 py-1 hover:bg-slate-100">
              {link.label}
            </Link>
          ))}
        </nav>
      </aside>
      <main className="p-6">{children}</main>
    </div>
  );
}

