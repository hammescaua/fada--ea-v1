# 05 — Discussão

Esta seção interpreta os resultados, **justifica as decisões e descartes**, expõe as
**limitações e ameaças à validade** e aponta o **trabalho futuro**. O fio condutor é o
princípio declarado do projeto: **honestidade acima de esperteza**.

---

## 1. Interpretação dos principais resultados

### 1.1 Um modelo simples, acurado e auditável

O modelo regional alcançou **MAE de 6,96 sc/ha** sob validação temporal *leave-one-year-out*
(LOYO), com uma **regressão Ridge linear**. O XGBoost foi marginalmente melhor (MAE 6,86),
porém a diferença (~0,1 sc/ha) **não justifica** abrir mão da interpretabilidade. O modelo
linear entrega **coeficientes auditáveis**: o **déficit hídrico reprodutivo** domina
(−456 kg/ha por desvio-padrão), seguido do **veranico reprodutivo** (−81,5) — exatamente os
mecanismos que a agronomia da soja prevê como críticos. Essa **validade de conteúdo** (o
modelo "acerta pelos motivos certos") é, num sistema de decisão, tão importante quanto a
acurácia bruta. Um modelo opaco com 0,1 sc/ha a menos de erro seria um mau negócio para a
confiança do produtor.

### 1.2 Os intervalos são honestos

A pergunta central do projeto — *"os intervalos comunicados são realmente honestos?"* —
recebeu resposta empírica afirmativa. A **cobertura observada do IC80 foi 79,2%** e o
**diagrama de confiabilidade é quase diagonal** (desvios ≤ ~1,1 p.p. em todos os níveis de
0,5 a 0,95). Em um domínio onde "resposta confiante e errada destrói confiança", demonstrar
calibração é um resultado de primeira ordem, não um detalhe técnico.

### 1.3 Personalização que melhora sem enganar

A camada adaptativa **reduziu o MAE de 6,96 para 6,65 sc/ha** e a *pinball loss* de 2,254
para 2,18, **sem estreitar o intervalo** (largura 22,35 → 22,53). Isso confirma a hipótese
**IC_personalizado ≥ IC_regional**: ganha-se acurácia **sem** comprar uma falsa sensação de
certeza. O encolhimento bayesiano garante que fazendas com pouco histórico sejam tratadas
com ceticismo (no exemplo sintético, viés real de +12% aplicado como +9,3% com n=10), e a
**garantia de não-estreitamento foi verificada formalmente** por *property-based testing*
sobre 25.000 entradas.

---

## 2. Decisões deliberadas e descartes justificados

A disciplina de **crítica-antes-de-implementar** levou a rejeitar várias opções
aparentemente atraentes. Os descartes são, eles próprios, um resultado científico.

### 2.1 Sem *deep learning* (nesta escala de dados)
Com 787 observações e forte estrutura agronômica conhecida, *deep learning* ofereceria
baixa interpretabilidade e alto risco de sobreajuste, sem ganho esperado sobre um linear
bem-especificado. **Descartado** em favor de modelos parcimoniosos (ADR-0003/0004).

### 2.2 Sem validação cruzada aleatória
*k-fold* embaralhado **vaza futuro no passado** em séries temporais e infla o desempenho.
Usou-se **exclusivamente LOYO**. Esta é, possivelmente, a decisão metodológica mais
importante para a honestidade das métricas reportadas.

### 2.3 Sem *score* único de prioridade
Um índice mágico de prioridade comunica **falsa precisão** e esconde o porquê. A camada de
decisão entrega **atenção por talhão com alertas nomeados e auditáveis** (ADR-0016), cada
um rastreável à sua causa.

### 2.4 Sem prescrição agronômica
O sistema **descreve e estima**, mas não prescreve dose/produto — evita responsabilidade
agronômica indevida e mantém o produtor/agrônomo no controle (ADR-0014/0016).

