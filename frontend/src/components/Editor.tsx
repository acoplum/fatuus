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
    <div className="editor">
      <textarea
        value={value}
        onChange={(event) => onChange(event.target.value)}
        placeholder="Cole o texto para analisar..."
        rows={16}
      />
      <div className={`editor__counter${overLimit ? " editor__counter--over" : ""}`}>
        {value.length} / {MAX_TEXT_LENGTH}
      </div>
      <button type="button" onClick={onAnalyze} disabled={disabled}>
        {loading ? "Analisando..." : "Analisar"}
      </button>
    </div>
  );
}
