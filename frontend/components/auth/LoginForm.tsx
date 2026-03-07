"use client";

import Link from "next/link";
import { useState } from "react";
import { useForm } from "react-hook-form";

import { useAuth } from "@/lib/auth";

type LoginFormData = {
  email: string;
  password: string;
};

export default function LoginForm() {
  const { login, error: authError, loading } = useAuth();
  const [localError, setLocalError] = useState<string | null>(null);
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting }
  } = useForm<LoginFormData>({
    mode: "onChange"
  });

  const onSubmit = async (values: LoginFormData) => {
    setLocalError(null);
    try {
      await login(values.email, values.password);
    } catch (error) {
      setLocalError(error instanceof Error ? error.message : "Connexion impossible.");
    }
  };

  return (
    <div className="card mx-auto w-full max-w-md p-6">
      <h1 className="text-2xl font-bold text-fiscia-900">Connexion cabinet</h1>
      <p className="mt-2 text-sm text-slate-600">Connectez-vous a votre espace fiscal securise.</p>

      <form className="mt-6 space-y-4" onSubmit={handleSubmit(onSubmit)}>
        <div>
          <label className="label" htmlFor="email">
            Email professionnel
          </label>
          <input
            id="email"
            type="email"
            className="input"
            placeholder="exemple@cabinet.fr"
            {...register("email", {
              required: "Email obligatoire",
              pattern: {
                value: /\S+@\S+\.\S+/,
                message: "Format email invalide"
              }
            })}
          />
          {errors.email ? <p className="mt-1 text-xs text-red-600">{errors.email.message}</p> : null}
        </div>

        <div>
          <label className="label" htmlFor="password">
            Mot de passe
          </label>
          <input
            id="password"
            type="password"
            className="input"
            {...register("password", {
              required: "Mot de passe obligatoire",
              minLength: { value: 8, message: "Minimum 8 caracteres" }
            })}
          />
          {errors.password ? <p className="mt-1 text-xs text-red-600">{errors.password.message}</p> : null}
        </div>

        {(localError || authError) && (
          <p className="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
            {localError || authError}
          </p>
        )}

        <button type="submit" disabled={isSubmitting || loading} className="btn-primary w-full">
          {isSubmitting || loading ? "Connexion..." : "Se connecter"}
        </button>
      </form>

      <div className="mt-5 space-y-3">
        <button type="button" className="btn-secondary w-full">
          Continuer avec Google
        </button>
        <button type="button" className="btn-secondary w-full">
          Continuer avec Microsoft
        </button>
      </div>

      <div className="mt-5 flex items-center justify-between text-sm">
        <Link href="/auth/forgot-password">Mot de passe oublie ?</Link>
        <Link href="/auth/register">Creer un compte</Link>
      </div>
    </div>
  );
}


