export type Role = "admin" | "fiscaliste" | "client";

export interface UserProfile {
  id: number;
  email: string;
  role: Role | string;
  firm_id: number;
  is_active: boolean;
  created_at: string;
}

export interface TokenPair {
  access_token: string;
  refresh_token: string;
  token_type?: string;
}

export interface AuthResponse {
  user: UserProfile;
  tokens: TokenPair;
}

export interface BillingPlan {
  name: "starter" | "pro" | "cabinet" | string;
  price: number;
  calculation_limit: number;
  unlimited: boolean;
}

export interface UsageSummary {
  firm_id: number;
  period: string;
  credits_total: number;
  credits_used: number;
  credits_remaining: number;
  overage_count: number;
  unlimited: boolean;
}

export interface InvoiceEvent {
  stripe_event_id: string;
  type: string;
  amount: number;
  status: string;
  created_at: string;
  currency?: string;
}

export interface CalculationPreview {
  id: string;
  siren: string;
  exercice_clos: string;
  is_total: number;
  regime: string;
  created_at: string;
}

export interface CalculationDetail extends CalculationPreview {
  rf?: number;
  acompte_trimestriel?: number;
  ai_explanation?: string;
  lignes?: Array<{ code: string; montant: number }>;
}

export interface LiasseInput {
  siren: string;
  exercice_clos: string;
  benefice_comptable: string;
  perte_comptable: string;
  wi_is_comptabilise: string;
  wg_amendes_penalites: string;
  wm_interets_excedentaires: string;
  wn_reintegrations_diverses: string;
  wv_regime_mere_filiale: string;
  l8_qp_12pct: string;
}

export interface LiasseResult {
  calculation_id: number;
  result: {
    rf_brut: string;
    rf_net: string;
    is_total: string;
    regime: string;
    acompte_trimestriel: string;
    details: Record<string, string>;
  };
  disclaimer: string;
  credit_usage: UsageSummary;
}

export interface TeamMember {
  id: string;
  nom: string;
  email: string;
  role: Role | string;
  actif: boolean;
}

