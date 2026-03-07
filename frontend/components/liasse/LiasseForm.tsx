"use client";

import { useMemo } from "react";
import { useForm } from "react-hook-form";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Skeleton } from "@/components/ui/skeleton";
import type { LiasseInput, LiasseResult } from "@/lib/types";

type LiasseFormData = LiasseInput & {
  ca: string;
  capital_pp: boolean;
};

type LiasseFormProps = {
  isLoading: boolean;
  error?: string | null;
  result?: LiasseResult | null;
  onSubmit: (liasse: LiasseInput, ca: number, capitalPp: boolean) => Promise<void>;
};

const rows: Array<{ key: keyof LiasseInput; label: string; hint: string }> = [
  { key: "benefice_comptable", label: "WA - Benefice comptable", hint: "Resultat comptable avant retraitements" },
  { key: "perte_comptable", label: "WQ - Perte comptable", hint: "A renseigner si perte comptable" },
  { key: "wi_is_comptabilise", label: "WI - IS comptabilise", hint: "Toujours reintegre (Art. 213 CGI)" },
  { key: "wg_amendes_penalites", label: "WG - Amendes / penalites", hint: "Non deductible (Art. 39-2 CGI)" },
  { key: "wm_interets_excedentaires", label: "WM - Interets excedentaires", hint: "Controle plafonds Art. 39 et 212" },
  { key: "wn_reintegrations_diverses", label: "WN - Reintegrations diverses", hint: "Dont quote-part mere-filiale" },
  { key: "wv_regime_mere_filiale", label: "WV - Regime mere-filiale", hint: "Deduction sous 6 conditions Art.145" },
  { key: "l8_qp_12pct", label: "L8 - Quote-part 12% PV LT", hint: "Reintegration obligatoire sur PV LT" }
];

function numberOrZero(value: string) {
  const numeric = Number(value);
  return Number.isFinite(numeric) ? numeric : 0;
}

