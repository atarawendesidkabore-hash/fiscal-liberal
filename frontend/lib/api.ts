import type {
  AuthResponse,
  BillingPlan,
  CalculationDetail,
  CalculationPreview,
  InvoiceEvent,
  LiasseInput,
  LiasseResult,
  TeamMember,
  UsageSummary,
  UserProfile
} from "@/lib/types";

type HttpMethod = "GET" | "POST" | "PUT" | "DELETE";

async function request<T>(path: string, method: HttpMethod, body?: unknown): Promise<T> {
  const response = await fetch(path, {
    method,
    credentials: "include",
    headers: {
      "Content-Type": "application/json"
    },
    body: body ? JSON.stringify(body) : undefined
  });

  if (!response.ok) {
    const payload = await response.json().catch(() => ({}));
    throw new Error(payload.detail ?? payload.message ?? "Erreur API");
  }

  return (await response.json()) as T;
}

export const api = {
  login: (email: string, password: string) =>
    request<AuthResponse>("/api/auth/login", "POST", { email, password }),

  register: (firm_name: string, email: string, password: string, plan_type = "starter") =>
    request<AuthResponse>("/api/auth/register", "POST", { firm_name, email, password, plan_type }),

  logout: (refresh_token: string) => request<{ status: string }>("/api/auth/logout", "POST", { refresh_token }),

  me: () => request<UserProfile>("/api/auth/me", "GET"),

  searchCgi: (query: string) =>
    request<{ results: Array<{ article: string; title: string; excerpt: string }> }>("/api/proxy/search", "POST", {
      query
    }),

  calcIS: (rf: number, ca: number, capital_pp: boolean) =>
    request<{
      calculation_id: number;
      is_total: string;
      regime: string;
      tranche_15: string;
      tranche_25: string;
      acompte_trimestriel: string;
      disclaimer: string;
    }>("/api/proxy/calc-is", "POST", { rf, ca, capital_pp }),

  submitLiasse: (liasse: LiasseInput, ca: number, capital_pp: boolean) =>
    request<LiasseResult>("/api/proxy/liasse", "POST", { liasse, ca, capital_pp }),

  billingPlans: () => request<{ plans: BillingPlan[] }>("/api/proxy/billing/plans", "GET"),

  billingUsage: () => request<{ usage: UsageSummary }>("/api/proxy/billing/usage", "GET"),

  billingInvoices: () => request<{ invoices: InvoiceEvent[] }>("/api/proxy/billing/invoices", "GET"),

  billingSubscribe: (plan_name: string, success_url: string, cancel_url: string) =>
    request<{
      checkout_url: string;
      checkout_session_id: string;
      currency: string;
      payment_methods: string[];
      wallets_enabled: string[];
    }>("/api/proxy/billing/subscribe", "POST", { plan_name, success_url, cancel_url }),

  billingCancel: (at_period_end = true) => request("/api/proxy/billing/cancel", "POST", { at_period_end }),

  billingUpgrade: (plan_name: string) => request("/api/proxy/billing/upgrade", "POST", { plan_name }),

  listCalculations: async (): Promise<CalculationPreview[]> => {
    // Placeholder until dedicated list endpoint is exposed.
    return [
      {
        id: "calc-001",
        siren: "123456789",
        exercice_clos: "2024-12-31",
        is_total: 22000,
        regime: "PME 15%/25%",
        created_at: "2026-03-07 09:12"
      },
      {
        id: "calc-002",
        siren: "987654321",
        exercice_clos: "2024-12-31",
        is_total: 17500,
        regime: "Taux normal 25%",
        created_at: "2026-03-06 16:30"
      }
    ];
  },

  calculationById: async (id: string): Promise<CalculationDetail | null> => {
    const all = await api.listCalculations();
    const found = all.find((item) => item.id === id);
    if (!found) return null;
    return {
      ...found,
      ai_explanation:
        "Analyse IA: le regime applique est coherent avec les parametres PME et les retraitements extracomptables identifies.",
      lignes: [
        { code: "WI", montant: 10000 },
        { code: "WG", montant: 2000 },
        { code: "WM", montant: 8000 },
        { code: "WV", montant: -30000 },
        { code: "L8", montant: 5000 }
      ]
    };
  },

  teamMembers: async (): Promise<TeamMember[]> => {
    return [
      { id: "1", nom: "Alice Dupont", email: "alice@cabinet.fr", role: "admin", actif: true },
      { id: "2", nom: "Marc Leroy", email: "marc@cabinet.fr", role: "fiscaliste", actif: true },
      { id: "3", nom: "Client Demo", email: "client@entreprise.fr", role: "client", actif: false }
    ];
  }
};

