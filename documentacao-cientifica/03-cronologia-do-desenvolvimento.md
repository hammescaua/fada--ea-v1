# 03 — Cronologia do Desenvolvimento

Registro **etapa a etapa** do desenvolvimento, do repositório vazio ao produto de ponta a
ponta. Cada fase descreve: **objetivo**, **decisões/críticas**, **o que foi construído** e
**validação**. A sequência reflete o histórico de **32 commits** (16–22 de junho de 2026),
desenvolvido em ciclos de *crítica-antes-de-implementar*.

> **Convenção.** Cada fase corresponde a uma fatia vertical funcional (do dado à
> interface). A ordem é a real do histórico Git.

---

## Fase 0 — Fundação (16/06)

**Objetivo.** Estabelecer princípios, arquitetura e o esqueleto do monólito modular.

**Decisões.** Determinístico-first; incerteza como cidadã de primeira classe; *data
flywheel* desde o MVP; monólito modular com *bounded contexts* (DDD) em vez de
microsserviços (ADR-0001). LLM restrito a orquestração/explicação (ADR-0002).

**Construído.** Estrutura de pastas em 4 camadas (API → Serviços → Domínio → Infra);
configuração; *health check*; primeiros ADRs e documentação de arquitetura.

**Validação.** Suíte inicial de testes verde; *lint* limpo.

---

## Fase 1 — MVP Camada 1: Inteligência Regional (16–17/06)

**Objetivo.** Primeira fatia vertical completa: dado município+cultura+safra →
produtividade estimada com incerteza, cenários, riscos e explicação.

**Crítica.** Rejeitou-se *deep learning* (dados insuficientes, baixa interpretabilidade) e
qualquer número gerado por LLM. Optou-se por modelo estatístico interpretável e validação
**temporal** (LOYO), nunca aleatória.

**Construído.**
- Conectores IBGE/PAM, NASA POWER e Open-Meteo (com *fallback* e *cache*);
- Pipeline `build_dataset` (engenharia de *features* agronômicas: GDD, ET0 Hargreaves,
  déficit hídrico reprodutivo, veranico, dias quentes);
- Pipeline `train` comparando Ridge/Random Forest/XGBoost sob LOYO, com MLflow;
- Endpoint `POST /api/v1/regional-intelligence`;
- ADRs do modelo e da validação; exemplos de saída real.

**Validação.** Métricas LOYO por modelo (ver Resultados); testes de domínio e de endpoint.

---

## Fase 2 — Planting Date What-If (17–18/06)

**Objetivo.** Responder "qual a melhor data para plantar?" com **otimização robusta**.

**Crítica.** Recusou-se reportar uma única data "ótima" sem o risco de cauda. A otimização
deve equilibrar resultado esperado e *downside*, dentro do ZARC.

**Construído.**
- Simulação fenológica (GDD) por data candidata; pipeline `build_planting_grid`;
- Endpoint de simulação e de otimização (`planting-window-optimization`) com aversão ao
  risco parametrizável;
- *Backtest* de reconciliação com a média regional.

**Validação.** Reconciliação plantio↔regional (Δ pequeno; ver Resultados); testes.

---

## Fase 3 — Flywheel de dados + Assistente (18/06)

**Objetivo.** Capturar *ground truth* do produtor e oferecer um assistente conversacional.

**Crítica.** O assistente **não** pode inventar números — apenas roteia para serviços
determinísticos. *Fallback* determinístico quando não há chave de LLM.

**Construído.**
- Entidades do *flywheel*: Farm, Field, Season, CropCycle, **YieldObservation**;
- Orquestrador (Claude) que mapeia intenção → ferramenta de domínio;
- Endpoint `POST /api/v1/assistant`.

**Validação.** Testes de roteamento; verificação de que nenhum número provém do LLM.

---

## Fase 4 — Primeiro Frontend (18–19/06)

**Objetivo.** Interface Next.js consumindo os endpoints existentes.

**Construído.** *Scaffold* Next.js (App Router) + TypeScript + Tailwind + TanStack Query +
Recharts; telas iniciais de inteligência regional e plantio; camada `lib/api.ts`.

**Validação.** *Build* do frontend; integração ponta a ponta.

---

## Fase 5 — Digital Twin V1 (19/06)

**Objetivo.** Representar a safra como **sequência de eventos**, não apenas estados.

**Crítica.** Eventos > estados: um `AgriculturalEvent` imutável preserva a história e
habilita auditoria e custo incremental.

**Construído.** Modelo de eventos; **Catálogo de Produtos**; **Cost Engine** (custo/ha,
custo/saca, *break-even*); telas de timeline e custo.

**Validação.** Testes do Cost Engine; exemplo de custo (ver Resultados).

---

## Fase 6 — Adaptive Farm Intelligence (19–20/06)

**Objetivo.** Personalizar a predição por fazenda sem comprometer a incerteza.

**Crítica.** `Predição = Regional + Correção_de_viés`; a incerteza **nunca** diminui só
por personalizar. Encolhimento bayesiano (Normal-Normal) para ceticismo proporcional à
evidência.

