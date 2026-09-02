interface BurstinessGaugeProps {
  before: number;
  after: number;
}

function clampToPercent(value: number): number {
  const bounded = Math.max(-1, Math.min(1, value));
  return ((bounded + 1) / 2) * 100;
}

export function BurstinessGauge({ before, after }: BurstinessGaugeProps) {
  const beforePct = clampToPercent(before);
  const afterPct = clampToPercent(after);

  return (
    <div className="burstiness-gauge">
      <div className="burstiness-gauge__track">
        <span
          className="burstiness-gauge__marker burstiness-gauge__marker--before"
          style={{ left: `${beforePct}%` }}
          title={`antes: ${before.toFixed(2)}`}
        >
          ▼
        </span>
        <span
          className="burstiness-gauge__marker burstiness-gauge__marker--after"
          style={{ left: `${afterPct}%` }}
          title={`depois: ${after.toFixed(2)}`}
        >
          ▲
        </span>
      </div>
      <div className="burstiness-gauge__labels">
        <span>antes: {before.toFixed(2)}</span>
        <span>depois: {after.toFixed(2)}</span>
      </div>
    </div>
  );
}
