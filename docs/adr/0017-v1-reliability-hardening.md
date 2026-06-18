# ADR-0017 — Consolidação V1: robustez e adoção

**Status:** Aceito · **Data:** 2026-06-18

## Contexto
Princípio: **confiabilidade e adoção > novas funcionalidades**. Toda a inteligência
construída perde valor se a plataforma quebra, pende ou parece vazia.

## Causa raiz do erro de conexão
Investigação encontrou três falhas estruturais:
1. **Ausência de CORS no backend** — causa nº1. O browser bloqueia o fetch
   cross-origin → `Failed to fetch` → mensagem "não foi possível conectar".
2. **`fetch` sem timeout** — backend lento = spinner infinito.
3. **Sem error boundaries** — erro de render derruba o app (tela branca).

## Decisões — IMPLEMENTAR AGORA
- **CORS middleware** (origens via `FADA_CORS_ORIGINS`, `*` em dev; sem cookies →
  `allow_credentials=False`).
- **Timeout nos fetch** (AbortController no cliente).
- **Error boundaries** (`app/error.tsx` + `global-error.tsx`).
- **`GET /system/status`** (db, modelo, versão, contagens) + página `/system`.
- **`GET /farms/{id}/dashboard`** (agregação determinística) + página `/home`.
- **`POST /demo/seed`** — fazenda de demonstração (o sistema nunca parece vazio).
- **`GET /farms/{id}/operations.csv`** — export CSV (baixo esforço, alta utilidade).
- **Bottom nav mobile** (12 itens de sidebar é demais para celular).
- **Healthcheck da API** no docker-compose.

## ADIAR
- Onboarding wizard dedicado (o fluxo `/farms` + demo + empty-state guiado bastam;
  `CropCycle` já é suficiente para o primeiro uso).
- Export Excel/PDF (CSV primeiro; PDF é esforço alto/valor marginal).
- Playwright/E2E (exige browser real, frágil no ambiente; smoke tests cobrem).
- Container frontend no compose (não verificável aqui; healthcheck + docs por ora).

## DESCARTAR
- Offline/service worker, redesign total de UX, stack pesada de observabilidade —
  complexidade prematura.

## Robustez por design
- React Query isola erros por query: uma falha de endpoint mostra `ErrorBlock` no
  card, **não** derruba as outras páginas. O risco real era CORS (tudo falha),
  timeout (pendura) e crash de render (tela branca) — os três tratados.
- Nenhuma IA generativa no dashboard: tudo determinístico (atenção, agenda, orçamento).

## Consequências
- (+) Plataforma robusta e demonstrável; "por onde começo?" respondido pela /home.
- (−) Sem E2E em browser ainda — coberto por testes de API + smoke.
