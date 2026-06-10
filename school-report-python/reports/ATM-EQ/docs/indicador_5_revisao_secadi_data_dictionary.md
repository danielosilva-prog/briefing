# Dicionario de Dados - `Indicador_5_Revisao_Secadi.sql`

Arquivo fonte: `school-report-python/reports/ATM-EQ/queries/Indicador_5_Revisao_Secadi.sql`

## Objetivo da query

Calcular, por municipio, etapa (`EI`, `AI`) e recorte de raca/cor (incluindo categoria `Quilombola`), o percentual de alunos da rede municipal (Censo 2024) cuja turma possui **todas** as docencias avaliadas como adequadas em `Grupo 1` ou `Grupo 2` (AFD/INEP, regra SECADI).

## Fontes fisicas (BigQuery)

- `ts_censo_basico_docente`
- `ts_censo_basico_turma`
- `ts_censo_basico_matricula`

Todos os demais nomes (`BASE_DOCENTE`, `AGG`, etc.) sao CTEs temporarias desta query.

## Visao de lineage (resumo)

1. `BASE_DOCENTE` -> prepara docencias e formacao.
2. `BASE_DISCIPLINA` -> transforma flags de disciplina em linhas.
3. `MAP_G1` e `MAP_G2` -> tabelas inline de codigos de formacao por disciplina.
4. `DOCENCIA_ADEQUADA` -> classifica cada docencia (`DOCENCIA_G12_OK`).
5. `TURMA_ALL_G12` -> turma e valida se todas docencias sao G1/G2.
6. `BASE_MATRICULA` -> base de alunos EI/AI com raca/cor e quilombola.
7. `ALUNO_STATUS` -> liga aluno ao status da turma.
8. `AGG` -> agrega contadores por municipio/etapa/raca.
9. `SELECT final` -> calcula percentuais e retorna painel completo.

## Dicionario por CTE

## 1) `BASE_DOCENTE`

Granularidade: 1 linha por `docente x turma x ano` (com disciplinas ainda em colunas flag).

Fontes:
- `ts_censo_basico_docente d`
- `ts_censo_basico_turma t` (join por `ID_TURMA` + `NU_ANO_CENSO`)

Filtros:
- `d.TP_TIPO_ATENDIMENTO_TURMA IN (1,2)`
- `d.TP_TIPO_DOCENTE IN (1,5)`
- `d.NU_ANO_CENSO = 2024`
- `d.TP_DEPENDENCIA = 3` (rede municipal)

Campos:
- `CO_PESSOA_FISICA` (origem: `d.CO_PESSOA_FISICA`)
- `NU_ANO_CENSO` (origem: `d.NU_ANO_CENSO`)
- `ID_TURMA` (origem: `d.ID_TURMA`)
- `TP_ETAPA_ENSINO` (origem: `t.TP_ETAPA_ENSINO`)
- `ETAPA` (derivado):
  - `EI`: `TP_ETAPA_ENSINO IN (1,2,3)`
  - `AI`: `IN (4,5,6,7,14,15,16,17,18,56)`
  - `AF`: `IN (8,9,10,11,12,13,19,20,21,22,23,24,41)`
  - `EM`: `IN (25..38)`
  - `EJAEF`: `IN (65,69,70,72,73)`
  - `EJAEM`: `IN (67,71,74)`
  - senao `NULL`
- `FORMACAO` (derivado): string com delimitadores `|...|` contendo:
  - `CO_CURSO_1/2/3`
  - `CO_AREA_COMPL_PEDAGOGICA_1/2/3` com left-pad para 8 digitos
  - objetivo: permitir match exato por `LIKE '%|COD|%'`
- `TP_ESCOLARIDADE` (origem: `d.TP_ESCOLARIDADE`)
- `SEM_COMP_PED` (derivado):
  - `1` se `CO_AREA_COMPL_PEDAGOGICA_1/2/3` sao `0` (ou `NULL`)
  - senao `0`
- Flags de disciplina (origem direta de `d`):
  - `IN_DISC_LINGUA_PORTUGUESA`
  - `IN_DISC_PORT_SEGUNDA_LINGUA`
  - `IN_DISC_ARTES`
  - `IN_DISC_EDUCACAO_FISICA`
  - `IN_DISC_MATEMATICA`
  - `IN_DISC_CIENCIAS`
  - `IN_DISC_QUIMICA`
  - `IN_DISC_FISICA`
  - `IN_DISC_BIOLOGIA`
  - `IN_DISC_ESTUDOS_SOCIAIS`
  - `IN_DISC_HISTORIA`
  - `IN_DISC_GEOGRAFIA`
  - `IN_DISC_SOCIOLOGIA`
  - `IN_DISC_FILOSOFIA`
  - `IN_DISC_ENSINO_RELIGIOSO`
  - `IN_DISC_LINGUA_INGLES`
  - `IN_DISC_LINGUA_ESPANHOL`
  - `IN_DISC_LINGUA_FRANCES`
  - `IN_DISC_LINGUA_OUTRA`

