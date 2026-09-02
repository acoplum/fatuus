interface MetricsBarProps {
  scoreBefore: number;
  scoreAfter: number;
  accepted: boolean;
  attempts: number;
}

export function MetricsBar({ scoreBefore, scoreAfter, accepted, attempts }: MetricsBarProps) {
  const delta = scoreBefore - scoreAfter;
  const deltaPercent = scoreBefore > 0 ? ((delta / scoreBefore) * 100).toFixed(0) : "0";

  return (
    <dl className="metrics-bar">
      <div className="metrics-bar__item metrics-bar__item--score">
        <dt>Score sintético</dt>
        <dd>
          {scoreBefore.toFixed(1)} → {scoreAfter.toFixed(1)}
        </dd>
        <div className="metrics-bar__meta">
          {delta > 0 ? (
            <span className="metrics-bar__badge metrics-bar__badge--success">
              -{deltaPercent}% marcas
            </span>
          ) : (
            <span className="metrics-bar__badge metrics-bar__badge--neutral">estável</span>
          )}
          <span className="metrics-bar__help">
            Densidade de jargão de LLM e padrões sintéticos identificados.
          </span>
        </div>
      </div>

      <div className="metrics-bar__item metrics-bar__item--gate">
        <dt>Gate</dt>
        <dd className={accepted ? "metrics-bar__val--ok" : "metrics-bar__val--warn"}>
          {accepted ? "aceito" : "recusado (texto original mantido)"}
        </dd>
        <div className="metrics-bar__meta">
          <span className="metrics-bar__help">
            {accepted
              ? "Validação semântica confirmou preservação integral do conteúdo original."
              : "Salvaguarda ativada: reescrita rejeitada por desvio semântico ou tamanho excessivo."}
          </span>
        </div>
      </div>

      <div className="metrics-bar__item metrics-bar__item--attempts">
        <dt>Tentativas</dt>
        <dd>{attempts}</dd>
        <div className="metrics-bar__meta">
          <span className="metrics-bar__help">
            {attempts === 1
              ? "Aprovado na 1ª passada pelo pipeline agêntico."
              : `Exigiu ${attempts} iterações de reamostragem para atender aos critérios.`}
          </span>
        </div>
      </div>
    </dl>
  );
}
