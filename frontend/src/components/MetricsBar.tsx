interface MetricsBarProps {
  scoreBefore: number;
  scoreAfter: number;
  accepted: boolean;
  attempts: number;
}

export function MetricsBar({ scoreBefore, scoreAfter, accepted, attempts }: MetricsBarProps) {
  return (
    <dl className="metrics-bar">
      <div className="metrics-bar__item">
        <dt>Score sintético</dt>
        <dd>
          {scoreBefore.toFixed(1)} → {scoreAfter.toFixed(1)}
        </dd>
      </div>
      <div className="metrics-bar__item">
        <dt>Gate</dt>
        <dd>{accepted ? "aceito" : "recusado (texto original mantido)"}</dd>
      </div>
      <div className="metrics-bar__item">
        <dt>Tentativas</dt>
        <dd>{attempts}</dd>
      </div>
    </dl>
  );
}
