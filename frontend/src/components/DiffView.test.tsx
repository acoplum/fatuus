import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DiffView } from "./DiffView";

describe("DiffView", () => {
  it("marks removed words with <del> and added words with <ins>", () => {
    const { container } = render(
      <DiffView
        before="É importante ressaltar que o sistema é robusto."
        after="O sistema é robusto e rápido."
      />
    );
    expect(container.querySelectorAll("del").length).toBeGreaterThan(0);
    expect(container.querySelectorAll("ins").length).toBeGreaterThan(0);
  });

  it("renders unchanged text as plain content with no markup", () => {
    const { container } = render(<DiffView before="Texto igual." after="Texto igual." />);
    expect(container.querySelectorAll("del")).toHaveLength(0);
    expect(container.querySelectorAll("ins")).toHaveLength(0);
    expect(container.textContent).toBe("Texto igual.");
  });
});
