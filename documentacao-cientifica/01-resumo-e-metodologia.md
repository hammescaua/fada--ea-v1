# 01 — Resumo e Metodologia de Desenvolvimento

## Resumo

O **FADA (Farm AI Decision Agent)** é um sistema de apoio à decisão agrícola para a
cultura da soja, desenvolvido inicialmente para a microrregião de Três Passos (Noroeste
do Rio Grande do Sul). O sistema integra **dados públicos** (produtividade municipal
histórica do IBGE e séries climáticas de reanálise da NASA POWER e do Open-Meteo) com
**dados da propriedade** informados pelo produtor, transformando-os em respostas
acionáveis: estimativa de produtividade com incerteza, janela ótima de plantio, análise
de custo e margem, priorização de talhões e personalização progressiva por fazenda.

A premissa metodológica central é o **determinismo auditável**: todo valor numérico é
produzido por serviços de domínio determinísticos e testáveis; um modelo de linguagem
(LLM) é empregado apenas para roteamento de intenções e explicação em linguagem natural,
**nunca para gerar números**. A incerteza é tratada como cidadã de primeira classe: toda
predição é acompanhada de intervalo e cenários, e a **calibração** desses intervalos é
medida empiricamente.

## Paradigma de desenvolvimento

O desenvolvimento seguiu um processo **iterativo e incremental**, organizado em fatias
verticais funcionais (do dado à interface), com as seguintes características
metodológicas distintivas:

### 1. Crítica antes da implementação (*critique-then-implement*)

Cada etapa foi precedida de uma **análise crítica explícita** que: (i) questionava as
premissas da funcionalidade proposta; (ii) identificava riscos científicos e
arquiteturais; (iii) classificava cada ideia em **implementar agora / adiar / descartar**;
e (iv) justificava cada descarte. Esse procedimento evitou a incorporação de complexidade
prematura e de métodos cientificamente frágeis (ver Discussão).

### 2. Verificação por testes automatizados (*test-backed*)

Cada mudança de comportamento foi acompanhada de **testes automatizados** (suíte final:
**164 testes**, executados por `pytest`). A suíte inclui testes unitários de domínio,
testes de integração de endpoints e **testes baseados em propriedades**
(*property-based testing*), nos quais uma propriedade matemática é verificada sobre
milhares de entradas aleatórias (p. ex., a garantia de que a personalização nunca reduz a
largura do intervalo foi verificada sobre 25.000 entradas aleatórias).

### 3. Reprodutibilidade

O pipeline de dados e treino é determinístico e versionado: parâmetros em `params.yaml`,
grafo de execução em `dvc.yaml`, e rastreamento de experimentos em **MLflow**. O modelo
treinado, o conjunto de *features* e o relatório de calibração são versionados no
repositório, de modo que o sistema funciona imediatamente após a instalação e que os
resultados aqui relatados podem ser reproduzidos.

### 4. Validação temporal (nunca aleatória)

A avaliação preditiva utilizou exclusivamente **validação temporal** do tipo
*leave-one-year-out* (deixe-um-ano-de-fora), em que cada ano é predito por um modelo
treinado nos demais anos. Validação cruzada aleatória foi deliberadamente evitada, por
introduzir vazamento de informação do futuro para o passado em séries temporais.

### 5. Controle de versão disciplinado

O histórico foi mantido em **32 commits** descritivos, com separação consistente entre
mudanças de *backend* e de *frontend*, cada commit verificado (testes + *lint* +
*build*) antes do registro.

## Arquitetura de software (síntese)

O sistema foi implementado como um **monólito modular** segundo princípios de
*Domain-Driven Design* (DDD), com **15 contextos de domínio** isolados e puros (sem
dependência de banco de dados ou rede), organizados em camadas (API → Serviços →
Domínio → Infraestrutura). Essa decisão (registrada no ADR-0001) privilegiou velocidade
de iteração e auditabilidade sobre a complexidade distribuída de microsserviços,
mantendo, contudo, fronteiras limpas que permitiriam extração futura em serviços.

## Linha do tempo

O desenvolvimento ocorreu entre **16 e 22 de junho de 2026**, evoluindo de um repositório
vazio até um produto funcional de ponta a ponta (backend + frontend), conforme detalhado
na [Cronologia do Desenvolvimento](03-cronologia-do-desenvolvimento.md).
