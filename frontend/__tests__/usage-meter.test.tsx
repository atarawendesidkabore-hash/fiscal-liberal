import { render, screen } from "@testing-library/react";

import UsageMeter from "@/components/facturation/UsageMeter";

describe("UsageMeter", () => {
  it("affiche le mode illimite", () => {
    render(
      <UsageMeter
        usage={{
          firm_id: 1,
          period: "2026-03",
          credits_total: 0,
          credits_used: 220,
          credits_remaining: 0,
          overage_count: 0,
          unlimited: true
        }}
      />
    );

    expect(screen.getByText(/Formule illimitee active/i)).toBeInTheDocument();
  });

  it("affiche une alerte credits bas", () => {
    render(
      <UsageMeter
        usage={{
          firm_id: 1,
          period: "2026-03",
          credits_total: 50,
          credits_used: 45,
          credits_remaining: 5,
          overage_count: 0,
          unlimited: false
        }}
      />
    );

    expect(screen.getByText(/Credits bas/i)).toBeInTheDocument();
    expect(screen.getByText("5")).toBeInTheDocument();
  });
});
