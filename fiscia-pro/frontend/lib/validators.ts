import { PLAFOND_CA_PME } from "./fiscal-constants";

export function isPmeEligible(caHt: number, capital75pp: boolean): boolean {
  return caHt < PLAFOND_CA_PME && capital75pp;
}

export function isSiren(siren: string): boolean {
  return /^\d{9}$/.test(siren);
}

