# 07 — Métricas do Projeto

Métricas quantitativas do **artefato de software** e do **processo de desenvolvimento**,
úteis para caracterizar o esforço e a maturidade do sistema no relatório. Todos os valores
foram extraídos diretamente do repositório versionado.

---

## 1. Dimensão do código e da documentação

| Métrica | Valor |
|---|---:|
| LOC backend (aplicação, Python) | **8.974** |
| LOC pipelines (Python) | **841** |
| LOC frontend (TypeScript/TSX) | **7.668** |
| LOC documentação (Markdown) | **3.317** |
| **Total aproximado** | **~20.800 LOC** |

## 2. Qualidade e verificação

| Métrica | Valor |
|---|---:|
| Testes automatizados (pytest) | **164** |
| Arquivos de teste | 27 |
| Entradas no *property-based test* de não-estreitamento do intervalo | 25.000 |
| *Lint* (ruff) | limpo |
| *Build* do frontend | OK |

## 3. Superfície funcional

| Métrica | Valor |
|---|---:|
| Endpoints de API declarados | **41** |
| Contextos de domínio (DDD) | **15** |
| Páginas do frontend | ~14 |
| ADRs (registros de decisão) | **17** |

## 4. Dados e modelo

| Métrica | Valor |
|---|---:|
| Linhas do dataset de *features* | **787** |
| Municípios | 20 |
| Período | 1980–2024 |
| Modelos comparados | 3 (Ridge, Random Forest, XGBoost) |
| Modelo em produção | Ridge linear (interpretável) |
| MAE LOYO (produção) | 6,96 sc/ha |
| Cobertura IC80 (regional) | 0,792 |

## 5. Processo de desenvolvimento

| Métrica | Valor |
|---|---:|
| Commits | **32** |
| Janela de desenvolvimento | 16–22 de junho de 2026 (7 dias) |
| Separação backend/frontend | consistente (commits dedicados) |
| Idioma de commits/UI/docs | Português |

---

## 6. Mapeamento *commit → funcionalidade*

Histórico completo (ordem cronológica real), evidenciando a cadência **backend → frontend**
por fatia vertical:

| # | Hash | Data | Mensagem | Fase |
|---:|---|---|---|---|
| 1 | ae4d14d | 16/06 | Initial commit | 0 — Fundação |
| 2 | 6049c70 | 16/06 | Funda FADA: arquitetura, roadmap e esqueleto do MVP | 0 — Fundação |
| 3 | f9a40f9 | 17/06 | MVP Camada 1: Inteligência Regional ponta a ponta | 1 — Regional |
| 4 | a5d3c0f | 17/06 | Planting Date What-If: simulação e otimização robusta | 2 — Plantio |
| 5 | 185ba08 | 17/06 | Flywheel de ground truth, Digital Twin (fundação) e orchestrator | 3 — Flywheel |
| 6 | 9ad9fc1 | 17/06 | Frontend Next.js: 5 páginas consumindo os endpoints | 4 — Frontend |
| 7 | b78be1f | 17/06 | Digital Twin V1: timeline de eventos + Cost Engine | 5 — Digital Twin |
| 8 | ee23215 | 17/06 | Frontend Digital Twin: páginas Safra e Financeiro | 5 — Digital Twin |
| 9 | 38773de | 17/06 | Adaptive Farm Intelligence: encolhimento hierárquico | 6 — Adaptativo |
| 10 | bf53e4e | 17/06 | Frontend: Inteligência Adaptativa (regional vs personalizado) | 6 — Adaptativo |
| 11 | 0a1e0f8 | 17/06 | Calibração e confiabilidade (ADR-0013) | 7 — Calibração |
| 12 | 26e4ef4 | 17/06 | Frontend: Calibração (reliability diagram) | 7 — Calibração |
| 13 | ede383c | 17/06 | Field Intelligence + Insight Engine (ADR-0014) | 8 — Talhão/Insights |
| 14 | a5979b9 | 17/06 | Frontend: Inteligência por Talhão | 8 — Talhão/Insights |
| 15 | da69e10 | 18/06 | Produto na safra: Quick Capture, Plano e Orçamento (ADR-0015) | 9 — In-season |
| 16 | f5b4e93 | 18/06 | Frontend: Plano & Orçamento | 9 — In-season |
| 17 | 9c7ed73 | 18/06 | Camada de apoio à decisão (ADR-0016) | 10 — Decisões |
| 18 | 28beef7 | 18/06 | Frontend: Decisões (heatmap de atenção explicável) | 10 — Decisões |
| 19 | 8f7cf6c | 18/06 | V1 robustez: CORS, /system, dashboard, demo, export (ADR-0017) | 11 — Robustez |
| 20 | c9ff5b7 | 19/06 | Frontend V1: /home, /system, error boundaries, timeout, nav | 11 — Robustez |
| 21 | 1ececb6 | 19/06 | Raiz amigável no backend (/ -> links úteis) | 11 — Robustez |
| 22 | 3379d6e | 19/06 | Frontend: normaliza NEXT_PUBLIC_API_URL (corrige 404) | 11 — Robustez |
| 23 | b384b35 | 19/06 | Backend: GET /farms/{id}/crop-cycles p/ contexto global | 12 — UX V1.1 |
| 24 | bfa5d98 | 19/06 | Frontend UX V1.1: contexto global Fazenda·Safra, nav por tarefa | 12 — UX V1.1 |
| 25 | 278c3c0 | 19/06 | Backend: raciocínio estruturado no regional (transparência) | 12 — UX V1.1 |
| 26 | 233e606 | 19/06 | Frontend: transparência ("Como chegamos nisso") | 12 — UX V1.1 |
| 27 | bf20d5b | 19/06 | Frontend: "Minha Lavoura" como tela única da safra | 12 — UX V1.1 |
| 28 | 45b53b4 | 19/06 | Frontend: registro rápido na Início + selo de confiança | 12 — UX V1.1 |
| 29 | b538d13 | 19/06 | Frontend: presets (operações favoritas) no registro rápido | 12 — UX V1.1 |
| 30 | 3246cb9 | 22/06 | Conclusão V1: docs (README, V1_OVERVIEW) e .env.example | 13 — Documentação |
| 31 | 0d35444 | 22/06 | Frontend: onboarding em wizard (fecha o plano UX V1.1) | 12/13 |
| 32 | f442d38 | 22/06 | Guia completo do projeto para leigos (14 capítulos) | 13 — Documentação |

> Este documento (`documentacao-cientifica/`) é registrado em commit subsequente ao da
> tabela, fechando o ciclo de documentação.

---

## 7. Leitura das métricas

- **Equilíbrio backend/frontend** (~9k vs ~7,7k LOC) reflete um produto **de ponta a
  ponta**, não um protótipo de modelo isolado.
- **164 testes para ~17,6k LOC de aplicação** indica densidade de verificação alta para um
  artefato desenvolvido em janela curta.
- A **cadência commit a commit** (backend imediatamente seguido do frontend
  correspondente) evidencia o método de **fatias verticais funcionais**.
- **17 ADRs em 32 commits** mostra que ~metade das unidades de trabalho carregou uma
  decisão arquitetural registrada — um indicador de desenvolvimento **deliberado e
  auditável**.
