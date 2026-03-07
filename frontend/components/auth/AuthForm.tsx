"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { useForm } from "react-hook-form";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";

type AuthMode = "connexion" | "inscription" | "mot-de-passe-oublie";

type AuthFormProps = {
  mode: AuthMode;
};

type FormValues = {
  cabinet: string;
  email: string;
  password: string;
  confirmPassword: string;
};

export default function AuthForm({ mode }: AuthFormProps) {
  const router = useRouter();
  const { login } = useAuth();
  const [error, setError] = useState<string | null>(null);
  const [sent, setSent] = useState(false);

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors, isSubmitting }
  } = useForm<FormValues>({
    defaultValues: { cabinet: "", email: "", password: "", confirmPassword: "" },
    mode: "onChange"
  });

  const onSubmit = async (values: FormValues) => {
    setError(null);
    if (mode === "connexion") {
      try {
        await login(values.email, values.password);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Connexion impossible.");
      }
      return;
    }

    if (mode === "inscription") {
      try {
        await api.register(values.cabinet, values.email, values.password, "starter");
        router.push("/tableau-de-bord");
      } catch (err) {
        setError(err instanceof Error ? err.message : "Inscription impossible.");
      }
      return;
    }

    await new Promise((resolve) => setTimeout(resolve, 700));
    setSent(true);
  };

  const title = mode === "connexion" ? "Connexion" : mode === "inscription" ? "Inscription" : "Reinitialiser le mot de passe";
  const description =
    mode === "connexion"
      ? "Connectez-vous a votre espace fiscal securise."
      : mode === "inscription"
        ? "Creez votre cabinet et demarrez vos calculs IA."
        : "Recevez un lien de reinitialisation par email.";

  return (
    <Card className="mx-auto w-full max-w-lg">
      <CardHeader>
        <CardTitle>{title}</CardTitle>
        <CardDescription>{description}</CardDescription>
      </CardHeader>
      <CardContent>
        <form className="space-y-4" onSubmit={handleSubmit(onSubmit)}>
          {mode === "inscription" ? (
            <div className="space-y-2">
              <Label htmlFor="cabinet">Nom du cabinet</Label>
              <Input id="cabinet" placeholder="Cabinet Dupont" {...register("cabinet", { required: "Nom obligatoire" })} />
              {errors.cabinet ? <p className="text-xs text-red-600">{errors.cabinet.message}</p> : null}
            </div>
          ) : null}

          <div className="space-y-2">
            <Label htmlFor="email">Email</Label>
            <Input
              id="email"
              type="email"
              placeholder="contact@cabinet.fr"
              {...register("email", {
                required: "Email obligatoire",
                pattern: { value: /\S+@\S+\.\S+/, message: "Format invalide" }
              })}
            />
            {errors.email ? <p className="text-xs text-red-600">{errors.email.message}</p> : null}
          </div>

          {mode !== "mot-de-passe-oublie" ? (
            <div className="space-y-2">
              <Label htmlFor="password">Mot de passe</Label>
              <Input
                id="password"
                type="password"
                {...register("password", {
                  required: "Mot de passe obligatoire",
                  minLength: { value: 8, message: "Minimum 8 caracteres" }
                })}
              />
              {errors.password ? <p className="text-xs text-red-600">{errors.password.message}</p> : null}
            </div>
          ) : null}

          {mode === "inscription" ? (
            <div className="space-y-2">
              <Label htmlFor="confirmPassword">Confirmer le mot de passe</Label>
              <Input
                id="confirmPassword"
                type="password"
                {...register("confirmPassword", {
                  required: "Confirmation obligatoire",
                  validate: (value) => value === watch("password") || "Les mots de passe ne correspondent pas"
                })}
              />
              {errors.confirmPassword ? <p className="text-xs text-red-600">{errors.confirmPassword.message}</p> : null}
            </div>
          ) : null}

          {error ? <p className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p> : null}
          {sent ? (
            <p className="rounded-md border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm text-emerald-700">
              Si cet email existe, un lien a ete envoye.
            </p>
          ) : null}

          <Button className="w-full" type="submit" disabled={isSubmitting}>
            {isSubmitting ? "Traitement..." : title}
          </Button>
        </form>

        {mode === "connexion" ? (
          <>
            <div className="my-4 grid grid-cols-2 gap-2">
              <Button variant="outline" type="button">
                Google
              </Button>
              <Button variant="outline" type="button">
                Microsoft
              </Button>
            </div>
            <div className="flex items-center justify-between text-sm">
              <Link href="/auth/mot-de-passe-oublie">Mot de passe oublie ?</Link>
              <Link href="/auth/inscription">Creer un compte</Link>
            </div>
          </>
        ) : null}

        {mode === "inscription" ? (
          <p className="mt-4 text-sm text-muted-foreground">
            Deja inscrit ? <Link href="/auth/connexion">Se connecter</Link>
          </p>
        ) : null}
      </CardContent>
    </Card>
  );
}

