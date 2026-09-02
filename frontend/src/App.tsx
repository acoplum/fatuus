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
      <header className="app__header">
        <div className="app__header-brand">
          <div className="app__logo">F</div>
          <div className="app__header-titles">
            <div className="app__header-title-row">
              <h1 className="app__title">Fatuus</h1>
              <span className="badge badge--pill">Open Source · Apache-2.0</span>
            </div>
            <p className="app__tagline">
              Desconstrução de marcas sintéticas (unslop) e recomposição de cadência de IA
            </p>
          </div>
        </div>
        <div className="app__header-info">
          <div className="app__info-chip">
            <span className="app__info-dot" />
            Camada 0 (Determinística) + Camada 1 (Agno Agêntico)
          </div>
        </div>
      </header>

      <main className="app__panels">
        <Editor value={text} onChange={setText} onAnalyze={handleAnalyze} loading={loading} />
        <div className="app__report">
          {error && <ErrorBanner message={error} onRetry={handleAnalyze} />}

          {loading && (
            <div className="card report-loading">
              <div className="spinner" />
              <h3>Higienizando texto...</h3>
              <p>Executando Camada 0 (limpeza determinística) e Camada 1 (agentes de cadência com Gemini)...</p>
            </div>
          )}

          {!report && !loading && !error && (
            <div className="card report-empty">
              <div className="report-empty__icon">✨</div>
              <h3 className="report-empty__title">Aguardando texto para análise</h3>
              <p className="report-empty__desc">
                Cole um texto gerado por LLM no editor à esquerda e clique em <strong>Analisar</strong>.
              </p>
              <div className="report-empty__steps">
                <div className="report-empty__step">
                  <div className="report-empty__step-num">0</div>
                  <div>
                    <strong>Camada 0 (Determinística):</strong> Identifica clichês sintéticos (<em>"é importante ressaltar"</em>, <em>"mergulhar em"</em>) e remove caracteres invisíveis (zero-width).
                  </div>
                </div>
                <div className="report-empty__step">
                  <div className="report-empty__step-num">1</div>
                  <div>
                    <strong>Camada 1 (Agêntica):</strong> Agentes de anti-simetria quebram paralelismos robóticos e variam o tamanho dos períodos para elevar o <em>burstiness</em>.
                  </div>
                </div>
                <div className="report-empty__step">
                  <div className="report-empty__step-num">G</div>
                  <div>
                    <strong>Gate de Fidelidade:</strong> Avalia se a essência do texto original foi preservada sem cortes excessivos ou alucinações.
                  </div>
                </div>
              </div>
            </div>
          )}

          {report && !loading && <ReportPanel report={report} />}
        </div>
      </main>
    </div>
  );
}