## 2) `BASE_DISCIPLINA`

Granularidade: 1 linha por `docente x turma x disciplina`.

Origem: `BASE_DOCENTE`.

Logica:
- Serie de `UNION ALL` convertendo cada flag `IN_DISC_* = 1` em valor textual de `DISCIPLINA`.
- Regra extra: para `ETAPA='EI'`, adiciona linha com `DISCIPLINA='Educacao Infantil'`.
- Portugues considera tambem `IN_DISC_PORT_SEGUNDA_LINGUA`.

Campos:
- `CO_PESSOA_FISICA`
- `NU_ANO_CENSO`
- `ID_TURMA`
- `ETAPA`
- `FORMACAO`
- `TP_ESCOLARIDADE`
- `SEM_COMP_PED`
- `DISCIPLINA` (derivado textual)

## 3) `MAP_G1`

Granularidade: 1 linha por `DISCIPLINA x COD`.

Origem: tabela inline `VALUES`.

Campos:
- `DISCIPLINA`
- `COD`

Semantica:
- Lista codigos de formacao aceitos em Grupo 1 (licenciatura na area e/ou complementacao na area, incluindo regras especificas).

## 4) `MAP_G2`

Granularidade: 1 linha por `DISCIPLINA x COD`.

Origem: tabela inline `VALUES`.

Campos:
- `DISCIPLINA`
- `COD`

Semantica:
- Lista codigos de formacao aceitos em Grupo 2 (bacharelado na area, sujeito a `SEM_COMP_PED=1` na classificacao).

## 5) `DOCENCIA_ADEQUADA`

Granularidade: 1 linha por `docencia` (herdada de `BASE_DISCIPLINA`, filtrada para `EI/AI`).

Origem: `BASE_DISCIPLINA d`.

Filtro:
- `d.ETAPA IN ('EI','AI')`

Campos:
- Todos os campos de `d`
- `DOCENCIA_G12_OK` (derivado, inteiro 0/1):
  - `1` se existe match em `MAP_G1` (`DISCIPLINA` e `FORMACAO LIKE '%|COD|%'`)
  - `1` regra especial AI/EI (exceto linguas estrangeiras):
    - `FORMACAO` contem `0113P011` (Pedagogia lic) **ou** `00000025` (comp pedagogica)
  - `1` se `SEM_COMP_PED=1` e existe match em `MAP_G2`
  - `1` regra especial AI/EI G2 (exceto linguas estrangeiras):
    - `SEM_COMP_PED=1` e `FORMACAO` contem `0113P012` ou `0111C012`
  - senao `0`

## 6) `TURMA_ALL_G12`

Granularidade: 1 linha por `turma x etapa x ano`.

Origem: `DOCENCIA_ADEQUADA`.

Campos:
- `NU_ANO_CENSO`
- `ID_TURMA`
- `ETAPA`
- `N_DOCENCIAS_AVALIADAS` = `COUNT(*)`
- `TURMA_ALL_G12` = `MIN(DOCENCIA_G12_OK)`
  - Interpretacao: so vale `1` se **todas** as docencias da turma forem adequadas.

## 7) `BASE_MATRICULA`

Granularidade: 1 linha por `matricula` (EI/AI, rede municipal, 2024).

Fontes:
- `ts_censo_basico_matricula m`
- `ts_censo_basico_turma t` (join por `ID_TURMA` + `NU_ANO_CENSO`)

Filtros:
- `m.NU_ANO_CENSO = 2024`
- `m.TP_DEPENDENCIA = 3` (rede municipal)
- `t.TP_ETAPA_ENSINO IN (1,2,3,4,5,6,7,14,15,16,17,18,56)` (EI+AI)

Campos:
- `NU_ANO_CENSO` (origem: `m.NU_ANO_CENSO`)
- `CO_MUNICIPIO` (origem: `m.CO_MUNICIPIO`)
- `ID_MATRICULA` (origem: `m.ID_MATRICULA`)
- `ID_TURMA` (origem: `m.ID_TURMA`)
- `ETAPA` (derivado de `t.TP_ETAPA_ENSINO`: `EI` ou `AI`)
- `FL_RESIDE_QUILOMBO`:
  - `1` se `m.TP_LOCAL_RESID_DIFERENCIADA = 3`, senao `0`
- `FL_ESCOLA_EM_QUILOMBO`:
  - `1` se `m.TP_LOCALIZACAO_DIFERENCIADA = 3`, senao `0`
