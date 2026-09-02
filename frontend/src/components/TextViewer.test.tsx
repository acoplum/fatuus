import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { TextViewer } from "./TextViewer";

describe("TextViewer", () => {
  it("renders diff view by default", () => {
    const { container } = render(
      <TextViewer before="Antes de tudo." after="Depois de tudo." />
    );
    expect(container.querySelectorAll("del, ins").length).toBeGreaterThan(0);
  });

  it("switches to clean text tab", async () => {
    render(<TextViewer before="Texto original." after="Texto limpo final." />);
    await userEvent.click(screen.getByRole("button", { name: "Texto Limpo (Novo)" }));
    expect(screen.getByText("Texto limpo final.")).toBeInTheDocument();
  });

  it("switches to split view tab and shows both versions", async () => {
    render(<TextViewer before="Texto original." after="Texto limpo final." />);
    await userEvent.click(screen.getByRole("button", { name: "Lado a Lado" }));
    expect(screen.getByText("Original (15 carac.)")).toBeInTheDocument();
    expect(screen.getByText("Limpo (18 carac.)")).toBeInTheDocument();
    expect(screen.getByText("Texto original.")).toBeInTheDocument();
    expect(screen.getByText("Texto limpo final.")).toBeInTheDocument();
  });

  it("copies clean text to clipboard when copy button is clicked", async () => {
    const writeTextMock = vi.fn().mockResolvedValue(undefined);
    Object.defineProperty(navigator, "clipboard", {
      value: { writeText: writeTextMock },
      configurable: true,
      writable: true,
    });

    render(<TextViewer before="Texto original." after="Texto limpo final." />);
    await userEvent.click(screen.getByRole("button", { name: /Copiar Texto Limpo/ }));

    expect(writeTextMock).toHaveBeenCalledWith("Texto limpo final.");
    expect(screen.getByRole("button", { name: "✓ Copiado!" })).toBeInTheDocument();
  });
});
