# 02 — Materiais e Métodos

Este documento descreve as **fontes de dados**, os **métodos estatísticos e agronômicos**,
as **ferramentas** e os **procedimentos de reprodutibilidade** empregados no
desenvolvimento e na avaliação do FADA. Está organizado para ser citável diretamente na
seção *Materiais e Métodos* de um relatório científico.

---

## 1. Área de estudo e cultura

- **Cultura:** soja (*Glycine max*).
- **Recorte geográfico:** microrregião de **Três Passos**, Noroeste do Rio Grande do Sul,
  Brasil, com **20 municípios** considerados (incluindo Horizontina, Três de Maio, Santa
  Rosa, Tucunduva, entre outros).
- **Recorte temporal:** safras de **1980 a 2024** (séries anuais).

A escolha da microrregião segue o princípio de **profundidade antes de amplitude**:
modelar bem um sistema agrícola homogêneo (mesmo regime climático, mesma cultura
dominante) antes de generalizar. A arquitetura, contudo, não tem nada específico de soja
ou de Três Passos *hard-coded* — cultura e região são parâmetros.

---

## 2. Fontes de dados

Todas as fontes são **públicas e auditáveis**. Os conectores de ingestão preveem
*fallback* e *cache* local para garantir reprodutibilidade mesmo diante de instabilidade
das APIs externas.

### 2.1 Produtividade histórica (variável-resposta / *ground truth*)

- **Fonte:** IBGE — **Produção Agrícola Municipal (PAM)**, via API SIDRA.
- **Variável:** rendimento médio (kg/ha) de soja por município e ano, convertido para
  **sacas por hectare** (sc/ha; 1 saca = 60 kg).
- **Papel:** é a **verdade-terreno** contra a qual o modelo é treinado e validado.

### 2.2 Variáveis climáticas (preditoras)

- **Fontes:** **NASA POWER** (reanálise climática) como fonte primária e **Open-Meteo**
  (*Historical Weather API*, base ERA5) como fonte alternativa/redundante.
- **Variáveis brutas diárias:** precipitação, temperatura máxima e mínima, radiação.
- **Papel:** insumo para a engenharia de *features* agronômicas (Seção 4).

### 2.3 Dados de conjuntura (melhor esforço)

- **Fonte:** **CONAB** (Companhia Nacional de Abastecimento) para safras/preços de
  referência, usada em caráter de melhor esforço.

### 2.4 Dados da propriedade (*flywheel*)

- **Origem:** informados pelo próprio produtor através da interface (fazenda, talhão,
  safra, ciclo de cultura, **produtividade observada**, eventos de manejo e custos).
- **Papel:** alimentam a **personalização por fazenda** (Seção 5.4) e constituem o ativo
  longitudinal que melhora o sistema a cada safra registrada.

> **Dimensão do conjunto consolidado:** o dataset de *features* versionado contém
> **787 linhas** (combinações município × ano com resposta e preditoras completas).

### 2.5 Como citar as fontes (sugestão)

- IBGE. *Produção Agrícola Municipal (PAM)*. Sistema IBGE de Recuperação Automática
  (SIDRA). Instituto Brasileiro de Geografia e Estatística.
- NASA. *POWER — Prediction Of Worldwide Energy Resources*. NASA Langley Research Center.
- Open-Meteo. *Historical Weather API* (reanálise ERA5).
- CONAB. *Acompanhamento da Safra Brasileira de Grãos*. Companhia Nacional de
  Abastecimento.

---

## 3. Métodos agronômicos (engenharia de *features*)

As variáveis climáticas diárias foram transformadas em **indicadores agronômicos**
interpretáveis, alinhados às fases fenológicas da soja. Esta etapa incorpora conhecimento
de domínio explícito (em vez de delegar a descoberta de padrões a um modelo opaco).

### 3.1 Fenologia por graus-dia (GDD)

As fases de desenvolvimento foram estimadas por **acúmulo térmico** (*Growing Degree
Days*):

```
GDD_dia = max(0, (T_max + T_min) / 2 − T_base)
```