export default function LiasseForm({ isLoading, error, result, onSubmit }: LiasseFormProps) {
  const {
    register,
    handleSubmit,
    watch,
    formState: { errors, isSubmitting }
  } = useForm<LiasseFormData>({
    mode: "onChange",
    defaultValues: {
      siren: "",
      exercice_clos: "2024-12-31",
      benefice_comptable: "0",
      perte_comptable: "0",
      wi_is_comptabilise: "0",
      wg_amendes_penalites: "0",
      wm_interets_excedentaires: "0",
      wn_reintegrations_diverses: "0",
      wv_regime_mere_filiale: "0",
      l8_qp_12pct: "0",
      ca: "0",
      capital_pp: false
    }
  });

  const watchValues = watch();

  const preview = useMemo(() => {
    const rc = numberOrZero(watchValues.benefice_comptable) - numberOrZero(watchValues.perte_comptable);
    const reintegrations =
      numberOrZero(watchValues.wi_is_comptabilise) +
      numberOrZero(watchValues.wg_amendes_penalites) +
      numberOrZero(watchValues.wm_interets_excedentaires) +
      numberOrZero(watchValues.wn_reintegrations_diverses) +
      numberOrZero(watchValues.l8_qp_12pct);
    const deductions = numberOrZero(watchValues.wv_regime_mere_filiale);
    const rfBrut = rc + reintegrations - deductions;
    const pmeEligible = Boolean(watchValues.capital_pp) && numberOrZero(watchValues.ca) < 10_000_000;

    return {
      rfBrut,
      pmeEligible,
      isEstimate: pmeEligible
        ? Math.min(rfBrut, 42500) * 0.15 + Math.max(rfBrut - 42500, 0) * 0.25
        : rfBrut * 0.25
    };
  }, [watchValues]);

  const submit = async (data: LiasseFormData) => {
    await onSubmit(
      {
        siren: data.siren,
        exercice_clos: data.exercice_clos,
        benefice_comptable: data.benefice_comptable,
        perte_comptable: data.perte_comptable,
        wi_is_comptabilise: data.wi_is_comptabilise,
        wg_amendes_penalites: data.wg_amendes_penalites,
        wm_interets_excedentaires: data.wm_interets_excedentaires,
        wn_reintegrations_diverses: data.wn_reintegrations_diverses,
        wv_regime_mere_filiale: data.wv_regime_mere_filiale,
        l8_qp_12pct: data.l8_qp_12pct
      },
      Number(data.ca),
      data.capital_pp
    );
  };

  return (
    <div className="grid gap-6 lg:grid-cols-[1.7fr,1fr]">
      <Card>
        <CardHeader>
          <CardTitle>Saisie liasse 2058-A</CardTitle>
          <CardDescription>Validation temps reel et controle des lignes critiques.</CardDescription>
        </CardHeader>
        <CardContent>
          <form className="space-y-4" onSubmit={handleSubmit(submit)}>
            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="siren">SIREN</Label>
                <Input
                  id="siren"
                  placeholder="123456789"
                  {...register("siren", {
                    required: "SIREN requis",
                    pattern: { value: /^\d{9}$/, message: "Le SIREN doit contenir 9 chiffres" }
                  })}
                />
                {errors.siren ? <p className="text-xs text-red-600">{errors.siren.message}</p> : null}
              </div>
              <div className="space-y-2">
                <Label htmlFor="exercice_clos">Exercice clos</Label>
                <Input id="exercice_clos" type="date" {...register("exercice_clos", { required: true })} />
              </div>
              <div className="space-y-2">
                <Label htmlFor="ca">CA HT</Label>
                <Input id="ca" type="number" step="0.01" {...register("ca", { required: true, min: 0 })} />
              </div>
              <div className="space-y-2 pt-8">
                <label className="inline-flex items-center gap-2 text-sm text-muted-foreground">
                  <input type="checkbox" {...register("capital_pp")} />
                  Capital detenu {"\u003e="} 75% personnes physiques
                </label>
              </div>
            </div>

            <div className="grid gap-4 md:grid-cols-2">
              {rows.map((row) => (
                <div key={row.key} className="space-y-2">
                  <Label htmlFor={row.key}>{row.label}</Label>
                  <Input id={row.key} type="number" step="0.01" {...register(row.key)} />
                  <p className="text-xs text-muted-foreground">{row.hint}</p>
                </div>
              ))}
            </div>

            {error ? <p className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p> : null}

            <Button className="w-full" type="submit" disabled={isSubmitting || isLoading}>
              {isSubmitting || isLoading ? "Calcul en cours..." : "Calculer la liasse"}
            </Button>
          </form>
        </CardContent>
      </Card>

      <div className="space-y-4">
        <Card>
          <CardHeader>
            <CardTitle>Preview instantane</CardTitle>
            <CardDescription>Estimation avant envoi API.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <PreviewLine label="RF brut estime" value={`${preview.rfBrut.toLocaleString("fr-FR")} EUR`} />
            <PreviewLine label="Regime estime" value={preview.pmeEligible ? "PME 15%/25%" : "Taux normal 25%"} />
            <PreviewLine label="IS estime" value={`${preview.isEstimate.toLocaleString("fr-FR")} EUR`} />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Resultat serveur</CardTitle>
            <CardDescription>Retour du moteur fiscal FiscIA Pro.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {isLoading ? (
              <div className="space-y-2">
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-4 w-4/5" />
                <Skeleton className="h-4 w-3/5" />
              </div>
            ) : result ? (
              <>
                <PreviewLine label="IS total" value={`${result.result.is_total} EUR`} />
                <PreviewLine label="Regime" value={result.result.regime} />
                <PreviewLine label="Acompte trimestriel" value={`${result.result.acompte_trimestriel} EUR`} />
                <p className="text-xs text-muted-foreground">{result.disclaimer}</p>
              </>
            ) : (
              <p className="text-sm text-muted-foreground">Aucun resultat pour le moment.</p>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

function PreviewLine({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between text-sm">
      <span className="text-muted-foreground">{label}</span>
      <span className="font-semibold tabular-nums">{value}</span>
    </div>
  );
}

