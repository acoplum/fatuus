import type { AnalysisReport } from "../types";
import { BurstinessGauge } from "./BurstinessGauge";
import { DiffView } from "./DiffView";
import { HeatmapView } from "./HeatmapView";
import { MetricsBar } from "./MetricsBar";

interface ReportPanelProps {
  report: AnalysisReport;
}

export function ReportPanel({ report }: ReportPanelProps) {
  const { originalText, clean, before, after } = report;

  return (
    <div className="report-panel">
      <MetricsBar
        scoreBefore={before.synthetic_score}
        scoreAfter={after.synthetic_score}
        accepted={clean.layer1_accepted}
        attempts={clean.layer1_attempts}
      />
      <DiffView before={originalText} after={clean.cleaned_text} />
      <HeatmapView text={originalText} matches={before.slop_matches} />
      <BurstinessGauge
        before={before.sentence_metrics.burstiness}
        after={after.sentence_metrics.burstiness}
      />
    </div>
  );
}
