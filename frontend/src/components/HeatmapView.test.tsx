import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { HeatmapView } from "./HeatmapView";

const text =
  "É importante ressaltar que o sistema funciona bem. É importante ressaltar que é rápido.";

describe("HeatmapView", () => {
  it("highlights the matched term inline", () => {
    const term = "É importante ressaltar que";
    const start = text.indexOf(term);
    const matches = [{ term, start, end: start + term.length, pattern: "x" }];

    const { container } = render(<HeatmapView text={text} matches={matches} />);

    expect(container.querySelectorAll("mark")).toHaveLength(1);
    expect(container.querySelector("mark")?.textContent).toBe(term);
  });

  it("lists term occurrence counts below the text, case-insensitively", () => {
    const term = "É importante ressaltar que";
    const first = text.indexOf(term);
    const second = text.indexOf(term, first + 1);
    const matches = [
      { term, start: first, end: first + term.length, pattern: "x" },
      { term, start: second, end: second + term.length, pattern: "x" },
    ];

    render(<HeatmapView text={text} matches={matches} />);

    expect(
      screen.getByText('"é importante ressaltar que" — 2 ocorrências')
    ).toBeInTheDocument();
  });

  it("renders no highlight marks and no summary when there are no matches", () => {
    const { container } = render(<HeatmapView text="Texto limpo." matches={[]} />);

    expect(container.querySelectorAll("mark")).toHaveLength(0);
    expect(container.querySelector(".heatmap-view__summary")).not.toBeInTheDocument();
    expect(screen.getByText("Texto limpo.")).toBeInTheDocument();
  });

  it("skips a match that overlaps one already rendered, in both the marks and the summary", () => {
    const matches = [
      { term: "a", start: 0, end: 10, pattern: "x" },
      { term: "b", start: 5, end: 15, pattern: "x" },
    ];

    const { container } = render(<HeatmapView text={text} matches={matches} />);

    expect(container.querySelectorAll("mark")).toHaveLength(1);
    expect(screen.queryByText(/"b"/)).not.toBeInTheDocument();
  });
});
