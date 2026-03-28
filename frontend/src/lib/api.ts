const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface FetchOptions extends RequestInit {
  token?: string;
}

async function apiFetch<T>(path: string, opts: FetchOptions = {}): Promise<T> {
  const { token, headers: extraHeaders, ...rest } = opts;
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(extraHeaders as Record<string, string>),
  };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  let res: Response;
  try {
    res = await fetch(`${API_BASE}${path}`, { headers, ...rest });
  } catch (error) {
    const message =
      error instanceof Error && error.message
        ? `Impossible de contacter l'API locale (${API_BASE}).`
        : "Impossible de contacter l'API locale.";
    throw new ApiError(0, message);
  }

  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: res.statusText }));
    throw new ApiError(res.status, body.detail || "Erreur serveur");
  }

  if (res.status === 204) return null as T;
  return res.json();
}

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = "ApiError";
  }
}

// --- Auth ---

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface UserResponse {
  id: string;
  email: string;
  full_name: string | null;
  role: string;
  firm_id: string | null;
  is_active: boolean;
}

export async function register(data: {
  email: string;
  password: string;
  full_name: string;
  firm_name?: string;
  firm_siren?: string;
}): Promise<UserResponse> {
  return apiFetch("/auth/register", { method: "POST", body: JSON.stringify(data) });
}

export async function login(email: string, password: string): Promise<TokenResponse> {
  return apiFetch("/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

export async function refreshToken(refresh_token: string): Promise<TokenResponse> {
  return apiFetch("/auth/refresh", {
    method: "POST",
    body: JSON.stringify({ refresh_token }),
  });
}

export async function getMe(token: string): Promise<UserResponse> {
  return apiFetch("/auth/me", { token });
}

// --- Liasse ---

export interface LiasseInput {
  siren: string;
  exercice_clos: string;
  benefice_comptable: number;
  perte_comptable: number;
  wi_is_comptabilise: number;
  wg_amendes_penalites: number;
  wm_interets_excedentaires: number;
  wn_reintegrations_diverses: number;
  wv_regime_mere_filiale: number;
  l8_qp_12pct: number;
}

export interface LiasseResult {
  rf_brut: number;
  rf_net: number;
  is_total: number;
  regime: string;
  acompte_trimestriel: number;
  details: Record<string, number>;
  meta?: {
    ca: number;
    capital_pp: boolean;
  };
  disclaimer: string;
  saved_id?: string;
}

export async function calculateLiasse(
  token: string,
  liasse: LiasseInput,
  ca: number,
  capital_pp: boolean,
  save: boolean = false
): Promise<LiasseResult> {
  return apiFetch(`/v2/liasse?save=${save}`, {
    token,
    method: "POST",
    body: JSON.stringify({ liasse, ca, capital_pp }),
  });
}

export interface Liasse2058BCInput {
  deficits_reportables_ouverture: number;
  moins_values_lt_ouverture: number;
  moins_values_lt_imputees: number;
  acomptes_verses: number;
  credits_impot: number;
  contribution_sociale: number;
  regularisations: number;
}

export interface Liasse2058BCResult {
  tableau_2058b: Record<string, number>;
  tableau_2058c: Record<string, number>;
  regime: string;
  notes: string[];
  disclaimer: string;
}

export async function prepare2058BC(
  token: string,
  liasse: LiasseInput,
  ca: number,
  capital_pp: boolean,
  annexes: Liasse2058BCInput
): Promise<Liasse2058BCResult> {
  return apiFetch("/v2/liasse/2058-bc", {
    token,
    method: "POST",
    body: JSON.stringify({ liasse, ca, capital_pp, annexes }),
  });
}

export interface AIStatusResponse {
  available: boolean;
  model: string;
}

export interface AIExplainResponse {
  response: string;
  model: string;
  mode: string;
  elapsed_ms: number;
  tokens_evaluated: number;
  tokens_generated: number;
  disclaimer: string;
}

export async function getAIStatus(token: string): Promise<AIStatusResponse> {
  return apiFetch("/v2/ai/status", { token });
}

export async function explainWithAI(
  token: string,
  prompt: string,
  mode: "is" | "liasse" | "mere" | "general" = "general",
  temperature: number = 0.05
): Promise<AIExplainResponse> {
  return apiFetch("/v2/ai/explain", {
    token,
    method: "POST",
    body: JSON.stringify({ prompt, mode, temperature }),
  });
}

export async function explainLiasseWithAI(
  token: string,
  liasse: LiasseInput,
  ca: number,
  capital_pp: boolean
): Promise<AIExplainResponse> {
  return apiFetch("/v2/ai/explain-liasse", {
    token,
    method: "POST",
    body: JSON.stringify({ liasse, ca, capital_pp }),
  });
}

// --- Saved calculations ---

export interface SavedLiasse {
  id: string;
  siren: string;
  exercice_clos: string;
  rf_brut: number;
  rf_net: number;
  is_total: number;
  regime: string;
  created_at: string | null;
}

export interface SavedLiasseDetail {
  id: string;
  user_id: string;
  siren: string;
  exercice_clos: string;
  input_data: Record<string, unknown>;
  result_data: Record<string, unknown>;
  created_at: string | null;
  updated_at: string | null;
  disclaimer: string;
}

export async function listSavedLiasses(
  token: string,
  siren?: string
): Promise<{ count: number; results: SavedLiasse[] }> {
  const params = siren ? `?siren=${siren}` : "";
  return apiFetch(`/v2/liasse/saved${params}`, { token });
}

export async function getSavedLiasse(
  token: string,
  id: string
): Promise<SavedLiasseDetail> {
  return apiFetch(`/v2/liasse/saved/${id}`, { token });
}

export async function deleteSavedLiasse(
  token: string,
  id: string
): Promise<{ deleted: boolean }> {
  return apiFetch(`/v2/liasse/saved/${id}`, { token, method: "DELETE" });
}

// --- Quick IS calc (public, no auth) ---

export interface CalcISResult {
  rf: number;
  regime: string;
  tranche_15pct: number;
  tranche_25pct: number;
  is_total: number;
  acompte_trimestriel: number;
  disclaimer: string;
}

export async function calcIS(ca: number, capital_pp: boolean): Promise<CalcISResult> {
  return apiFetch("/calc-is", {
    method: "POST",
    body: JSON.stringify({ ca, capital_pp }),
  });
}
