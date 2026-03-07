"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useAuth } from "@/lib/auth";

type SettingsForm = {
  email: string;
  receiveAlerts: boolean;
  dataExport: boolean;
  autoDeleteAuditAfterYears: string;
};

export default function ReglagesPage() {
  const { user } = useAuth();
  const [saved, setSaved] = useState(false);
  const { register, handleSubmit } = useForm<SettingsForm>({
    defaultValues: {
      email: user?.email ?? "",
      receiveAlerts: true,
      dataExport: false,
      autoDeleteAuditAfterYears: "10"
    }
  });

  const submit = async () => {
    await new Promise((resolve) => setTimeout(resolve, 500));
    setSaved(true);
  };

  return (
    <section className="space-y-5">
      <Card>
        <CardHeader>
          <CardTitle>Reglages et conformite RGPD</CardTitle>
          <CardDescription>Controle du profil, notifications et conservation des donnees.</CardDescription>
        </CardHeader>
      </Card>

      <form className="space-y-4" onSubmit={handleSubmit(submit)}>
        <Card>
          <CardHeader>
            <CardTitle>Profil</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="space-y-2">
              <Label htmlFor="email">Email utilisateur</Label>
              <Input id="email" type="email" {...register("email")} />
            </div>
            <label className="inline-flex items-center gap-2 text-sm text-muted-foreground">
              <input type="checkbox" {...register("receiveAlerts")} />
              Recevoir les alertes fiscales hebdomadaires
            </label>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>RGPD</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <label className="inline-flex items-center gap-2 text-sm text-muted-foreground">
              <input type="checkbox" {...register("dataExport")} />
              Activer export automatique des donnees utilisateur
            </label>
            <div className="space-y-2">
              <Label htmlFor="autoDeleteAuditAfterYears">Retention journaux d&apos;audit (annees)</Label>
              <Input id="autoDeleteAuditAfterYears" type="number" min="1" max="10" {...register("autoDeleteAuditAfterYears")} />
            </div>
          </CardContent>
        </Card>

        <Button type="submit">Sauvegarder les reglages</Button>
        {saved ? <p className="text-sm text-emerald-700">Reglages sauvegardes.</p> : null}
      </form>
    </section>
  );
}

