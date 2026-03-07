import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import DemoPage from "@/app/demo/page";

describe("DemoPage", () => {
  it("incremente le compteur jusqu'a la limite", async () => {
    const user = userEvent.setup();
    render(<DemoPage />);

    const button = screen.getByRole("button", { name: /Lancer la simulation/i });

    for (let index = 1; index <= 5; index += 1) {
      await user.click(button);
      expect(screen.getByText(`Usage demo: ${index}/5`)).toBeInTheDocument();
    }

    expect(button).toBeDisabled();
  });
});
