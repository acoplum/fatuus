import { MAX_TEXT_LENGTH } from "../constants";

interface EditorProps {
  value: string;
  onChange: (text: string) => void;
  onAnalyze: () => void;
  loading: boolean;
}

export function Editor({ value, onChange, onAnalyze, loading }: EditorProps) {
  const overLimit = value.length > MAX_TEXT_LENGTH;
  const disabled = loading || value.trim().length === 0 || overLimit;

  return (
    <div className="card editor">
      <div className="card__header">
        <h3 className="card__title">Texto Original / Entrada</h3>
        <p className="card__subtitle">
          Cole o texto gerado por IA para diagnóstico de slop e reescrita de cadência.
        </p>
      </div>
      <textarea
        value={value}
        onChange={(event) => onChange(event.target.value)}
        placeholder="Cole o texto para analisar..."
        rows={18}
      />
      <div className="editor__footer">
        <div className={`editor__counter${overLimit ? " editor__counter--over" : ""}`}>
          {value.length} / {MAX_TEXT_LENGTH}
        </div>
        <button
          type="button"
          className="btn btn--primary"
          onClick={onAnalyze}
          disabled={disabled}
        >
          {loading ? "Analisando..." : "Analisar"}
        </button>
      </div>
    </div>
  );
}
