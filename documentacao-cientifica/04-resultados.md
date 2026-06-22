# 04 — Resultados

Esta seção reúne os **resultados quantitativos** do FADA, extraídos diretamente dos
artefatos versionados (modelo treinado, relatório de calibração, suíte de testes,
histórico Git). Todos os números são **reprodutíveis** pelos pipelines descritos em
[Materiais e Métodos](02-materiais-e-metodos.md). Resultados baseados em **dados
sintéticos** estão **explicitamente marcados**.

Unidade padrão: **sacas por hectare (sc/ha)**, 1 saca = 60 kg.

---

## 1. Conjunto de dados

| Atributo | Valor |
|---|---|
| Linhas (município × ano com resposta e preditoras completas) | **787** |
| Municípios | **20** |
| Período | **1980–2024** |
| Variável-resposta | rendimento de soja (sc/ha), fonte IBGE/PAM |
| Preditoras principais | déficit hídrico reprodutivo, veranico reprodutivo, dias quentes reprodutivos, precipitação total, ano |

---

## 2. Comparação de modelos (validação *leave-one-year-out*)

Métricas *out-of-fold* sob validação temporal LOYO:

| Modelo | MAE (sc/ha) | RMSE (sc/ha) |
|---|---|---|
| **Ridge (linear)** — *em produção* | **6,96** | **8,85** |
| Random Forest | 7,35 | 9,60 |
| XGBoost | 6,86 | 8,79 |

**Observação.** O XGBoost obteve o melhor desempenho na validação (MAE 6,86), mas a
**diferença frente ao Ridge é marginal** (≈0,10 sc/ha de MAE). O modelo **Ridge linear**
foi escolhido para produção por sua **interpretabilidade** (coeficientes auditáveis,
artefato JSON legível) — uma decisão de *honestidade e auditabilidade sobre ganho marginal
de acurácia* (ver Discussão).

---

## 3. Coeficientes do modelo em produção (Ridge)

Efeito de cada *feature* sobre o rendimento, em **kg/ha por desvio-padrão** da variável
(sinal e magnitude interpretáveis):

| *Feature* | Coeficiente (kg/ha por desvio-padrão) | Leitura agronômica |
|---|---:|---|
| Déficit hídrico reprodutivo (mm) | **−456,3** | maior estresse hídrico na fase crítica → menor rendimento (efeito dominante) |
| Veranico mais longo reprodutivo (dias) | **−81,5** | sequências secas na floração/enchimento reduzem o rendimento |
| Precipitação total da safra (mm) | **−62,1** | excesso/distribuição desfavorável associado a perda |
| Dias quentes reprodutivos | **−4,7** | estresse térmico na fase crítica |
| Ano de colheita | **+525,4** | tendência tecnológica positiva ao longo do tempo |

O **déficit hídrico reprodutivo** é, de longe, o fator de maior impacto — coerente com o
conhecimento agronômico da soja, o que reforça a validade de conteúdo do modelo.

---

## 4. Incerteza: quantis dos resíduos (LOYO)

Quantis empíricos dos resíduos *out-of-fold* que definem cenários e bordas dos intervalos:

| Quantil | Resíduo (sc/ha) |
|---|---:|
| p5 | −15,77 |
| p10 | −11,70 |
| p50 | +0,38 |
| p90 | +10,76 |
| p95 | +14,43 |

A mediana próxima de zero (+0,38) indica **ausência de viés sistemático** relevante no
modelo regional.

---

## 5. Calibração dos intervalos (LOYO, n = 787)

### 5.1 Métricas agregadas

| Métrica | Modelo Regional | Personalizado |
|---|---:|---:|
| Cobertura do IC 80% (alvo 0,80) | **0,792** | 0,807 |
| MAE (sc/ha) | 6,96 | **6,65** |
| RMSE (sc/ha) | 8,85 | **8,61** |
| Viés (sc/ha) | 0,16 | 0,29 |
| Largura média do intervalo (sc/ha) | 22,35 | 22,53 |
| Pinball loss (média) | 2,254 | **2,18** |

