import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import ConfirmDialog from "@/components/ui/confirm-dialog";

describe("ConfirmDialog", () => {
  it("ne rend rien quand ferme", () => {
    const { container } = render(
      <ConfirmDialog
        open={false}
        title="Supprimer"
        description="Confirmer"
        onCancel={() => undefined}
        onConfirm={() => undefined}
      />
    );

    expect(container).toBeEmptyDOMElement();
  });

  it("appelle les callbacks", async () => {
    const user = userEvent.setup();
    const onConfirm = jest.fn();
    const onCancel = jest.fn();

    render(
      <ConfirmDialog
        open
        title="Retirer"
        description="Action irreversible"
        onCancel={onCancel}
        onConfirm={onConfirm}
      />
    );

    await user.click(screen.getByRole("button", { name: /Annuler/i }));
    await user.click(screen.getByRole("button", { name: /Confirmer/i }));

    expect(onCancel).toHaveBeenCalledTimes(1);
    expect(onConfirm).toHaveBeenCalledTimes(1);
  });
});
