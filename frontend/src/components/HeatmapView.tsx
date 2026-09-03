import type { ReactNode } from "react";
import type { SlopMatch, StructuralMatch } from "../types";

interface HeatmapViewProps {
  text: string;
  matches: SlopMatch[];
  structuralMatches?: StructuralMatch[];
}

interface TermCount {
  term: string;
  count: number;
}

interface Highlight extends SlopMatch {
  structural: boolean;
  name?: string;
}

function countByTerm(matches: SlopMatch[]): TermCount[] {
  const counts = new Map<string, number>();
  for (const match of matches) {
    const key = match.term.toLowerCase();
    counts.set(key, (counts.get(key) ?? 0) + 1);
  }
  return Array.from(counts.entries())
    .map(([term, count]) => ({ term, count }))
    .sort((a, b) => b.count - a.count || a.term.localeCompare(b.term));
}

export function HeatmapView({ text, matches, structuralMatches = [] }: HeatmapViewProps) {
  const codePoints = Array.from(text);
  const fragments: ReactNode[] = [];
  const accepted: Highlight[] = [];
  let cursor = 0;

  const highlights: Highlight[] = [
    ...matches.map((m) => ({ ...m, structural: false })),
    ...structuralMatches.map((m) => ({ ...m, structural: true })),
  ].sort((a, b) => a.start - b.start);

  highlights.forEach((match, index) => {
    if (match.start < cursor) {
      return;
    }
    if (match.start > cursor) {
      fragments.push(codePoints.slice(cursor, match.start).join(""));
    }
    fragments.push(
      <mark key={index} className={match.structural ? "mark--structural" : undefined}>
        {codePoints.slice(match.start, match.end).join("")}
      </mark>
    );
    accepted.push(match);
    cursor = match.end;
  });
  if (cursor < codePoints.length) {
    fragments.push(codePoints.slice(cursor).join(""));
  }

  // A lista resumo conta só os matches efetivamente destacados: um match
  // pulado por sobrepor outro não pode aparecer aqui como se tivesse sido
  // marcado no texto.
  const terms = countByTerm(accepted.filter((m) => !m.structural));
  const structuralNames = countByTerm(
    accepted
      .filter((m) => m.structural)
      .map((m) => ({ ...m, term: m.name ?? m.term }))
  );

  return (
    <div className="card heatmap-view">
      <div className="card__header">
        <h3 className="card__title">Marcas Sintéticas no Texto (Camada 0)</h3>
        <p className="card__subtitle">
          Expressões e clichês de LLM identificados no texto original antes da higienização.
        </p>
      </div>

      {terms.length > 0 && (
        <div className="heatmap-view__summary-wrap">
          <ul className="heatmap-view__summary">
            {terms.map(({ term, count }) => (
              <li key={term}>{`"${term}" — ${count} ocorrência${count > 1 ? "s" : ""}`}</li>
            ))}
          </ul>
        </div>
      )}

      {structuralNames.length > 0 && (
        <div className="heatmap-view__summary-wrap">
          <ul className="heatmap-view__summary heatmap-view__summary--structural">
            {structuralNames.map(({ term, count }) => (
              <li key={term}>{`padrão estrutural: ${term} — ${count} ocorrência${count > 1 ? "s" : ""}`}</li>
            ))}
          </ul>
        </div>
      )}

      <div className="heatmap-view__content">
        <p className="heatmap-view__text">{fragments}</p>
      </div>
    </div>
  );
}