**Leitura.** A cobertura observada do intervalo de 80% é **79,2%** (regional) — praticamente
sobre o alvo nominal, indicando **intervalos honestos**. A personalização **melhora a
acurácia** (MAE 6,96 → 6,65; RMSE 8,85 → 8,61; pinball 2,254 → 2,18) **sem estreitar
indevidamente** o intervalo (largura essencialmente igual: 22,35 → 22,53), confirmando a
hipótese **IC_personalizado ≥ IC_regional** em qualidade preditiva, com incerteza
preservada.

### 5.2 Diagrama de confiabilidade (Regional)

Cobertura observada vs. nominal em múltiplos níveis:

| Nível nominal | Cobertura observada |
|---:|---:|
| 0,50 | 0,489 |
| 0,60 | 0,593 |
| 0,70 | 0,691 |
| 0,80 | 0,792 |
| 0,90 | 0,893 |
| 0,95 | 0,942 |

A curva é **quase diagonal** (desvios ≤ ~1,1 ponto percentual), evidência forte de
**calibração**: quando o sistema diz "80%", acerta perto de 80% das vezes.

---

## 6. Personalização — demonstração (DADOS SINTÉTICOS)

> ⚠️ **Aviso.** Na ausência de série longitudinal real de uma fazenda específica, a
> personalização foi demonstrada com uma **fazenda sintética**. Os números abaixo são de
> **demonstração do mecanismo**, não de validação em campo real.

- Fazenda sintética com viés real de **+12%** sobre o regional;
- Viés **recuperado** pelo estimador: **12,1%** (recuperação quase exata do sinal);
- Viés **aplicado** após encolhimento: **+9,3%** (n = 10 observações, confiança 77%) — a
  atenuação reflete o ceticismo bayesiano proporcional à evidência;
- **Intervalo não estreitado** pela personalização (consistente com o princípio e com o
  *property-based test* de 25.000 entradas).

---

## 7. Reconciliação plantio ↔ regional

- **Linha de base** (plantio ~1º de novembro): produtividade simulada **52,4 sc/ha** vs.
  **51,2 sc/ha** do modelo regional → **Δ +1,2 sc/ha** (boa concordância entre o simulador
  fenológico e o modelo estatístico independente).
- **Otimização (Horizontina):** melhor data **30/11**, com *score* robusto **50,3**,
  esperado **54,8 sc/ha** e **cauda inferior (*downside*) 45,7 sc/ha** — a data ótima é
  sempre reportada **com** seu risco de cauda, nunca isolada.

---

## 8. Exemplo de custo e margem (Cost Engine)

Cenário ilustrativo (100 ha, custo total R$ 260 mil):

| Indicador | Valor |
|---|---:|
| Custo por hectare | R$ 2.600/ha |
| Custo por saca | R$ 50,73/saca |
| *Break-even* (produtividade de equilíbrio) | **20,8 sc/ha** |

O *break-even* de ~20,8 sc/ha, bem abaixo das estimativas de ~50 sc/ha, contextualiza a
margem de segurança da safra para o produtor.

---

## 9. Métricas do artefato de software

| Métrica | Valor |
|---|---:|
| Testes automatizados (pytest) | **164** (27 arquivos de teste) |
| *Property-based*: entradas no teste de não-estreitamento | 25.000 |
| Endpoints de API declarados | 41 |
| Contextos de domínio (DDD) | 15 |
| ADRs (registros de decisão) | 17 |
| Commits | 32 |
| LOC backend (app) | 8.974 |
| LOC pipelines | 841 |
| LOC frontend (ts/tsx) | 7.668 |
| LOC documentação (markdown) | 3.317 |

Detalhamento e mapeamento *commit → funcionalidade* em
[07 — Métricas do Projeto](07-metricas-do-projeto.md).

---

## 10. Síntese dos resultados

1. **Modelo regional acurado e interpretável:** MAE LOYO de 6,96 sc/ha com Ridge linear;
   coeficiente dominante (déficit hídrico reprodutivo, −456 kg/ha por desvio-padrão)
   agronomicamente coerente.
2. **Intervalos honestos:** cobertura do IC80 = 79,2% e diagrama de confiabilidade quase
   diagonal.
3. **Personalização que melhora sem enganar:** MAE 6,96 → 6,65 e pinball 2,254 → 2,18,
   **sem** estreitar o intervalo — garantia verificada formalmente.
4. **Decisões com risco explícito:** janela de plantio reportada com *downside*; custo com
   *break-even*; nenhuma prescrição sem evidência.
