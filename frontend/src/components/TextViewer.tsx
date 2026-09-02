import { useState } from "react";
import { DiffView } from "./DiffView";

interface TextViewerProps {
  before: string;
  after: string;
}

export type TabType = "diff" | "clean" | "split" | "original";

export function TextViewer({ before, after }: TextViewerProps) {
  const [activeTab, setActiveTab] = useState<TabType>("diff");
  const [copied, setCopied] = useState(false);

  async function handleCopy() {
    try {
      if (navigator.clipboard?.writeText) {
        await navigator.clipboard.writeText(after);
      } else {
        const textarea = document.createElement("textarea");
        textarea.value = after;
        textarea.style.position = "fixed";
        textarea.style.left = "-9999px";
        document.body.appendChild(textarea);
        textarea.select();
        document.execCommand("copy");
        document.body.removeChild(textarea);
      }
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      setCopied(false);
    }
  }

  return (
    <div className="card text-viewer">
      <div className="card__header text-viewer__header">
        <div>
          <h3 className="card__title">Texto Processado & Comparação</h3>
          <p className="card__subtitle">
            Alterne entre o diff com alterações, apenas o texto limpo, visualização lado a lado ou original.
          </p>
        </div>
        <div className="text-viewer__actions">
          <button
            type="button"
            className={`btn btn--copy${copied ? " btn--copied" : ""}`}
            onClick={handleCopy}
            title="Copiar apenas o texto higienizado final"
          >
            {copied ? "✓ Copiado!" : "📋 Copiar Texto Limpo"}
          </button>
        </div>
      </div>

      <div className="text-viewer__tabs">
        <button
          type="button"
          className={`tab-btn${activeTab === "diff" ? " tab-btn--active" : ""}`}
          onClick={() => setActiveTab("diff")}
        >
          Diff (Alterações)
        </button>
        <button
          type="button"
          className={`tab-btn${activeTab === "clean" ? " tab-btn--active" : ""}`}
          onClick={() => setActiveTab("clean")}
        >
          Texto Limpo (Novo)
        </button>
        <button
          type="button"
          className={`tab-btn${activeTab === "split" ? " tab-btn--active" : ""}`}
          onClick={() => setActiveTab("split")}
        >
          Lado a Lado
        </button>
        <button
          type="button"
          className={`tab-btn${activeTab === "original" ? " tab-btn--active" : ""}`}
          onClick={() => setActiveTab("original")}
        >
          Original
        </button>
      </div>

      <div className="text-viewer__body">
        {activeTab === "diff" && <DiffView before={before} after={after} />}
        {activeTab === "clean" && (
          <div className="text-viewer__clean-text">{after}</div>
        )}
        {activeTab === "split" && (
          <div className="text-viewer__split">
            <div className="text-viewer__split-col">
              <div className="text-viewer__split-badge text-viewer__split-badge--before">
                Original ({before.length} carac.)
              </div>
              <div className="text-viewer__split-content">{before}</div>
            </div>
            <div className="text-viewer__split-col">
              <div className="text-viewer__split-badge text-viewer__split-badge--after">
                Limpo ({after.length} carac.)
              </div>
              <div className="text-viewer__split-content">{after}</div>
            </div>
          </div>
        )}
        {activeTab === "original" && (
          <div className="text-viewer__original-text">{before}</div>
        )}
      </div>
    </div>
  );
}
