"use client";

import Link from "next/link";
import { useAuth } from "@/lib/auth-context";
import { marketingHref } from "@/lib/marketing-url";

export default function Navbar() {
  const { user, logout } = useAuth();
  const brandHref = user ? "/dashboard" : marketingHref("/");

  return (
    <nav className="bg-slate-900 text-white border-b border-slate-700">
      <div className="max-w-7xl mx-auto px-4 h-14 flex items-center justify-between">
        <Link href={brandHref} className="flex items-center gap-2 font-bold text-lg">
          <span className="text-blue-400">FiscIA</span>
          <span className="text-slate-400 text-sm font-normal">Pro</span>
        </Link>

        {user ? (
          <div className="flex items-center gap-6">
            <Link href="/dashboard" className="text-sm text-slate-300 hover:text-white transition">
              Tableau de bord
            </Link>
            <Link href="/liasse" className="text-sm text-slate-300 hover:text-white transition">
              Liasse 2058-A
            </Link>
            <Link
              href="/liasse/2065-2033"
              className="text-sm text-slate-300 hover:text-white transition"
            >
              2065 + 2033
            </Link>
            <div className="flex items-center gap-3 ml-4 pl-4 border-l border-slate-700">
              <div className="text-xs text-slate-400">
                <div>{user.email}</div>
                <div className="text-blue-400 capitalize">{user.role}</div>
              </div>
              <button
                onClick={logout}
                className="text-xs text-slate-400 hover:text-red-400 transition"
              >
                Deconnexion
              </button>
            </div>
          </div>
        ) : (
          <div className="flex gap-3">
            <Link
              href="/login"
              className="text-sm text-slate-300 hover:text-white transition"
            >
              Connexion
            </Link>
            <Link
              href="/register"
              className="text-sm bg-blue-600 hover:bg-blue-700 px-3 py-1.5 rounded transition"
            >
              Inscription
            </Link>
          </div>
        )}
      </div>
    </nav>
  );
}
