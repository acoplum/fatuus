import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PipelineExplanation } from "./PipelineExplanation";

describe("PipelineExplanation", () => {
  it("renders the explanation cards for Camada 0, Camada 1 and Gate", () => {
    render(
      <PipelineExplanation
        accepted={true}
        attempts={1}
        slopCount={3}
        gateReasons={[]}
      />
    );

    expect(screen.getByText("Camada 0")).toBeInTheDocument();
    expect(screen.getByText("Camada 1")).toBeInTheDocument();
    expect(screen.getByText("Gate")).toBeInTheDocument();
    expect(screen.getByText(/3 termo\(s\) sintético\(s\) detectado\(s\)/)).toBeInTheDocument();
    expect(screen.getByText(/Aprovado na 1ª tentativa/)).toBeInTheDocument();
  });

  it("renders rejection information and gate reasons when rejected", () => {
    render(
      <PipelineExplanation
        accepted={false}
        attempts={3}
        slopCount={1}
        gateReasons={["Tamanho desviou do limite aceitável"]}
      />
    );

    expect(screen.getByText(/Recusado após 3 tentativas/)).toBeInTheDocument();
    expect(screen.getByText("Tamanho desviou do limite aceitável")).toBeInTheDocument();
  });
});
