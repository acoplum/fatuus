import type { AnalysisReport } from "../types";
import { BurstinessGauge } from "./BurstinessGauge";
import { HeatmapView } from "./HeatmapView";
import { MetricsBar } from "./MetricsBar";
import { PipelineExplanation } from "./PipelineExplanation";
import { TextViewer } from "./TextViewer";

interface ReportPanelProps {
  report: AnalysisReport;
}

export function ReportPanel({ report }: ReportPanelProps) {
  const { originalText, clean, before, after } = report;

  return (
    <div className="report-panel">
      <div className="card report-panel__overview">
        <div className="card__header">
          <h3 className="card__title">Diagnóstico & Métricas de IA</h3>
          <p className="card__subtitle">
            Indicadores de densidade sintética e variação rítmica antes e depois do pipeline.
          </p>
        </div>
        <MetricsBar
          scoreBefore={before.synthetic_score}
          scoreAfter={after.synthetic_score}
          accepted={clean.layer1_accepted}
          attempts={clean.layer1_attempts}
        />
        <BurstinessGauge
          before={before.sentence_metrics.burstiness}
          after={after.sentence_metrics.burstiness}
        />
      </div>

      <TextViewer before={originalText} after={clean.cleaned_text} />

      <HeatmapView
        text={originalText}
        matches={before.slop_matches}
        structuralMatches={before.structural_matches}
      />

      <PipelineExplanation
        accepted={clean.layer1_accepted}
        attempts={clean.layer1_attempts}
        slopCount={before.slop_count}
        gateReasons={clean.gate_reasons}
      />
    </div>
  );
}
