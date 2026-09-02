import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { MetricsBar } from "./MetricsBar";

describe("MetricsBar", () => {
  it("shows the synthetic score before and after", () => {
    render(<MetricsBar scoreBefore={42.5} scoreAfter={3.0} accepted={true} attempts={1} />);
    expect(screen.getByText("42.5 → 3.0")).toBeInTheDocument();
  });

  it("labels an accepted result as aceito", () => {
    render(<MetricsBar scoreBefore={42.5} scoreAfter={3.0} accepted={true} attempts={1} />);
    expect(screen.getByText("aceito")).toBeInTheDocument();
  });

  it("labels a rejected result with the fallback explanation", () => {
    render(<MetricsBar scoreBefore={42.5} scoreAfter={42.5} accepted={false} attempts={3} />);
    expect(screen.getByText("recusado (texto original mantido)")).toBeInTheDocument();
  });

  it("shows the number of gate attempts", () => {
    render(<MetricsBar scoreBefore={42.5} scoreAfter={3.0} accepted={true} attempts={2} />);
    expect(screen.getByText("2")).toBeInTheDocument();
  });
});
