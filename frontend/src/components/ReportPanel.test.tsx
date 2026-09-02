import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import type { AnalysisReport } from "../types";
import { ReportPanel } from "./ReportPanel";

const report: AnalysisReport = {
  originalText: "É importante ressaltar que o sistema é robusto.",
  clean: {
    cleaned_text: "O sistema é robusto e rápido.",
    layer0: { cleaned_text: "O sistema é robusto.", invisible_removed: 0, slop_replaced: 1 },
    layer1_accepted: true,
    layer1_attempts: 1,
    gate_reasons: [],
  },
  before: {
    word_count: 8,
    synthetic_score: 42.0,
    slop_count: 1,
    slop_density_per_100_words: 12.5,
    invisible_char_count: 0,
    sentence_metrics: { sentence_count: 1, avg_words_per_sentence: 8, std_dev_words: 0, burstiness: -0.75 },
    slop_matches: [{ term: "É importante ressaltar que", start: 0, end: 27, pattern: "x" }],
    invisible_chars: [],
  },
  after: {
    word_count: 6,
    synthetic_score: 3.0,
    slop_count: 0,
    slop_density_per_100_words: 0,
    invisible_char_count: 0,
    sentence_metrics: { sentence_count: 1, avg_words_per_sentence: 6, std_dev_words: 0, burstiness: 0.2 },
    slop_matches: [],
    invisible_chars: [],
  },
};

describe("ReportPanel", () => {
  it("renders the metrics, diff, heatmap and burstiness sections together", () => {
    const { container } = render(<ReportPanel report={report} />);
    expect(screen.getByText("42.0 → 3.0")).toBeInTheDocument();
    expect(container.querySelectorAll("del, ins").length).toBeGreaterThan(0);
    expect(container.querySelectorAll("mark")).toHaveLength(1);
    expect(screen.getByText("antes: -0.75")).toBeInTheDocument();
  });
});
