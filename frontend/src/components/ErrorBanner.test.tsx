import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { ErrorBanner } from "./ErrorBanner";

describe("ErrorBanner", () => {
  it("shows the error message with an alert role", () => {
    render(<ErrorBanner message="Falha de rede." />);
    expect(screen.getByRole("alert")).toHaveTextContent("Falha de rede.");
  });

  it("does not render a retry button when onRetry is not given", () => {
    render(<ErrorBanner message="Falha de rede." />);
    expect(screen.queryByRole("button")).not.toBeInTheDocument();
  });

  it("calls onRetry when the retry button is clicked", async () => {
    const onRetry = vi.fn();
    render(<ErrorBanner message="Falha de rede." onRetry={onRetry} />);
    await userEvent.click(screen.getByRole("button", { name: "Tentar de novo" }));
    expect(onRetry).toHaveBeenCalledTimes(1);
  });
});
