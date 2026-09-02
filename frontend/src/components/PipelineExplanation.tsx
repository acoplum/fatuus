interface PipelineExplanationProps {
  accepted: boolean;
  attempts: number;
  slopCount: number;
  gateReasons?: string[];
}

export function PipelineExplanation({
  accepted,
  attempts,
  slopCount,
  gateReasons = [],
}: PipelineExplanationProps) {
  return (
    <div className="card pipeline-explanation">
      <div className="card__header">
        <h3 className="card__title">Lógica das Correções & Linha Seguida</h3>
        <p className="card__subtitle">
          Entenda o que aconteceu em cada etapa do processamento do texto.
        </p>
      </div>

      <div className="pipeline-explanation__grid">
        <div className="pipeline-step">
          <div className="pipeline-step__badge">Camada 0</div>
          <h4 className="pipeline-step__title">Higienização Determinística (&lt; 5ms)</h4>
          <p className="pipeline-step__desc">
            Execução de regras estáticas e dicionários regex sem uso de LLM.
          </p>
          <ul className="pipeline-step__list">
            <li>
              <strong>Marcas e Clichês:</strong> {slopCount} termo(s) sintético(s)
              detectado(s) e substituído(s) por construções mais diretas.
            </li>
            <li>
              <strong>Caracteres Invisíveis:</strong> Limpeza de rastreadores zero-width (ZWSP, ZWNJ, BOM)
              que costumam vir embutidos em cópias de geradores de IA.
            </li>
          </ul>
        </div>

        <div className="pipeline-step">
          <div className="pipeline-step__badge pipeline-step__badge--layer1">Camada 1</div>
          <h4 className="pipeline-step__title">Recomposição de Cadência (Agno + Gemini)</h4>
          <p className="pipeline-step__desc">
            Agentes especialistas em anti-simetria e quebra de paralelismos robóticos.
          </p>
          <ul className="pipeline-step__list">
            <li>
              <strong>Quebra de Monotonia:</strong> Alternância intencional entre períodos curtos e longos,
              elevando a métrica de <em>burstiness</em> para soar natural.
            </li>
            <li>
              <strong>Desconstrução Estrutural:</strong> Eliminação de vícios como listas simétricas forçadas
              e conclusões redundantes (*"em suma"*, *"por fim"*).
            </li>
          </ul>
        </div>

        <div className="pipeline-step">
          <div className={`pipeline-step__badge ${accepted ? "pipeline-step__badge--gate-ok" : "pipeline-step__badge--gate-rejected"}`}>
            Gate
          </div>
          <h4 className="pipeline-step__title">
            Gate de Fidelidade ({accepted ? "Aprovado" : "Recusado"})
          </h4>
          <p className="pipeline-step__desc">
            {accepted
              ? `Aprovado na ${attempts}ª tentativa. O texto preservou os fatos e a essência técnica do original.`
              : `Recusado após ${attempts} tentativas. O texto original higienizado pela Camada 0 foi mantido como salvaguarda.`}
          </p>
          {gateReasons.length > 0 && (
            <div className="pipeline-step__reasons">
              <strong>Motivos apontados pelo gate:</strong>
              <ul>
                {gateReasons.map((reason, idx) => (
                  <li key={idx}>{reason}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
