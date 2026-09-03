import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { App } from "./App";
import { ApiError, cleanText, probeText } from "./api";

vi.mock("./api", () => ({
  cleanText: vi.fn(),
  probeText: vi.fn(),
  ApiError: class ApiError extends Error {
    status: number;
    constructor(status: number) {
      super(`status ${status}`);
      this.status = status;
    }
  },
}));

const mockedCleanText = vi.mocked(cleanText);
const mockedProbeText = vi.mocked(probeText);

const CLEAN_RESULT = {
  cleaned_text: "O sistema é robusto e rápido.",
  layer0: {
    cleaned_text: "O sistema é robusto.",
    invisible_removed: 0,
    typography_normalized: 0,
    slop_replaced: 1,
  },
  layer1_accepted: true,
  layer1_attempts: 1,
  gate_reasons: [],
};

const BEFORE_RESULT = {
  word_count: 8,
  synthetic_score: 42.0,
  slop_count: 1,
  slop_density_per_100_words: 12.5,
  invisible_char_count: 0,
  structural_count: 0,
  sentence_metrics: { sentence_count: 1, avg_words_per_sentence: 8, std_dev_words: 0, burstiness: -0.75 },
  typography: {
    em_dash_count: 0,
    em_dash_per_100_words: 0,
    curly_quote_count: 0,
    ellipsis_char_count: 0,
    space_lookalike_count: 0,
  },
  formatting: { bold_segment_count: 0, bold_bullet_count: 0, emoji_heading_count: 0 },
  slop_matches: [],
  structural_matches: [],
  invisible_chars: [],
};

const AFTER_RESULT = {
  ...BEFORE_RESULT,
  synthetic_score: 3.0,
  slop_count: 0,
  sentence_metrics: { ...BEFORE_RESULT.sentence_metrics, burstiness: 0.2 },
};

describe("App", () => {
  beforeEach(() => {
    mockedCleanText.mockReset();
    mockedProbeText.mockReset();
  });

  it("shows the report after a successful analysis", async () => {
    mockedCleanText.mockResolvedValue(CLEAN_RESULT);
    mockedProbeText.mockResolvedValueOnce(BEFORE_RESULT).mockResolvedValueOnce(AFTER_RESULT);
    render(<App />);

    await userEvent.type(screen.getByPlaceholderText("Cole o texto para analisar..."), "texto");
    await userEvent.click(screen.getByRole("button", { name: "Analisar" }));

    await waitFor(() => expect(screen.getByText("42.0 → 3.0")).toBeInTheDocument());
    expect(mockedProbeText).toHaveBeenNthCalledWith(2, CLEAN_RESULT.cleaned_text);
  });

  it("shows a fallback label without treating a rejected gate as an error", async () => {
    mockedCleanText.mockResolvedValue({
      ...CLEAN_RESULT,
      layer1_accepted: false,
      gate_reasons: ["burstiness não melhorou"],
    });
    mockedProbeText.mockResolvedValueOnce(BEFORE_RESULT).mockResolvedValueOnce(BEFORE_RESULT);
    render(<App />);

    await userEvent.type(screen.getByPlaceholderText("Cole o texto para analisar..."), "texto");
    await userEvent.click(screen.getByRole("button", { name: "Analisar" }));

    await waitFor(() =>
      expect(screen.getByText("recusado (texto original mantido)")).toBeInTheDocument()
    );
    expect(screen.queryByRole("alert")).not.toBeInTheDocument();
  });

  it("shows a session-expired message on a 401", async () => {
    mockedCleanText.mockRejectedValue(new ApiError(401));
    render(<App />);

    await userEvent.type(screen.getByPlaceholderText("Cole o texto para analisar..."), "texto");
    await userEvent.click(screen.getByRole("button", { name: "Analisar" }));

    await waitFor(() =>
      expect(screen.getByRole("alert")).toHaveTextContent("Sessão expirada, recarregue a página.")
    );
  });

  it("shows a generic error banner on a network/5xx failure", async () => {
    mockedCleanText.mockRejectedValue(new Error("network down"));
    render(<App />);

    await userEvent.type(screen.getByPlaceholderText("Cole o texto para analisar..."), "texto");
    await userEvent.click(screen.getByRole("button", { name: "Analisar" }));

    await waitFor(() =>
      expect(screen.getByRole("alert")).toHaveTextContent("Falha ao analisar o texto. Tente de novo.")
    );
  });
});
