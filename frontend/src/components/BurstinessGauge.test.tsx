import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { BurstinessGauge } from "./BurstinessGauge";

describe("BurstinessGauge", () => {
  it("shows the before and after values as labels", () => {
    render(<BurstinessGauge before={-0.75} after={0.2} />);
    expect(screen.getByText("antes: -0.75")).toBeInTheDocument();
    expect(screen.getByText("depois: 0.20")).toBeInTheDocument();
  });

  it("positions the before marker left of the after marker when it improved", () => {
    const { container } = render(<BurstinessGauge before={-0.75} after={0.2} />);
    const before = container.querySelector(".burstiness-gauge__marker--before") as HTMLElement;
    const after = container.querySelector(".burstiness-gauge__marker--after") as HTMLElement;
    expect(parseFloat(before.style.left)).toBeLessThan(parseFloat(after.style.left));
  });

  it("clamps out-of-range values to the edges of the scale", () => {
    const { container } = render(<BurstinessGauge before={-2} after={5} />);
    const before = container.querySelector(".burstiness-gauge__marker--before") as HTMLElement;
    const after = container.querySelector(".burstiness-gauge__marker--after") as HTMLElement;
    expect(before.style.left).toBe("0%");
    expect(after.style.left).toBe("100%");
  });
});
