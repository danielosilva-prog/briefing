# Mapeamento de Indicadores - P06 Diagnostico de Equidade

Arquivo da pagina:
- `school-report-python/reports/ATM-EQ/template/pages/P06-DiagnosticoEquidade.typ`

Query atual da pagina:
- `school-report-python/reports/ATM-EQ/queries/p6_diagnostico_equidade.sql`

Tabelas de apoio carregadas no BigQuery sandbox:
- `br-mec-segape-sandbox.projeto_segape_dmape_relat_automatico.atm_eq_pneerq_diagnostico_equidade_municipio`
- `br-mec-segape-sandbox.projeto_segape_dmape_relat_automatico.atm_eq_pneerq_diagnostico_equidade_uf`
- `br-mec-segape-sandbox.projeto_segape_dmape_relat_automatico.atm_eq_pneerq_dicionario_variavel`

Planilha de origem:
- `school-report-python/reports/ATM-EQ/docs/Diagnostico_Equidade_ATM.xlsx`

## Objetivo

Documentar a origem e a semantica dos indicadores consumidos pela P06, usando como referencia a planilha do Diagnostico de Equidade (PNEERQ - 2024).

## Fontes logicas na planilha

### 1. `Respostas - Redes Municipais`

Granularidade:
- 1 linha por municipio

Uso na P06:
- base principal para o municipio selecionado
- respostas do questionario (`P*`)
- indices prontos (`I_*`)

Campos relevantes:
- `CO_MUNICIPIO`
- `CO_UF`
- `P2A`
- `P18A ... P18K`
- `P20A`
- `P29B`
- `I_Erer_Geral`
- `I_Erer_Institucionalizacao`
- `I_Erer_Formacao`
- `I_Erer_Gestao_Escolar`
- `I_Erer_Material_Didatico_Paradidatico`
- `I_Erer_Financiamento`
- `I_Erer_Avaliacao_Monitoramento`
- `I_Geral_EEQ`
- `I_Geral_EEI`

### 2. `Respostas - Redes Estaduais`

Granularidade:
- 1 linha por UF / rede estadual

Uso na P06:
- comparacao de referencia da rede estadual da UF

Campos relevantes:
- `CO_UF`
- `I_Erer_Geral`
- demais `I_*` para refinamentos futuros

### 3. `Dicionario de Variáveis`

Granularidade:
- 1 linha por variavel/item/resposta

Uso na P06:
- interpretar os codigos das respostas
- validar a semantica dos campos exibidos na pagina

Campos relevantes:
- `CO_PERGUNTA`
- `TEXT_PERGUNTA`
- `ITEM`
- `CO_RESPOSTA`
- `TEXT_RESPOSTA`
- `Índice`

## Tabelas no sandbox

### `atm_eq_pneerq_diagnostico_equidade_municipio`

Granularidade:
- 1 linha por municipio

Origem:
- aba `Respostas - Redes Municipais`

Normalizacoes aplicadas:
- nomes em `snake_case`
- `999` -> `NULL`
- `Nao respondeu ao questionario` -> `NULL` nos indices
- flags `0/1` convertidas para `BOOL`
- colunas `p*_x` mantidas como `STRING`
- colunas `i_*` carregadas como `BIGNUMERIC`

### `atm_eq_pneerq_diagnostico_equidade_uf`

Granularidade:
- 1 linha por UF / rede estadual

Origem:
- aba `Respostas - Redes Estaduais`

Normalizacoes:
- mesmas da tabela municipal

### `atm_eq_pneerq_dicionario_variavel`

Granularidade:
- 1 linha por variavel / item / resposta

Origem:
- aba `Dicionario de Variáveis`

Uso:
- dicionario semantico para traducao das respostas codificadas

## Indicadores hoje usados pela P06

### 1. `mediaIndiceGeralERERMunicipal`

Exibicao na pagina:
- card principal "Media do Indice geral - ERER Rede Municipal"

Origem:
- `Respostas - Redes Municipais`
- coluna `I_Erer_Geral`
- tabela final `atm_eq_pneerq_diagnostico_equidade_municipio.i_erer_geral`

Regra atual:
- usa o valor do municipio selecionado
- formatacao com 1 casa decimal e virgula

Observacao:
- apesar do nome `mediaIndiceGeralERERMunicipal`, o valor mostrado nao e uma media; e o indice do municipio

### 2. `minimoIndiceGeralERERMunicipal`

Origem:
- conjunto de municipios da mesma UF
- tabela `atm_eq_pneerq_diagnostico_equidade_municipio`

Regra atual:
- `MIN(i_erer_geral)` dos municipios da UF do municipio selecionado

### 3. `maximoIndiceGeralERERMunicipal`

Origem:
- conjunto de municipios da mesma UF

Regra atual:
- `MAX(i_erer_geral)` dos municipios da UF

### 4. `medianaIndiceGeralERERMunicipal`

Origem:
- conjunto de municipios da mesma UF

Regra atual:
- mediana aproximada via `APPROX_QUANTILES(i_erer_geral, 2)[OFFSET(1)]`

### 5. `mediaIndiceGeralERERUF`

Exibicao na pagina:
- texto abaixo da barra gradiente do bloco "segundo UF e Rede de Ensino"

Origem atual:
- `Respostas - Redes Estaduais`
- coluna `I_Erer_Geral`
- tabela `atm_eq_pneerq_diagnostico_equidade_uf.i_erer_geral`