### 2.5 CRPS descartado (nesta fase)
O *Continuous Ranked Probability Score* exige uma **distribuição preditiva completa**. O
produto comunica **quantis/cenários**, para os quais a **pinball loss** é a métrica própria
e diretamente interpretável. Adotar CRPS exigiria assumir/forçar uma forma distribucional
que o sistema deliberadamente não comunica. **Descartado por coerência** entre o que se mede
e o que se entrega (ADR-0013).

### 2.6 Sem extrapolação linear de custo
Custos não escalam linearmente com a área; o Cost Engine modela componentes explícitos em
vez de multiplicar um custo/ha por hectares (ADR-0011/0015).

### 2.7 LLM nunca gera número
Toda saída numérica vem de serviço de domínio determinístico; o LLM apenas roteia e explica,
com *fallback* determinístico. É o pilar de auditabilidade do sistema (ADR-0002/0010).

---

## 3. Limitações e ameaças à validade

### 3.1 Calibração via proxy municipal (limitação central)
A validação de calibração usa **municípios como proxy de fazendas**: a "verdade-terreno" é
o rendimento **municipal** (IBGE/PAM), não o de uma fazenda individual. Logo, a cobertura de
79,2% é honesta **no nível municipal**; a calibração **no nível de fazenda** permanece a ser
confirmada à medida que o *flywheel* acumular observações reais de produtores. Esta é a
limitação mais importante a declarar.

### 3.2 Demonstração da personalização é sintética
A recuperação de viés (+12% → 12,1% estimado, +9,3% aplicado) usa uma **fazenda fictícia**.
Demonstra o **mecanismo**, não desempenho em campo real. Validação real depende de dados
longitudinais que o produto começa a capturar agora.

### 3.3 *Features* climáticas de reanálise
NASA POWER e Open-Meteo (ERA5) são **reanálises** em grade, não estações na lavoura. Há erro
de representatividade espacial, sobretudo para fenômenos locais (veranicos, granizo).

### 3.4 Escopo geográfico e cultural
O sistema foi calibrado para **soja na microrregião de Três Passos**. Generalização para
outras culturas/regiões é arquiteturalmente prevista (parâmetros, não *hard-code*), mas
**não validada empiricamente** aqui.

### 3.5 Tendência temporal e extrapolação
O coeficiente de ano (+525 kg/ha) captura tendência tecnológica histórica; **extrapolar**
essa tendência para o futuro assume sua continuidade, o que pode falhar (saturação, choques
climáticos).

### 3.6 Horizonte temporal de desenvolvimento
O sistema foi construído em **uma janela curta e intensiva** (16–22/06/2026). Embora cada
incremento seja testado, o produto não passou por um ciclo de safra real completo nem por
uso prolongado por produtores.

---

## 4. Trabalho futuro

1. **Validação de calibração em nível de fazenda** assim que o *flywheel* acumular
   observações reais (o teste decisivo da limitação 3.1).
2. **Reespecificação periódica** dos quantis de resíduo e dos coeficientes a cada nova
   safra (re-treino versionado via DVC/MLflow).
3. **Incorporação de dados de campo** (estações, sensores, imagens) para reduzir o erro de
   representatividade das reanálises.
4. **Expansão controlada** para outras microrregiões/culturas, com revalidação temporal
   específica antes de qualquer comunicação ao usuário.
5. **Reavaliação do CRPS** se/quando o produto passar a comunicar distribuições preditivas
   completas em vez de cenários discretos.
6. **Estudos de uso** com produtores para medir fricção de captura e efeito do selo de
   confiança sobre a tomada de decisão.

---

## 5. Conclusão da discussão

O FADA demonstra que é possível construir um sistema de apoio à decisão agrícola
**determinístico, calibrado e auditável**, em que cada número tem origem rastreável e cada
faixa de incerteza é **medida, não afirmada**. Os resultados (modelo interpretável com
MAE 6,96 sc/ha; IC80 com cobertura 79,2%; personalização que melhora sem estreitar
indevidamente) sustentam a viabilidade da abordagem. As limitações — sobretudo a calibração
via proxy municipal — são declaradas abertamente, em coerência com o princípio que orientou
todo o desenvolvimento: **preferir dizer "ainda não sei" a inventar**.
