import { diffWords } from "diff";

interface DiffViewProps {
  before: string;
  after: string;
}

export function DiffView({ before, after }: DiffViewProps) {
  const parts = diffWords(before, after);

  return (
    <p className="diff-view">
      {parts.map((part, index) => {
        if (part.added) {
          return (
            <ins key={index} className="diff-view__added">
              {part.value}
            </ins>
          );
        }
        if (part.removed) {
          return (
            <del key={index} className="diff-view__removed">
              {part.value}
            </del>
          );
        }
        return <span key={index}>{part.value}</span>;
      })}
    </p>
  );
}
