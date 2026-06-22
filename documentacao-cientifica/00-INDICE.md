# Documentação Científica do Desenvolvimento — FADA

> **Propósito.** Esta pasta registra, de ponta a ponta, **todo o processo de
> desenvolvimento** do FADA (Farm AI Decision Agent), com decisões, mudanças, métodos,
> testes e **resultados quantitativos reais**. Foi organizada para servir de base direta
> às seções de *Materiais e Métodos*, *Resultados* e *Discussão* de um relatório de
> pesquisa científico.

## Como usar este registro no seu relatório

| Seção do seu relatório | Documento desta pasta |
|---|---|
| Metodologia (como o sistema foi desenvolvido) | **[01 — Resumo e Metodologia](01-resumo-e-metodologia.md)** |
| Materiais e Métodos (dados, técnicas, ferramentas) | **[02 — Materiais e Métodos](02-materiais-e-metodos.md)** |
| Desenvolvimento / Cronologia (o processo, etapa a etapa) | **[03 — Cronologia do Desenvolvimento](03-cronologia-do-desenvolvimento.md)** |
| **Resultados** (números, tabelas) | **[04 — Resultados](04-resultados.md)** |
| **Discussão** (interpretação, limitações, validade) | **[05 — Discussão](05-discussao.md)** |
| Decisões de projeto (registro) | **[06 — Registro de Decisões (ADRs)](06-registro-de-decisoes.md)** |
| Métricas do artefato de software | **[07 — Métricas do Projeto](07-metricas-do-projeto.md)** |

## Aviso de integridade dos dados (importante para o rigor)

Todos os números deste registro foram **extraídos diretamente dos artefatos versionados**
do projeto (modelo treinado, relatório de calibração, suíte de testes, histórico Git) e
são **reprodutíveis**. Onde um resultado se baseia em **dados sintéticos** (ex.: a
demonstração da personalização com uma fazenda fictícia, na ausência de dado real de
fazenda), isso está **explicitamente marcado** como tal. Limitações e ameaças à validade
estão na seção de Discussão.

## Resumo de uma frase

Desenvolveu-se, em ciclos iterativos com **crítica-antes-de-implementar** e **verificação
por testes automatizados**, um sistema determinístico de apoio à decisão agrícola para
soja (Noroeste do RS), cujo modelo regional é **estatisticamente calibrado** (cobertura
observada do intervalo de 80% = 79,2%) e cuja camada de personalização melhora a acurácia
(MAE 6,96 → 6,65 sc/ha) **sem comprometer a honestidade da incerteza**.
