"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useAuth } from "@/lib/auth-context";
import { listSavedLiasses, deleteSavedLiasse, type SavedLiasse, ApiError } from "@/lib/api";
import ProtectedRoute from "@/components/protected-route";

export default function DashboardPage() {
  return (
    <ProtectedRoute>
      <Dashboard />
    </ProtectedRoute>
  );
}

function Dashboard() {
  const { user, token } = useAuth();
  const [records, setRecords] = useState<SavedLiasse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function load() {
    if (!token) return;
    setLoading(true);
    try {
      const data = await listSavedLiasses(token);
      setRecords(data.results);
    } catch (err) {
      setError("Erreur lors du chargement");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, [token]);

  async function handleDelete(id: string) {
    if (!confirm("Supprimer ce calcul ?")) return;
    try {
      await deleteSavedLiasse(token!, id);
      setRecords((prev) => prev.filter((r) => r.id !== id));
    } catch (err) {
      if (err instanceof ApiError) {
        alert(err.message);
      }
    }
  }

  const fmt = (n: number) =>
    new Intl.NumberFormat("fr-FR", { style: "currency", currency: "EUR" }).format(n);

  return (
    <div className="max-w-5xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold">Tableau de bord</h1>
          <p className="text-slate-400 text-sm mt-1">
            {user?.email} — <span className="text-blue-400 capitalize">{user?.role}</span>
          </p>
        </div>
        <div className="flex gap-3">
          <Link
            href="/liasse"
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition"
          >
            + Nouveau 2058-A
          </Link>
          <Link
            href="/liasse/2065-2033"
            className="border border-slate-700 hover:border-blue-500 text-slate-200 px-4 py-2 rounded-lg text-sm font-medium transition"
          >
            + Nouveau 2065 + 2033
          </Link>
          <Link
            href="/liasse/2058-b-c"
            className="border border-slate-700 hover:border-blue-500 text-slate-200 px-4 py-2 rounded-lg text-sm font-medium transition"
          >
            + Nouveau 2058-B/C
          </Link>
        </div>
      </div>

      {/* Stats row */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <div className="bg-slate-900 border border-slate-800 rounded-lg p-5">
          <div className="text-xs text-slate-500 uppercase">Calculs sauvegardes</div>
          <div className="text-3xl font-bold mt-1">{records.length}</div>
        </div>
        <div className="bg-slate-900 border border-slate-800 rounded-lg p-5">
          <div className="text-xs text-slate-500 uppercase">IS total cumule</div>
          <div className="text-3xl font-bold mt-1 text-blue-400">
            {fmt(records.reduce((sum, r) => sum + r.is_total, 0))}
          </div>
        </div>
        <div className="bg-slate-900 border border-slate-800 rounded-lg p-5">
          <div className="text-xs text-slate-500 uppercase">SIREN distincts</div>
          <div className="text-3xl font-bold mt-1">
            {new Set(records.map((r) => r.siren)).size}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <Link
          href="/liasse"
          className="bg-slate-900 border border-slate-800 rounded-lg p-5 transition hover:border-blue-500"
        >
          <div className="text-xs uppercase text-slate-500">Module actif</div>
          <div className="mt-2 text-lg font-semibold text-white">Liasse 2058-A</div>
          <p className="mt-2 text-sm text-slate-400">
            Calculez le resultat fiscal et l&apos;IS avec import de fichiers.
          </p>
        </Link>
        <Link
          href="/liasse/2065-2033"
          className="bg-slate-900 border border-slate-800 rounded-lg p-5 transition hover:border-blue-500"
        >
          <div className="text-xs uppercase text-blue-400">Nouveau module</div>
          <div className="mt-2 text-lg font-semibold text-white">Preparation 2065 + 2033</div>
          <p className="mt-2 text-sm text-slate-400">
            Pre-remplissez votre dossier IS puis basculez vers le 2058-A.
          </p>
        </Link>
        <Link
          href="/liasse/2058-b-c"
          className="bg-slate-900 border border-slate-800 rounded-lg p-5 transition hover:border-blue-500"
        >
          <div className="text-xs uppercase text-emerald-400">Nouveau module</div>
          <div className="mt-2 text-lg font-semibold text-white">Preparation 2058-B / 2058-C</div>
          <p className="mt-2 text-sm text-slate-400">
            Finalisez les reports, acomptes, credits d&apos;impot et le solde d&apos;IS.
          </p>
        </Link>
      </div>

      {error && (
        <div className="bg-red-900/30 border border-red-800 text-red-300 text-sm rounded p-3 mb-4">
          {error}
        </div>
      )}

      {loading ? (
        <div className="text-slate-400 text-center py-12">Chargement...</div>
      ) : records.length === 0 ? (
        <div className="text-center py-16">
          <p className="text-slate-500 mb-4">Aucun calcul sauvegarde</p>
          <div className="flex justify-center gap-4">
            <Link
              href="/liasse"
              className="text-blue-400 hover:underline"
            >
              Effectuer votre premier calcul 2058-A
            </Link>
            <Link
              href="/liasse/2065-2033"
              className="text-slate-300 hover:underline"
            >
              Commencer un dossier 2065 + 2033
            </Link>
            <Link
              href="/liasse/2058-b-c"
              className="text-slate-300 hover:underline"
            >
              Ouvrir la preparation 2058-B / 2058-C
            </Link>
          </div>
        </div>
      ) : (
        <div className="bg-slate-900 border border-slate-800 rounded-lg overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-slate-800/50 text-left text-slate-400">
                <th className="px-4 py-3">SIREN</th>
                <th className="px-4 py-3">Exercice</th>
                <th className="px-4 py-3">RF Brut</th>
                <th className="px-4 py-3">IS Total</th>
                <th className="px-4 py-3">Regime</th>
                <th className="px-4 py-3">Date</th>
                <th className="px-4 py-3"></th>
              </tr>
            </thead>
            <tbody>
              {records.map((r) => (
                <tr key={r.id} className="border-t border-slate-800 hover:bg-slate-800/30">
                  <td className="px-4 py-3 font-mono">{r.siren}</td>
                  <td className="px-4 py-3">{r.exercice_clos}</td>
                  <td className="px-4 py-3 font-mono">{fmt(r.rf_brut)}</td>
                  <td className="px-4 py-3 font-mono text-blue-400">{fmt(r.is_total)}</td>
                  <td className="px-4 py-3 text-xs">
                    <span className={`px-2 py-0.5 rounded ${
                      r.regime.includes("PME")
                        ? "bg-green-900/30 text-green-400"
                        : "bg-slate-800 text-slate-400"
                    }`}>
                      {r.regime.includes("PME") ? "PME" : "Normal"}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-slate-500 text-xs">
                    {r.created_at ? new Date(r.created_at).toLocaleDateString("fr-FR") : "—"}
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex gap-2">
                      <Link
                        href={`/resultats?id=${r.id}`}
                        className="text-xs text-blue-400 hover:underline"
                      >
                        Voir
                      </Link>
                      <button
                        onClick={() => handleDelete(r.id)}
                        className="text-xs text-red-400 hover:underline"
                      >
                        Suppr.
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
