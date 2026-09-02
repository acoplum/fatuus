import { useState } from "react";
import { ApiError, cleanText, probeText } from "./api";
import { Editor } from "./components/Editor";
import { ErrorBanner } from "./components/ErrorBanner";
import { ReportPanel } from "./components/ReportPanel";
import type { AnalysisReport } from "./types";

export function App() {
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [report, setReport] = useState<AnalysisReport | null>(null);

  async function handleAnalyze() {
    setError(null);
    setLoading(true);
    try {
      const [clean, before] = await Promise.all([cleanText(text), probeText(text)]);
      const after = await probeText(clean.cleaned_text);
      setReport({ originalText: text, clean, before, after });
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) {
        setError("Sessão expirada, recarregue a página.");
      } else {
        setError("Falha ao analisar o texto. Tente de novo.");
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="app">
      <header className="app__header">Fatuus</header>
      <div className="app__panels">
        <Editor value={text} onChange={setText} onAnalyze={handleAnalyze} loading={loading} />
        <div className="app__report">
          {error && <ErrorBanner message={error} onRetry={handleAnalyze} />}
          {report && <ReportPanel report={report} />}
        </div>
      </div>
    </div>
  );
}