Fallback atual:
- se nao houver linha estadual da UF, usa a media dos municipios da UF

Ponto de atencao:
- o rotulo da pagina sugere "segundo UF e Rede de Ensino", mas hoje a implementacao usa apenas o indice da rede estadual da UF

### 6. `minimoIndiceGeralERERUF`

Origem atual:
- municipios da mesma UF

Regra atual:
- `MIN(i_erer_geral)` da distribuicao municipal da UF

### 7. `maximoIndiceGeralERERUF`

Origem atual:
- municipios da mesma UF

Regra atual:
- `MAX(i_erer_geral)` da distribuicao municipal da UF

### 8. `percentualIndiceGeralERERUF`

Exibicao na pagina:
- posicao do marcador sobre a barra gradiente

Origem atual:
- calculado na query

Regra atual:
- escala de 0 a 100 usando:
  - minimo da distribuicao municipal da UF
  - maximo da distribuicao municipal da UF
  - valor da rede estadual da UF, ou media municipal da UF como fallback

Formula:
- `100 * (valor_referencia - minimo) / (maximo - minimo)`
- limitado ao intervalo `[0, 100]`

Ponto de atencao:
- este percentual nao vem da planilha; e um derivado visual para posicionar o marcador

## KPIs textuais

### 9. `formacoesERER`

Exibicao na pagina:
- primeiro KPI textual

Origem:
- `P2A`
- pergunta:
  - "Desde a sancao da Lei no 10.639/2003, quantos cursos ... foram ofertados pela Secretaria de Educacao?"

Dicionario:
- `0` = `Nenhum`
- `1` = `1 a 5 cursos`
- `2` = `6 a 10 cursos`
- `3` = `Mais de 10 cursos`

Regra atual:
- a query converte `P2A` para:
  - `Nenhum`
  - `1 a 5`
  - `6 a 10`
  - `Mais de 10`
  - `Nao respondeu`

### 10. `revisaoCurriculo`

Origem:
- `P20A`
- pergunta:
  - "A Secretaria de Educacao realizou revisao curricular em cumprimento a Lei no 10.639/2003 e a Lei no 11.645/2008?"

Dicionario:
- `0` = `Nao`
- `1` = `Sim`

Regra atual:
- `1` -> `Realizou`
- `0` -> `Nao realizou`
- demais -> `Nao respondeu`

### 11. `aquisicaoMateriais`

Origem:
- bloco `P18A ... P18K`
- pergunta base:
  - "A Secretaria de Educacao faz aquisicao de materiais didatico-pedagogicos ..."

Semantica do dicionario:
- cada item representa uma etapa/modalidade
- `0` = `Nao`
- `1` = `Sim` para aquela etapa/modalidade

Regra atual:
- se existir ao menos um item `1`, retorna `Realiza`
- senao, se existir ao menos um item `0`, retorna `Nao realiza`
- senao, `Nao respondeu`

Ponto de atencao:
- hoje o indicador resume um bloco multi-item em resposta binaria agregada
- pode ser refinado no futuro para mostrar etapas/modalidades atendidas

### 12. `adocaoCriterioPriorizacao`

Origem:
- `P29B`
- pergunta:
  - "Se ha cadastro de demandas por vaga de creche ..., a Secretaria considera criterios socioeconomicos para priorizar as criancas a serem atendidas?"

Dicionario:
- `0` = `Nao ha cadastro`
- `1` = `Nao`
- `2` = `Sim`

Regra atual:
- `2` -> `Adota`
- `1` -> `Nao adota`
- `0` -> `Nao ha cadastro`
- demais -> `Nao respondeu`

## Elementos ainda estaticos na P06

Hoje a pagina ainda usa SVGs fixos:
- `P6-G1.svg`
- `P6-G2.svg`
- `P6-G3.svg`

Esses elementos ainda nao foram substituidos por consultas dinamicas.

## Pendencias de refinamento

### 1. Nome dos campos do bloco superior

Os nomes `mediaIndiceGeralERERMunicipal` e `mediaIndiceGeralERERUF` nao refletem perfeitamente o que esta sendo mostrado:
- o primeiro e o indice do municipio, nao uma media
- o segundo e o indice da rede estadual da UF, nao necessariamente uma media

### 2. Semantica do bloco "segundo UF e Rede de Ensino"

Ainda precisa decisao funcional:
- comparar municipio vs distribuicao dos municipios da UF?
- comparar municipio vs rede estadual da UF?
- comparar municipio, rede estadual e Brasil ao mesmo tempo?

### 3. Mosaico de 7 indices ERER

A planilha tem informacao suficiente para substituir o SVG:
- `I_Erer_Institucionalizacao`
- `I_Erer_Formacao`
- `I_Erer_Gestao_Escolar`
- `I_Erer_Material_Didatico_Paradidatico`
- `I_Erer_Financiamento`
- `I_Erer_Avaliacao_Monitoramento`
- `I_Erer_Geral`

### 4. Mosaico de indices EEQ comparando com UF e BR

A planilha tem base para este grafico, mas ainda falta fechar:
- quais indices entram
- se a comparacao com Brasil vira media dos municipios, media das UFs, ou outro agregado

## Resumo operacional

O que ja esta implementado:
- carga da planilha para 3 tabelas no sandbox
- query da P06 com campos numericos principais
- KPIs textuais traduzidos pelo dicionario

O que ainda depende de decisao:
- semantica exata dos comparativos da UF
- substituicao dos graficos estaticos por visuais dinamicos