com **T_base = 10 °C** para a soja. O acúmulo de GDD a partir da data de plantio delimita
as janelas **vegetativa** e **reprodutiva** (R1–R6), permitindo computar índices
específicos da fase crítica.

### 3.2 Evapotranspiração de referência (ET0) — Hargreaves

Na ausência de dados completos para Penman-Monteith, adotou-se a equação de
**Hargreaves-Samani**, que requer apenas temperaturas extremas e radiação extraterrestre:

```
ET0 = 0,0023 · Ra · (T_med + 17,8) · (T_max − T_min)^0,5
```

A escolha privilegia **robustez com dados esparsos** sobre a precisão marginal de métodos
mais exigentes em dados.

### 3.3 Balanço hídrico e indicadores de estresse

A partir de precipitação e ET0 derivaram-se, com ênfase na **fase reprodutiva** (a mais
sensível ao estresse hídrico na soja):

- **Déficit hídrico reprodutivo (mm)** — soma de (ET0 − precipitação) positiva na janela
  reprodutiva;
- **Veranico mais longo no período reprodutivo (dias)** — maior sequência de dias secos;
- **Dias quentes no período reprodutivo** — contagem de dias acima de limiar de
  temperatura;
- **Precipitação total da safra (mm)**.

Essas *features* foram escolhidas por terem **mecanismo agronômico conhecido**, o que
torna os coeficientes do modelo interpretáveis e auditáveis (ver Resultados).

---

## 4. Métodos estatísticos e de aprendizado de máquina

### 4.1 Modelo preditivo regional

Foram **comparados três modelos** sob validação temporal idêntica:

- **Regressão Ridge** (linear regularizada);
- **Random Forest**;
- **XGBoost** (*gradient boosting*).

O modelo de produção foi escolhido considerando **acurácia E interpretabilidade**
(ver decisão em Resultados/Discussão). O artefato do modelo é serializado em **JSON
legível** (coeficientes, médias e desvios de padronização, metadados), não em formato
binário opaco — uma decisão deliberada de auditabilidade.

### 4.2 Validação temporal *leave-one-year-out* (LOYO)

A capacidade preditiva foi estimada por **deixe-um-ano-de-fora**: para cada ano *t*, o
modelo é treinado em todos os anos ≠ *t* e avaliado em *t*. Métricas reportadas: **MAE**
(erro absoluto médio) e **RMSE** (raiz do erro quadrático médio), em sc/ha.

**Justificativa:** validação cruzada aleatória (*k-fold* embaralhado) **vaza informação
do futuro para o passado** em séries temporais, superestimando o desempenho. LOYO
respeita a ordem temporal e simula o uso real (prever uma safra futura com o passado).

### 4.3 Quantificação de incerteza (intervalos preditivos)

Os intervalos preditivos foram construídos a partir dos **quantis dos resíduos**
*out-of-fold* da validação LOYO (abordagem de inspiração **conformal**, livre de
suposição de normalidade). Os quantis empíricos dos resíduos (p5, p10, p50, p90, p95)
definem as bordas dos intervalos e os **cenários** (pessimista/normal/otimista).

### 4.4 Avaliação da calibração

A **honestidade** dos intervalos foi medida empiricamente:

- **Cobertura observada** — fração das observações de teste contidas no intervalo nominal
  (ex.: o intervalo de 80% deveria conter ~80% dos casos);
- **Intervalo de confiança de Wilson** sobre a cobertura — para julgar se o desvio entre
  cobertura nominal e observada é estatisticamente significativo (preferido ao intervalo
  normal por bom comportamento com proporções e amostras moderadas);
- **Diagrama de confiabilidade** (*reliability diagram*) — cobertura observada vs. nominal
  em vários níveis (0,5/0,6/0,7/0,8/0,9/0,95);
- **Pinball loss** (perda quantílica) — função de pontuação própria para avaliar quantis;
- **Largura média do intervalo** — para penalizar intervalos honestos porém inúteis de
  tão largos (*sharpness* sob calibração).

