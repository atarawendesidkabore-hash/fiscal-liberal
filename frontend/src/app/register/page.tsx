"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { register, ApiError } from "@/lib/api";

export default function RegisterPage() {
  const router = useRouter();
  const [form, setForm] = useState({
    email: "",
    password: "",
    full_name: "",
    firm_name: "",
    firm_siren: "",
  });
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  function update(field: string, value: string) {
    setForm((prev) => ({ ...prev, [field]: value }));
  }

  useEffect(() => {
    const email = new URLSearchParams(window.location.search).get("email");
    if (!email) return;
    setForm((prev) => (prev.email === email ? prev : { ...prev, email }));
  }, []);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      await register({
        email: form.email,
        password: form.password,
        full_name: form.full_name,
        firm_name: form.firm_name || undefined,
        firm_siren: form.firm_siren || undefined,
      });
      router.push(`/login?registered=1&email=${encodeURIComponent(form.email)}`);
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError("Erreur lors de l'inscription");
      }
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="flex items-center justify-center min-h-[70vh]">
      <div className="bg-slate-900 border border-slate-800 rounded-lg p-8 w-full max-w-md">
        <h1 className="text-2xl font-bold mb-6 text-center">Inscription</h1>

        {error && (
          <div className="bg-red-900/30 border border-red-800 text-red-300 text-sm rounded p-3 mb-4">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm text-slate-400 mb-1">Nom complet</label>
            <input
              type="text"
              required
              value={form.full_name}
              onChange={(e) => update("full_name", e.target.value)}
              className="w-full bg-slate-800 border border-slate-700 rounded px-3 py-2 text-white focus:border-blue-500 focus:outline-none"
              placeholder="Jean Dupont"
            />
          </div>

          <div>
            <label className="block text-sm text-slate-400 mb-1">Email</label>
            <input
              type="email"
              required
              value={form.email}
              onChange={(e) => update("email", e.target.value)}
              className="w-full bg-slate-800 border border-slate-700 rounded px-3 py-2 text-white focus:border-blue-500 focus:outline-none"
              placeholder="jean@cabinet.fr"
            />
          </div>

          <div>
            <label className="block text-sm text-slate-400 mb-1">
              Mot de passe <span className="text-slate-600">(8 caracteres min)</span>
            </label>
            <input
              type="password"
              required
              minLength={8}
              value={form.password}
              onChange={(e) => update("password", e.target.value)}
              className="w-full bg-slate-800 border border-slate-700 rounded px-3 py-2 text-white focus:border-blue-500 focus:outline-none"
            />
          </div>

          <hr className="border-slate-800" />

          <p className="text-xs text-slate-500">
            Optionnel : creer un cabinet (vous serez administrateur)
          </p>

          <div>
            <label className="block text-sm text-slate-400 mb-1">Nom du cabinet</label>
            <input
              type="text"
              value={form.firm_name}
              onChange={(e) => update("firm_name", e.target.value)}
              className="w-full bg-slate-800 border border-slate-700 rounded px-3 py-2 text-white focus:border-blue-500 focus:outline-none"
              placeholder="Cabinet Dupont & Associes"
            />
          </div>

          <div>
            <label className="block text-sm text-slate-400 mb-1">SIREN du cabinet</label>
            <input
              type="text"
              maxLength={9}
              pattern="\d{9}"
              value={form.firm_siren}
              onChange={(e) => update("firm_siren", e.target.value)}
              className="w-full bg-slate-800 border border-slate-700 rounded px-3 py-2 text-white focus:border-blue-500 focus:outline-none"
              placeholder="123456789"
            />
          </div>

          <button
            type="submit"
            disabled={submitting}
            className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-800 disabled:cursor-not-allowed text-white py-2.5 rounded font-medium transition"
          >
            {submitting ? "Inscription..." : "Creer mon compte"}
          </button>
        </form>

        <p className="text-center text-sm text-slate-500 mt-6">
          Deja un compte ?{" "}
          <Link href="/login" className="text-blue-400 hover:underline">
            Connexion
          </Link>
        </p>
      </div>
    </div>
  );
}