- `RACA_COR` (derivado):
  - `Quilombola` se reside em quilombo **ou** escola localizada em quilombo
  - senao por `TP_COR_RACA`:
    - `0` -> `Nao declarada`
    - `1` -> `Branca`
    - `2` -> `Preta`
    - `3` -> `Parda`
    - `4` -> `Amarela`
    - `5` -> `Indigena`
    - outros -> `Ignorado`

## 8) `ALUNO_STATUS`

Granularidade: 1 linha por `matricula` (com status da turma, quando houver).

Origem:
- `BASE_MATRICULA bm`
- `LEFT JOIN TURMA_ALL_G12 ta` por (`NU_ANO_CENSO`, `ID_TURMA`, `ETAPA`)

Campos:
- `CO_MUNICIPIO`
- `ETAPA`
- `RACA_COR`
- `ID_MATRICULA`
- `TURMA_ALL_G12` (pode ser `NULL` quando nao ha informacao docente para a turma)

## 9) `AGG`

Granularidade: 1 linha por `CO_MUNICIPIO x ETAPA x RACA_COR`.

Origem: `ALUNO_STATUS`.

Campos:
- `CO_MUNICIPIO`
- `ETAPA`
- `RACA_COR`
- `TOTAL_ALUNOS`:
  - `COUNT(DISTINCT ID_MATRICULA)`
- `TOTAL_ALUNOS_COM_INFO`:
  - `COUNT(DISTINCT CASE WHEN TURMA_ALL_G12 IS NOT NULL THEN ID_MATRICULA END)`
- `ALUNOS_ALL_G12`:
  - `COUNT(DISTINCT CASE WHEN TURMA_ALL_G12 = 1 THEN ID_MATRICULA END)`

## 10) `MUNICIPIOS`

Granularidade: 1 linha por municipio.

Origem: `BASE_MATRICULA`.

Campo:
- `CO_MUNICIPIO` (`DISTINCT`)

## 11) `CATEG_ETAPA`

Granularidade: dominio fixo.

Origem: inline `VALUES`.

Campos:
- `ETAPA` (`EI`, `AI`)
- `ORDEM_ETAPA` (1, 2)

## 12) `CATEG_RACA`

Granularidade: dominio fixo.

Origem: inline `VALUES`.

Campos:
- `RACA_COR`:
  - `Nao declarada`, `Branca`, `Preta`, `Parda`, `Amarela`, `Indigena`, `Quilombola`
- `ORDEM_RACA`:
  - 1..7

## Dicionario do resultado final (`SELECT`)

Granularidade final: 1 linha por `CO_MUNICIPIO x ETAPA x RACA_COR`, incluindo combinacoes sem ocorrencia (devido a `CROSS JOIN` de categorias e `LEFT JOIN` com `AGG`).

Campos finais:
- `CO_MUNICIPIO` (de `MUNICIPIOS`)
- `ETAPA` (de `CATEG_ETAPA`)
- `RACA_COR` (de `CATEG_RACA`)
- `TOTAL_ALUNOS` = `COALESCE(a.TOTAL_ALUNOS, 0)`
- `TOTAL_ALUNOS_COM_INFO` = `COALESCE(a.TOTAL_ALUNOS_COM_INFO, 0)`
- `ALUNOS_COM_TURMA_ALL_G12` = `COALESCE(a.ALUNOS_ALL_G12, 0)`
- `PERC_ALL_G12_VALIDOS`:
  - `ROUND(100.0 * ALUNOS_ALL_G12 / NULLIF(TOTAL_ALUNOS_COM_INFO, 0), 2)`
  - interpreta apenas turmas com info docente
- `PERC_ALL_G12_TOTAL`:
  - `ROUND(100.0 * ALUNOS_ALL_G12 / NULLIF(TOTAL_ALUNOS, 0), 2)`
  - interpreta turmas sem info como nao adequadas no denominador total

## Regras de negocio-chave

- Escopo temporal fixo: ano censitario `2024`.
- Escopo administrativo: somente `TP_DEPENDENCIA = 3` (rede municipal).
- Escopo pedagogico do indicador: apenas etapas `EI` e `AI`.
- Docencia adequada depende de mapeamentos `MAP_G1`/`MAP_G2` e regras especiais para EI/AI.
- Turma adequada exige condicao "all": `MIN(DOCENCIA_G12_OK)=1`.
- Categoria `Quilombola` sobrescreve classificacao de raca/cor quando residencia ou escola e quilombo.
- Resultado final devolve grade completa de etapa x raca por municipio, mesmo com zero casos.

## Observacoes tecnicas

- A query usa sintaxe de concatenacao `+` e `VALUES ... v(col1,col2)` tipica de T-SQL.
- Para BigQuery Standard SQL, isso normalmente exigiria ajustes (`CONCAT`, `UNNEST`/`STRUCT` etc.), caso executada diretamente sem camada de compatibilidade.
