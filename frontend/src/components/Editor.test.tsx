import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { MAX_TEXT_LENGTH } from "../constants";
import { Editor } from "./Editor";

describe("Editor", () => {
  it("calls onChange with the new text as the user types", async () => {
    const onChange = vi.fn();
    render(<Editor value="" onChange={onChange} onAnalyze={vi.fn()} loading={false} />);
    await userEvent.type(screen.getByPlaceholderText("Cole o texto para analisar..."), "a");
    expect(onChange).toHaveBeenCalledWith("a");
  });

  it("disables the button when the text is empty", () => {
    render(<Editor value="" onChange={vi.fn()} onAnalyze={vi.fn()} loading={false} />);
    expect(screen.getByRole("button", { name: "Analisar" })).toBeDisabled();
  });

  it("disables the button and flags the counter when over the character limit", () => {
    const overLimitText = "a".repeat(MAX_TEXT_LENGTH + 1);
    render(<Editor value={overLimitText} onChange={vi.fn()} onAnalyze={vi.fn()} loading={false} />);
    expect(screen.getByRole("button", { name: "Analisar" })).toBeDisabled();
    expect(screen.getByText(`${overLimitText.length} / ${MAX_TEXT_LENGTH}`)).toHaveClass(
      "editor__counter--over"
    );
  });

  it("shows a loading label and disables the button while analyzing", () => {
    render(<Editor value="texto válido" onChange={vi.fn()} onAnalyze={vi.fn()} loading={true} />);
    expect(screen.getByRole("button", { name: "Analisando..." })).toBeDisabled();
  });

  it("calls onAnalyze when the button is clicked with valid text", async () => {
    const onAnalyze = vi.fn();
    render(<Editor value="texto válido" onChange={vi.fn()} onAnalyze={onAnalyze} loading={false} />);
    await userEvent.click(screen.getByRole("button", { name: "Analisar" }));
    expect(onAnalyze).toHaveBeenCalledTimes(1);
  });
});