> **Nota sobre o CRPS.** O *Continuous Ranked Probability Score* foi considerado e
> **deliberadamente descartado** nesta fase (justificativa na Discussão): ele exige uma
> distribuição preditiva completa, ao passo que o produto comunica **quantis/cenários**,
> para os quais a *pinball loss* é a métrica própria e diretamente interpretável.

### 4.5 Personalização por fazenda — encolhimento bayesiano

A predição personalizada segue o modelo aditivo:

```
Predição_fazenda = Modelo_regional + Correção_de_viés
```

A **correção de viés** é estimada por **encolhimento (shrinkage) Normal-Normal**: o viés
observado da fazenda (média dos resíduos do produtor frente ao regional) é **puxado em
direção a zero** proporcionalmente à escassez de evidência. Com poucos anos de dado, a
correção é fortemente atenuada; com muitos anos consistentes, aproxima-se do viés bruto.

Princípio inviolável: a personalização pode **deslocar** a predição, mas **nunca estreita
o intervalo** apenas por personalizar (a incerteza só diminui com evidência genuína). Essa
garantia foi verificada por **teste baseado em propriedade** sobre **25.000 entradas
aleatórias**.

### 4.6 Otimização da data de plantio (robusta)

A janela de plantio foi avaliada por **simulação fenológica** ao longo de datas
candidatas dentro do **ZARC** (Zoneamento Agrícola de Risco Climático). Para cada data,
estimou-se a distribuição de resultados sobre os anos históricos e otimizou-se um
**critério robusto** que pondera o resultado esperado contra o **risco de cauda inferior**
(*downside*), parametrizado por uma aversão ao risco. Não se reporta uma única data
"ótima" sem o respectivo *downside*.

---

## 5. Ferramentas e ambiente computacional

| Camada | Tecnologias |
|---|---|
| Linguagem (backend) | Python 3.11 |
| API | FastAPI, Pydantic v2 |
| Persistência | SQLAlchemy 2.0 (SQLite por padrão; PostgreSQL opcional) |
| ML / estatística (offline) | scikit-learn, XGBoost, NumPy, pandas |
| Testes | pytest (incl. *property-based testing*) |
| Qualidade de código | ruff (*lint*) |
| Reprodutibilidade | params.yaml, DVC (`dvc.yaml`), MLflow |
| LLM (orquestração/explicação) | Claude (Anthropic) — opcional, com *fallback* determinístico |
| Frontend | Next.js (App Router), TypeScript, Tailwind CSS, TanStack React Query, Recharts |

O LLM atua **somente** no roteamento de intenções e na explicação em linguagem natural;
na ausência de chave de API, um *fallback* determinístico mantém o sistema funcional. **O
LLM nunca gera números.**

---

## 6. Reprodutibilidade

- **Parâmetros versionados** em `params.yaml` (sementes, limiares, hiperparâmetros).
- **Grafo de execução** em `dvc.yaml` (ingestão → *features* → treino → calibração).
- **Rastreamento de experimentos** em **MLflow** (métricas e comparação de modelos).
- **Artefatos versionados** no repositório: modelo treinado (JSON), conjunto de *features*
  (CSV) e relatório de calibração — o sistema funciona *out-of-the-box* e os resultados são
  reproduzíveis.
- **Pipelines executáveis:**
  ```bash
  python -m pipelines.build_dataset         # IBGE + Open-Meteo/NASA -> features
  python -m pipelines.train                 # compara Ridge/RF/XGBoost -> models (MLflow)
  python -m pipelines.build_planting_grid   # grade de data de plantio (fenologia GDD)
  python -m pipelines.backtest_calibration  # relatório de calibração
  ```

---

## 7. Procedimento de desenvolvimento e verificação

Cada incremento funcional seguiu o ciclo: **crítica → implementação → verificação**. A
verificação compreendeu execução da suíte de **testes automatizados** (final: 164 testes),
*lint* (ruff) e *build* do frontend antes de cada *commit*. O histórico foi mantido em
**commits descritivos** com separação entre *backend* e *frontend*. Detalhes na
[Cronologia](03-cronologia-do-desenvolvimento.md) e nas [Métricas](07-metricas-do-projeto.md).
