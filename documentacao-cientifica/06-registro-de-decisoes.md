# 06 — Registro de Decisões (ADRs)

Consolidação dos **17 Architecture Decision Records (ADRs)** do projeto. Cada ADR registra
uma decisão significativa: o **contexto**, a **decisão** e sua **justificativa**. Os
registros originais completos estão em [`docs/adr/`](../docs/adr/). Aqui apresenta-se a
síntese para referência no relatório.

> Um ADR é um documento curto e datado que responde "por que decidimos assim?". Manter ADRs
> é uma prática de engenharia que torna o raciocínio do projeto **auditável** ao longo do
> tempo — alinhada ao princípio de honestidade do FADA.

---

| # | Título | Decisão (síntese) | Por quê |
|---|---|---|---|
| **0001** | Monólito modular vs. microsserviços | Um único *deploy* com *bounded contexts* (DDD) de fronteiras limpas | Velocidade de iteração e auditabilidade; extrair em serviços só quando a escala exigir |
| **0002** | LLM apenas onde agrega valor | Domínio determinístico; LLM só para orquestração/explicação | O LLM **nunca gera número**; garante reprodutibilidade e auditoria |
| **0003** | Predições com incerteza calibrada; *baseline* antes de *deep learning* | Modelo estatístico interpretável com intervalo medido | Dados e estrutura agronômica favorecem parcimônia; incerteza é requisito, não enfeite |
| **0004** | Seleção parcimoniosa de *features* | Poucas *features* agroclimáticas com mecanismo conhecido | Interpretabilidade e robustez; evita sobreajuste |
| **0005** | *Pooling* regional + separação tendência×clima | Agrupar municípios; isolar tendência temporal do efeito climático | Aproveita homogeneidade regional; coeficientes interpretáveis |
| **0006** | Artefato de modelo interpretável (JSON) | Serializar o modelo em JSON legível (coef., padronização, metadados) | Auditabilidade; nada de binário opaco em produção |
| **0007** | Metodologia do What-If de plantio | Simulação fenológica (GDD) por data candidata | Responde "quando plantar" com base mecanística |
| **0008** | Otimização de plantio ajustada a risco | Critério robusto: esperado vs. *downside*, dentro do ZARC | Nunca reportar data "ótima" sem o risco de cauda |
| **0009** | Persistência de *ground truth* | Entidades Farm/Field/Season/CropCycle/YieldObservation | Fundação do *data flywheel*; ativo longitudinal defensável |
| **0010** | Orchestrator conversacional determinístico-first | Assistente roteia intenção → ferramenta; *fallback* sem LLM | Linguagem natural sem abrir mão do determinismo |
| **0011** | Digital Twin orientado a eventos + Cost Engine | Eventos imutáveis (não *event sourcing* completo); custo por componentes | Preserva história; custo não-linear explícito |
| **0012** | Adaptive Farm Intelligence (encolhimento) | `Regional + correção de viés` com *shrinkage* Normal-Normal | Personaliza com ceticismo; incerteza nunca diminui só por personalizar |
| **0013** | Calibração e confiabilidade | Cobertura + Wilson + diagrama + *pinball*; CRPS descartado | Medir honestidade dos intervalos; métrica coerente com o que se entrega |
| **0014** | Field Intelligence + Insight Engine | Descritivo por talhão; *insights* sob *evidence gating* | Sem prescrição; só afirmar com N e efeito suficientes |
| **0015** | Produto na safra: Quick Capture, Plano e Orçamento | Captura de baixa fricção + plano×real + orçamento | Alimenta o *flywheel* durante a safra |
| **0016** | Camada de apoio à decisão | Atenção por talhão com **alertas nomeados**; sem *score* único | Evita falsa precisão; cada alerta é auditável |
| **0017** | Consolidação V1: robustez e adoção | CORS configurável, *timeouts*, *error boundaries*, demo, onboarding | Transformar fatias em produto utilizável e confiável |

---

## Padrões transversais nas decisões

As 17 decisões compartilham princípios recorrentes:

1. **Determinismo e auditabilidade** (0001, 0002, 0006, 0010) — todo número rastreável.
2. **Incerteza honesta** (0003, 0008, 0012, 0013) — medir e comunicar risco; nunca fingir
   certeza.
3. **Parcimônia sobre complexidade** (0003, 0004, 0011) — só adicionar complexidade que se
   paga.
4. **Evidência antes de afirmação** (0012, 0014, 0016) — *shrinkage* e *evidence gating*.
5. **Sem falsa precisão / sem prescrição** (0014, 0016) — descrever, estimar, alertar — não
   mandar.

Para o texto integral de cada decisão, consulte os arquivos em
[`docs/adr/`](../docs/adr/).