**Construído.** Serviço de personalização (shrinkage); endpoint; tela de personalização da
fazenda.

**Validação.** **Property-based testing** (25.000 entradas) garantindo não-estreitamento
do intervalo; demonstração com fazenda sintética (ver Resultados, marcada como sintética).

---

## Fase 7 — Calibração e Confiabilidade (20/06)

**Objetivo.** Responder à pergunta central: **os intervalos comunicados são honestos?**

**Crítica.** Cada métrica foi questionada. Adotaram-se cobertura + **Wilson**, diagrama de
confiabilidade e **pinball loss**; **CRPS descartado** (justificativa na Discussão).
Hipótese a testar: IC_personalizado ≥ IC_regional em acurácia, sem perda de calibração.

**Construído.** Módulo de calibração (`metrics.py`, `report.py`); pipeline
`backtest_calibration`; relatório versionado; tela "Sobre o Modelo" + selo de confiança.

**Validação.** Cobertura observada do IC80 = 79,2% (regional); curva de confiabilidade
quase diagonal; personalização melhora MAE sem degradar calibração (ver Resultados).

---

## Fase 8 — Field Intelligence + Insight Engine (20–21/06)

**Objetivo.** Inteligência por talhão e geração de *insights*.

**Crítica.** *Insights* só sob **evidence gating** (N suficiente e efeito claro); sem
prescrição agronômica.

**Construído.** Inteligência por talhão; **Insight Engine** com limiares de evidência;
telas correspondentes.

**Validação.** Testes de *gating* (não emitir *insight* com evidência insuficiente).

---

## Fase 9 — Produto In-Season (21/06)

**Objetivo.** Uso durante a safra: captura rápida, plano e orçamento.

**Construído.** **Registro rápido** + *presets*; **Plano & Orçamento**; telas in-season.

**Validação.** Testes de serviço; verificação de baixa fricção de captura.

---

## Fase 10 — Decision Support (21/06)

**Objetivo.** "Onde olhar primeiro?" sem um **score mágico**.

**Crítica.** **Recusou-se** um único índice de prioridade (falsa precisão). Em vez disso,
**atenção por talhão** sustentada por **alertas nomeados e auditáveis**.

**Construído.** Decision Engine (`engine.py`); endpoint; tela de Decisões.

**Validação.** Testes do motor de decisão; cada alerta rastreável à sua causa.

---

## Fase 11 — Consolidação V1: robustez (21–22/06)

**Objetivo.** Transformar as fatias em uma V1 sólida e utilizável.

**Problemas resolvidos.**
- **CORS ausente** → erro "não foi possível conectar à API": adicionado `CORSMiddleware`
  com `FADA_CORS_ORIGINS` (ADR de robustez);
- **URL com barra final** → `//api/v1/...` (404): `normalizeBase()` em `lib/api.ts`;
- *Timeouts*, *error boundaries*, *home dashboard*, mobile-first, dados de demonstração,
  exportação.

**Validação.** Conexão ponta a ponta confirmada; testes/lint/build verdes.

---

## Fase 12 — UX V1.1 (22/06)

**Objetivo.** Eliminar fricção (não digitar IDs) e reforçar transparência.

**Construído.** Navegação revista; **contexto global** Fazenda·Safra (React Context +
`localStorage`); remoção de IDs da interface (uso de **nomes**); **onboarding** guiado;
selo de confiança; tela única consolidada; *presets*.

**Validação.** *Build*; fluxo de primeiro acesso (demo/onboarding) verificado.

---

## Fase 13 — Documentação (22/06)

**Objetivo.** Registrar o projeto para estudo e para relatório científico.

**Construído.** **`guia-do-projeto/`** (14 capítulos para leigos) e esta
**`documentacao-cientifica/`** (registro de ponta a ponta para relatório).

---

## Síntese da evolução

| Fase | Entrega | Camada |
|---|---|---|
| 0 | Fundação, arquitetura, ADRs | base |
| 1 | Inteligência Regional (modelo + endpoint) | dado→predição |
| 2 | What-If de data de plantio | decisão |
| 3 | Flywheel + Assistente | captura+linguagem |
| 4 | Primeiro frontend | interface |
| 5 | Digital Twin + Cost Engine | eventos+custo |
| 6 | Personalização (shrinkage) | adaptativo |
| 7 | Calibração e confiabilidade | honestidade |
| 8 | Talhão + Insight Engine | granularidade |
| 9 | In-season (captura, plano, orçamento) | uso na safra |
| 10 | Decision Support (sem score mágico) | priorização |
| 11 | Robustez V1 (CORS, erros, demo) | consolidação |
| 12 | UX V1.1 (contexto global, onboarding) | usabilidade |
| 13 | Documentação (guia + científica) | registro |

O mapeamento detalhado *commit → funcionalidade* está em
[07 — Métricas do Projeto](07-metricas-do-projeto.md).
