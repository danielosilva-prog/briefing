# Verificação de Queries BigQuery vs PDF — ATS-02

**Data da verificação:** 2026-03-10
**Exemplo utilizado:** UFPE — Universidade Federal de Pernambuco (`id_uo = 26242`)
**Projeto BigQuery:** `br-mec-segape`
**Dataset:** `educacao_politica_tesouro`
**Referência PDF:** `ATS Orçamento - Integração.pdf`

---

## Seção 1 — Tabelas BigQuery utilizadas

| Tabela | Alias usado nas queries | Função |
|--------|------------------------|--------|
| `tesouro_orcamento_unidade_orcamentaria` | `t_uo` | Despesa empenhada por Unidade Orçamentária (P01 — Orçamento Originário) |
| `tesouro_orcamento_destaque_recebido_instituicao` | `t_dest` | Crédito recebido e despesa empenhada por destaque (P02–P07) |
| `tesouro_orcamento_universidade_federal_grupo` | `t_grupo` | Classificação (`grupo_unidade_orcamentaria`) e nome (`unidade_orcamentaria`) da UO — usada em JOIN em todas as queries |

**Filtro universal:** `t_grupo.grupo_unidade_orcamentaria = 'Universidade'`
O JOIN com `t_grupo` garante que apenas registros de universidades federais sejam considerados.

---

## Seção 2 — Mapeamento Query → Gráfico no PDF

### P01 — Orçamento Originário (parâmetro: `@id_unidade_orcamentaria INT64`)

| Arquivo SQL | Parâmetro | Página/Gráfico | Colunas retornadas |
|-------------|-----------|----------------|--------------------|
| `visao_geral_periodo1.sql` | `id_unidade_orcamentaria` | P01 / G1 | `ano`, `despesa_empenhada` |
| `visao_geral_periodo2.sql` | `id_unidade_orcamentaria` | P01 / G2 | `ano`, `despesa_empenhada` |
| `resultado_lei_periodo1.sql` | `id_unidade_orcamentaria` | P01 / G3 | `ano`, `obrigatorio`, `discricionario`, `emendas` |
| `resultado_lei_periodo2.sql` | `id_unidade_orcamentaria` | P01 / G4 | `ano`, `obrigatorio`, `discricionario`, `emendas` |
| `grupo_despesa_periodo1.sql` | `id_unidade_orcamentaria` | P01 / G5 | `ano`, `pessoal_encargos`, `custeio`, `capital` |
| `grupo_despesa_periodo2.sql` | `id_unidade_orcamentaria` | P01 / G6 | `ano`, `pessoal_encargos`, `custeio`, `capital` |
| `metricas_orcamento.sql` | `id_unidade_orcamentaria` | P01 / KPIs | `ano`, `despesa_empenhada` (anos 2019–2021 e 2023–2025) |

### P02–P07 — Crédito Recebido por Destaque (parâmetro: `@id_uo_list ARRAY<STRING>`)

| Arquivo SQL | Parâmetro | Páginas/Gráficos | Colunas retornadas |
|-------------|-----------|------------------|--------------------|
| `credito_recebido_geral_p1.sql` | `id_uo_list` | P02–P07 / G1 | `ano`, `destaque_recebido`, `despesa_empenhada` |
| `credito_recebido_geral_p2.sql` | `id_uo_list` | P02–P07 / G2 | `ano`, `destaque_recebido`, `despesa_empenhada` |
| `credito_resultado_lei_p1.sql` | `id_uo_list` | P02–P07 / G3 | `ano`, `obrigatorio`, `discricionario`, `emendas` |
| `credito_resultado_lei_p2.sql` | `id_uo_list` | P02–P07 / G4 | `ano`, `obrigatorio`, `discricionario`, `emendas` |
| `credito_grupo_despesa_p1.sql` | `id_uo_list` | P02–P07 / G5 | `ano`, `pessoal_encargos`, `custeio`, `capital` |
| `credito_grupo_despesa_p2.sql` | `id_uo_list` | P02–P07 / G6 | `ano`, `pessoal_encargos`, `custeio`, `capital` |
| `metricas_credito_recebido.sql` | `id_uo_list` | P02–P07 / KPIs | `ano`, `despesa_empenhada` (anos 2019–2021 e 2023–2025) |
| `capes_auxilios_financeiros.sql` | *(sem parâmetro)* | P05 / G-AUX | `ano`, `auxilio_estudante`, `auxilio_pesquisador` |

### Lookup

| Arquivo SQL | Parâmetro | Uso |
|-------------|-----------|-----|
| `universidade_by_sigla.sql` | `id_unidade_orcamentaria` | Resolve nome da universidade a partir do `id_uo` |

### Filtros por página (executor.py `_UO_BY_PAGE`)

| Página | UO(s) | Órgão |
|--------|-------|-------|
| P02 (Geral) | `26101`, `26290`, `26291`, `26298`, `26443` | MEC + INEP + CAPES + FNDE + EBSERH |
| P03 | `26101` | MEC |
| P04 | `26290` | INEP |
| P05 | `26291` | CAPES |
| P06 | `26298` | FNDE |
| P07 | `26443` | EBSERH |

---

## Seção 3 — Observação sobre escopo: P01 vs PDF

O PDF `ATS Orçamento - Integração.pdf` mostra **agregados nacionais** (todas as universidades combinadas), não valores por instituição:

| Página Python | Seção no PDF | Escopo dos dados |
|---|---|---|
| **P01** | Seção 2 (Despesa Empenhada — Orçamento Originário) | **Nacional (todas as universidades)** no PDF, mas o Python usa `id_uo` por instituição |
| **P02** | Seção 3 (Crédito Recebido Geral) | Nacional: UOs `26101+26290+26291+26298+26443` → todas as universidades ✅ |
| **P03** | Seção 4 (MEC – UO 26101) | UO 26101 → todas as universidades ✅ |
| **P04** | Seção 5 (INEP – UO 26290) | UO 26290 → todas as universidades ✅ |
| **P05** | Seção 6 (CAPES – UO 26291) | UO 26291 → todas as universidades ✅ |
| **P06** | Seção 7 (FNDE – UO 26298) | UO 26298 → todas as universidades ✅ |
| **P07** | Seção 8 (EBSERH – UO 26443) | UO 26443 → todas as universidades ✅ |

**Consequência:** P01 não pode ser comparado diretamente com o PDF (escopos diferentes — o PDF mostra o nacional, o Python gera por instituição). P02–P07 podem e devem ser verificados linha a linha, pois ambos agregam todas as universidades filtradas pela UO correspondente.

---

## Seção 4 — Comparação PDF vs BigQuery (P02–P07) ✅

Todos os valores foram verificados e estão **consistentes com o PDF de referência**.

### Resumo executivo

| Página | UO | Métrica | Esperado (PDF) | Obtido (BQ) | Status |
|--------|----|---------|---------------|-------------|--------|
| P02 | 5 UOs | Acumulado P1 | R$ 3,58 Bi | R$ 3.579.540.120 ≈ R$ 3,58 Bi | ✅ |
| P02 | 5 UOs | Acumulado P2 | R$ 5,34 Bi | R$ 5.335.627.234 ≈ R$ 5,34 Bi | ✅ |
| P02 | 5 UOs | Variação P1 | -16,31% | -16,31% | ✅ |
| P02 | 5 UOs | Variação P2 | +19,98% | +19,98% | ✅ |
| P02 | 5 UOs | Incremento | R$ 1,76 Bi | R$ 1.756.087.114 ≈ R$ 1,76 Bi | ✅ |
| P02 | 5 UOs | % Incremento | 49,06% | 49,06% | ✅ |
| P03 | 26101 | Acumulado P1 | R$ 2,90 Bi | R$ 2.899.168.797 ≈ R$ 2,90 Bi | ✅ |
| P03 | 26101 | Acumulado P2 | R$ 4,23 Bi | R$ 4.228.991.321 ≈ R$ 4,23 Bi | ✅ |
| P03 | 26101 | Variação P1 | -23,49% | -23,49% | ✅ |
| P03 | 26101 | Variação P2 | +39,27% | +39,27% | ✅ |
| P03 | 26101 | Incremento | R$ 1,33 Bi | R$ 1.329.822.524 ≈ R$ 1,33 Bi | ✅ |
| P03 | 26101 | % Incremento | 45,87% | 45,87% | ✅ |
| P04 | 26290 | Acumulado P1 | R$ 3,31 Mi | R$ 3.314.745 ≈ R$ 3,31 Mi | ✅ |
| P04 | 26290 | Acumulado P2 | R$ 19,67 Mi | R$ 19.668.381 ≈ R$ 19,67 Mi | ✅ |
| P04 | 26290 | Variação P1 | -29,42% | -29,42% | ✅ |
| P04 | 26290 | Variação P2 | +51,33% | +51,33% | ✅ |
| P04 | 26290 | Incremento | R$ 16,35 Mi | R$ 16.353.636 ≈ R$ 16,35 Mi | ✅ |
| P04 | 26290 | % Incremento | 493,36% | 493,36% | ✅ |
| P05 | 26291 | Acumulado P1 | R$ 263,05 Mi | R$ 263.048.683 ≈ R$ 263,05 Mi | ✅ |
| P05 | 26291 | Acumulado P2 | R$ 392,80 Mi | R$ 392.804.104 ≈ R$ 392,80 Mi | ✅ |
| P05 | 26291 | Variação P1 | -10,84% | -10,84% | ✅ |
| P05 | 26291 | Variação P2 | +13,59% | +13,59% | ✅ |
| P05 | 26291 | Incremento | R$ 129,76 Mi | R$ 129.755.421 ≈ R$ 129,76 Mi | ✅ |
| P05 | 26291 | % Incremento | 49,33% | 49,32% | ✅ |
| P06 | 26298 | Acumulado P1 | R$ 302,26 Mi | R$ 302.264.594 ≈ R$ 302,26 Mi | ✅ |
| P06 | 26298 | Acumulado P2 | R$ 621,95 Mi | R$ 621.953.790 ≈ R$ 621,95 Mi | ✅ |
| P06 | 26298 | Variação P1 | +538,85% | +538,85% | ✅ |
| P06 | 26298 | Variação P2 | -60,17% | -60,17% | ✅ |
| P06 | 26298 | Incremento | R$ 319,69 Mi | R$ 319.689.196 ≈ R$ 319,69 Mi | ✅ |
| P06 | 26298 | % Incremento | 105,76% | 105,76% | ✅ |
| P07 | 26443 | Acumulado P1 | R$ 111,74 Mi | R$ 111.743.301 ≈ R$ 111,74 Mi | ✅ |
| P07 | 26443 | Acumulado P2 | R$ 72,21 Mi | R$ 72.209.639 ≈ R$ 72,21 Mi | ✅ |
| P07 | 26443 | Variação P1 | -99,51% | -99,51% | ✅ |
| P07 | 26443 | Variação P2 | -99,78% | -99,78% | ✅ |
| P07 | 26443 | Incremento | -R$ 39,53 Mi | -R$ 39.533.662 ≈ -R$ 39,53 Mi | ✅ |
| P07 | 26443 | % Incremento | -35,38% | -35,38% | ✅ |

### Detalhamento por página

#### P03 — MEC (UO 26101)

| Ano | Despesa Empenhada (R$) |
|-----|------------------------|
| 2019 | 1.068.103.988,48 |
| 2020 | 1.013.882.339,38 |
| 2021 | 817.182.469,33 |
| 2023 | 1.251.421.566,13 |
| 2024 | 1.234.679.641,26 |
| 2025 | 1.742.890.113,34 |

```
Acumulado P1 = 1.068.103.988,48 + 1.013.882.339,38 + 817.182.469,33 = R$ 2.899.168.797,19
Acumulado P2 = 1.251.421.566,13 + 1.234.679.641,26 + 1.742.890.113,34 = R$ 4.228.991.320,73

% Variação P1 = (817.182.469,33 - 1.068.103.988,48) / 1.068.103.988,48 × 100 = -23,49%
% Variação P2 = (1.742.890.113,34 - 1.251.421.566,13) / 1.251.421.566,13 × 100 = +39,27%

Incremento = 4.228.991.320,73 - 2.899.168.797,19 = R$ 1.329.822.523,54
% Incremento = 1.329.822.523,54 / 2.899.168.797,19 × 100 = 45,87%
```

#### P04 — INEP (UO 26290)

| Ano | Despesa Empenhada (R$) |
|-----|------------------------|
| 2019 | 459.272,72 |
| 2020 | 2.531.308,75 |
| 2021 | 324.163,93 |
| 2023 | 6.095.166,36 |
| 2024 | 4.349.275,78 |
| 2025 | 9.223.939,00 |

```
Acumulado P1 = 459.272,72 + 2.531.308,75 + 324.163,93 = R$ 3.314.745,40
Acumulado P2 = 6.095.166,36 + 4.349.275,78 + 9.223.939,00 = R$ 19.668.381,14

% Variação P1 = (324.163,93 - 459.272,72) / 459.272,72 × 100 = -29,42%
% Variação P2 = (9.223.939,00 - 6.095.166,36) / 6.095.166,36 × 100 = +51,33%

Incremento = 19.668.381,14 - 3.314.745,40 = R$ 16.353.635,74
% Incremento = 16.353.635,74 / 3.314.745,40 × 100 = 493,36%
```

#### P05 — CAPES (UO 26291)

| Ano | Despesa Empenhada (R$) |
|-----|------------------------|
| 2019 | 94.839.587,49 |
| 2020 | 83.654.591,65 |
| 2021 | 84.554.503,80 |
| 2023 | 115.423.606,17 |
| 2024 | 146.266.481,75 |
| 2025 | 131.114.015,62 |

```
Acumulado P1 = 94.839.587,49 + 83.654.591,65 + 84.554.503,80 = R$ 263.048.682,94
Acumulado P2 = 115.423.606,17 + 146.266.481,75 + 131.114.015,62 = R$ 392.804.103,54

% Variação P1 = (84.554.503,80 - 94.839.587,49) / 94.839.587,49 × 100 = -10,84%
% Variação P2 = (131.114.015,62 - 115.423.606,17) / 115.423.606,17 × 100 = +13,59%

Incremento = 392.804.103,54 - 263.048.682,94 = R$ 129.755.420,60
% Incremento = 129.755.420,60 / 263.048.682,94 × 100 = 49,32%
```

#### P06 — FNDE (UO 26298)

| Ano | Despesa Empenhada (R$) |
|-----|------------------------|
| 2019 | 21.379.056,05 |
| 2020 | 144.305.247,89 |
| 2021 | 136.580.289,95 |
| 2023 | 216.582.731,36 |
| 2024 | 319.106.840,34 |
| 2025 | 86.264.217,87 |

```
Acumulado P1 = 21.379.056,05 + 144.305.247,89 + 136.580.289,95 = R$ 302.264.593,89
Acumulado P2 = 216.582.731,36 + 319.106.840,34 + 86.264.217,87 = R$ 621.953.789,57

% Variação P1 = (136.580.289,95 - 21.379.056,05) / 21.379.056,05 × 100 = +538,85%
% Variação P2 = (86.264.217,87 - 216.582.731,36) / 216.582.731,36 × 100 = -60,17%

Incremento = 621.953.789,57 - 302.264.593,89 = R$ 319.689.195,68
% Incremento = 319.689.195,68 / 302.264.593,89 × 100 = 105,76%
```

#### P07 — EBSERH (UO 26443)

| Ano | Despesa Empenhada (R$) |
|-----|------------------------|
| 2019 | 56.573.861,69 |
| 2020 | 54.894.313,51 |
| 2021 | 275.125,81 |
| 2023 | 52.078.513,04 |
| 2024 | 20.018.439,16 |
| 2025 | 112.686,75 |

```
Acumulado P1 = 56.573.861,69 + 54.894.313,51 + 275.125,81 = R$ 111.743.301,01
Acumulado P2 = 52.078.513,04 + 20.018.439,16 + 112.686,75 = R$ 72.209.638,95

% Variação P1 = (275.125,81 - 56.573.861,69) / 56.573.861,69 × 100 = -99,51%
% Variação P2 = (112.686,75 - 52.078.513,04) / 52.078.513,04 × 100 = -99,78%

Incremento = 72.209.638,95 - 111.743.301,01 = -R$ 39.533.662,06
% Incremento = -39.533.662,06 / 111.743.301,01 × 100 = -35,38%
```

---

## Seção 5 — Queries BQ CLI executadas (P03–P07)

### Queries `metricas_credito_recebido.sql` por UO individual

```bash
# P03 — MEC (26101)
bq query --use_legacy_sql=false \
  --parameter='id_uo_list:ARRAY<STRING>:["26101"]' \
'SELECT t_dest.ano, SUM(t_dest.despesa_empenhada) AS despesa_empenhada
FROM `br-mec-segape.educacao_politica_tesouro.tesouro_orcamento_destaque_recebido_instituicao` AS t_dest
JOIN `br-mec-segape.educacao_politica_tesouro.tesouro_orcamento_universidade_federal_grupo` AS t_grupo
  ON t_dest.id_orgao_uge = CAST(t_grupo.id_unidade_orcamentaria AS STRING)
WHERE t_grupo.grupo_unidade_orcamentaria = "Universidade"
  AND t_dest.id_unidade_orcamentaria IN UNNEST(@id_uo_list)
  AND t_dest.ano IN (2019, 2020, 2021, 2023, 2024, 2025)
GROUP BY t_dest.ano ORDER BY t_dest.ano'
```

**Resultado P03 (26101 — MEC):**
```
+------+----------------------+
| ano  |  despesa_empenhada   |
+------+----------------------+
| 2019 | 1.0681039884799993E9 |
| 2020 | 1.0138823393800008E9 |
| 2021 |  8.171824693299991E8 |
| 2023 | 1.2514215661299999E9 |
| 2024 | 1.2346796412600007E9 |
| 2025 | 1.7428901133400002E9 |
+------+----------------------+
```

```bash
# P04 — INEP (26290)
bq query --use_legacy_sql=false \
  --parameter='id_uo_list:ARRAY<STRING>:["26290"]' \
'SELECT t_dest.ano, SUM(t_dest.despesa_empenhada) AS despesa_empenhada
FROM `br-mec-segape.educacao_politica_tesouro.tesouro_orcamento_destaque_recebido_instituicao` AS t_dest
JOIN `br-mec-segape.educacao_politica_tesouro.tesouro_orcamento_universidade_federal_grupo` AS t_grupo
  ON t_dest.id_orgao_uge = CAST(t_grupo.id_unidade_orcamentaria AS STRING)
WHERE t_grupo.grupo_unidade_orcamentaria = "Universidade"
  AND t_dest.id_unidade_orcamentaria IN UNNEST(@id_uo_list)
  AND t_dest.ano IN (2019, 2020, 2021, 2023, 2024, 2025)
GROUP BY t_dest.ano ORDER BY t_dest.ano'
```

**Resultado P04 (26290 — INEP):**
```
+------+-------------------+
| ano  | despesa_empenhada |
+------+-------------------+
| 2019 | 459272.7200000001 |
| 2020 |        2531308.75 |
| 2021 |         324163.93 |
| 2023 | 6095166.359999999 |
| 2024 | 4349275.779999999 |
| 2025 |         9223939.0 |
+------+-------------------+
```

```bash
# P05 — CAPES (26291)
bq query --use_legacy_sql=false \
  --parameter='id_uo_list:ARRAY<STRING>:["26291"]' \
'SELECT t_dest.ano, SUM(t_dest.despesa_empenhada) AS despesa_empenhada
FROM `br-mec-segape.educacao_politica_tesouro.tesouro_orcamento_destaque_recebido_instituicao` AS t_dest
JOIN `br-mec-segape.educacao_politica_tesouro.tesouro_orcamento_universidade_federal_grupo` AS t_grupo
  ON t_dest.id_orgao_uge = CAST(t_grupo.id_unidade_orcamentaria AS STRING)
WHERE t_grupo.grupo_unidade_orcamentaria = "Universidade"
  AND t_dest.id_unidade_orcamentaria IN UNNEST(@id_uo_list)
  AND t_dest.ano IN (2019, 2020, 2021, 2023, 2024, 2025)
GROUP BY t_dest.ano ORDER BY t_dest.ano'
```

**Resultado P05 (26291 — CAPES):**
```
+------+----------------------+
| ano  |  despesa_empenhada   |
+------+----------------------+
| 2019 |        9.483958749E7 |
| 2020 |  8.365459164999995E7 |
| 2021 |  8.455450379999997E7 |
| 2023 | 1.1542360616999988E8 |
| 2024 | 1.4626648174999997E8 |
| 2025 | 1.3111401562000011E8 |
+------+----------------------+
```

```bash
# P06 — FNDE (26298)
bq query --use_legacy_sql=false \
  --parameter='id_uo_list:ARRAY<STRING>:["26298"]' \
'SELECT t_dest.ano, SUM(t_dest.despesa_empenhada) AS despesa_empenhada
FROM `br-mec-segape.educacao_politica_tesouro.tesouro_orcamento_destaque_recebido_instituicao` AS t_dest
JOIN `br-mec-segape.educacao_politica_tesouro.tesouro_orcamento_universidade_federal_grupo` AS t_grupo
  ON t_dest.id_orgao_uge = CAST(t_grupo.id_unidade_orcamentaria AS STRING)
WHERE t_grupo.grupo_unidade_orcamentaria = "Universidade"
  AND t_dest.id_unidade_orcamentaria IN UNNEST(@id_uo_list)
  AND t_dest.ano IN (2019, 2020, 2021, 2023, 2024, 2025)
GROUP BY t_dest.ano ORDER BY t_dest.ano'
```

**Resultado P06 (26298 — FNDE):**
```
+------+----------------------+
| ano  |  despesa_empenhada   |
+------+----------------------+
| 2019 | 2.1379056049999997E7 |
| 2020 |       1.4430524789E8 |
| 2021 |       1.3658028995E8 |
| 2023 |       2.1658273136E8 |
| 2024 |  3.191068403399999E8 |
| 2025 |  8.626421786999997E7 |
+------+----------------------+
```

```bash
# P07 — EBSERH (26443)
bq query --use_legacy_sql=false \
  --parameter='id_uo_list:ARRAY<STRING>:["26443"]' \
'SELECT t_dest.ano, SUM(t_dest.despesa_empenhada) AS despesa_empenhada
FROM `br-mec-segape.educacao_politica_tesouro.tesouro_orcamento_destaque_recebido_instituicao` AS t_dest
JOIN `br-mec-segape.educacao_politica_tesouro.tesouro_orcamento_universidade_federal_grupo` AS t_grupo
  ON t_dest.id_orgao_uge = CAST(t_grupo.id_unidade_orcamentaria AS STRING)
WHERE t_grupo.grupo_unidade_orcamentaria = "Universidade"
  AND t_dest.id_unidade_orcamentaria IN UNNEST(@id_uo_list)
  AND t_dest.ano IN (2019, 2020, 2021, 2023, 2024, 2025)
GROUP BY t_dest.ano ORDER BY t_dest.ano'
```

**Resultado P07 (26443 — EBSERH):**
```
+------+---------------------+
| ano  |  despesa_empenhada  |
+------+---------------------+
| 2019 | 5.657386169000002E7 |
| 2020 |       5.489431351E7 |
| 2021 |           275125.81 |
| 2023 |       5.207851304E7 |
| 2024 |       2.001843916E7 |
| 2025 |           112686.75 |
+------+---------------------+
```

---

## Seção 6 — Queries BQ CLI executadas (exemplo: UFPE `id_uo=26242`)

### P01 — Orçamento Originário

#### Lookup — Nome da universidade

```bash
bq query --use_legacy_sql=false \
'SELECT id_unidade_orcamentaria, unidade_orcamentaria AS nome_universidade
FROM `br-mec-segape.educacao_politica_tesouro.tesouro_orcamento_universidade_federal_grupo`
WHERE id_unidade_orcamentaria = 26242
LIMIT 1'
```

**Resultado:**
```
+-------------------------+------------------------------------+
| id_unidade_orcamentaria |         nome_universidade          |
+-------------------------+------------------------------------+
|                   26242 | Universidade Federal de Pernambuco |
+-------------------------+------------------------------------+
```

---

#### P01 G1/G2 — Visão Geral: Despesa Empenhada (queries separadas por período)

```bash
# P01 G1 — Período 2019–2021
bq query --use_legacy_sql=false \
  --parameter='id_unidade_orcamentaria:INT64:26242' \
'SELECT t_uo.ano, SUM(t_uo.despesa_empenhada) AS despesa_empenhada
FROM `br-mec-segape.educacao_politica_tesouro.tesouro_orcamento_unidade_orcamentaria` AS t_uo
JOIN `br-mec-segape.educacao_politica_tesouro.tesouro_orcamento_universidade_federal_grupo` AS t_grupo
  ON CAST(t_uo.id_unidade_orcamentaria AS INT64) = t_grupo.id_unidade_orcamentaria
WHERE t_grupo.grupo_unidade_orcamentaria = "Universidade"
  AND t_uo.id_unidade_orcamentaria = CAST(@id_unidade_orcamentaria AS STRING)
  AND t_uo.ano BETWEEN 2019 AND 2021
GROUP BY t_uo.ano ORDER BY t_uo.ano'
```

**Resultado G1 (2019–2021):**
```
+------+----------------------+
| ano  |  despesa_empenhada   |
+------+----------------------+
| 2019 | 1.6076812558999996E9 |
| 2020 |  1.639185527660001E9 |
| 2021 | 1.7534616916199996E9 |
+------+----------------------+
```

```bash
# P01 G2 — Período 2023–2025
bq query --use_legacy_sql=false \
  --parameter='id_unidade_orcamentaria:INT64:26242' \
'SELECT t_uo.ano, SUM(t_uo.despesa_empenhada) AS despesa_empenhada
FROM `br-mec-segape.educacao_politica_tesouro.tesouro_orcamento_unidade_orcamentaria` AS t_uo
JOIN `br-mec-segape.educacao_politica_tesouro.tesouro_orcamento_universidade_federal_grupo` AS t_grupo
  ON CAST(t_uo.id_unidade_orcamentaria AS INT64) = t_grupo.id_unidade_orcamentaria
WHERE t_grupo.grupo_unidade_orcamentaria = "Universidade"
  AND t_uo.id_unidade_orcamentaria = CAST(@id_unidade_orcamentaria AS STRING)
  AND t_uo.ano BETWEEN 2023 AND 2025
GROUP BY t_uo.ano ORDER BY t_uo.ano'
```

**Resultado G2 (2023–2025):**
```
+------+----------------------+
| ano  |  despesa_empenhada   |
+------+----------------------+
| 2023 | 1.7881987135399992E9 |
| 2024 | 1.8720692701200001E9 |
| 2025 | 2.1355111810400004E9 |
+------+----------------------+
```

---

#### P01 G3/G4 — Resultado Lei: Obrigatório / Discricionário / Emendas

```bash
# P01 G3 — Período 2019–2021
bq query --use_legacy_sql=false \
  --parameter='id_unidade_orcamentaria:INT64:26242' \
'SELECT t_uo.ano,
  SUM(CASE WHEN t_uo.id_resultado_lei IN ("0","1") THEN t_uo.despesa_empenhada ELSE 0 END) AS obrigatorio,
  SUM(CASE WHEN t_uo.id_resultado_lei IN ("2","3") THEN t_uo.despesa_empenhada ELSE 0 END) AS discricionario,
  SUM(CASE WHEN t_uo.id_resultado_lei IN ("6","7","8","9") THEN t_uo.despesa_empenhada ELSE 0 END) AS emendas
FROM `br-mec-segape.educacao_politica_tesouro.tesouro_orcamento_unidade_orcamentaria` AS t_uo
JOIN `br-mec-segape.educacao_politica_tesouro.tesouro_orcamento_universidade_federal_grupo` AS t_grupo
  ON CAST(t_uo.id_unidade_orcamentaria AS INT64) = t_grupo.id_unidade_orcamentaria
WHERE t_grupo.grupo_unidade_orcamentaria = "Universidade"
  AND t_uo.id_unidade_orcamentaria = CAST(@id_unidade_orcamentaria AS STRING)
  AND t_uo.ano BETWEEN 2019 AND 2021
GROUP BY t_uo.ano ORDER BY t_uo.ano'
```

**Resultado G3 (2019–2021):**
```
+------+----------------------+----------------------+---------------+
| ano  |     obrigatorio      |    discricionario    |    emendas    |
+------+----------------------+----------------------+---------------+
| 2019 | 1.4270843417699993E9 | 1.8044691413000005E8 |      150000.0 |
| 2020 | 1.4457874367900002E9 | 1.8860131462999997E8 |    4796776.24 |
| 2021 |      1.58658273015E9 |       1.5328217369E8 | 1.359678778E7 |
+------+----------------------+----------------------+---------------+
```

```bash
# P01 G4 — Período 2023–2025
bq query --use_legacy_sql=false \
  --parameter='id_unidade_orcamentaria:INT64:26242' \
'SELECT t_uo.ano,
  SUM(CASE WHEN t_uo.id_resultado_lei IN ("0","1") THEN t_uo.despesa_empenhada ELSE 0 END) AS obrigatorio,
  SUM(CASE WHEN t_uo.id_resultado_lei IN ("2","3") THEN t_uo.despesa_empenhada ELSE 0 END) AS discricionario,
  SUM(CASE WHEN t_uo.id_resultado_lei IN ("6","7","8","9") THEN t_uo.despesa_empenhada ELSE 0 END) AS emendas
FROM `br-mec-segape.educacao_politica_tesouro.tesouro_orcamento_unidade_orcamentaria` AS t_uo
JOIN `br-mec-segape.educacao_politica_tesouro.tesouro_orcamento_universidade_federal_grupo` AS t_grupo
  ON CAST(t_uo.id_unidade_orcamentaria AS INT64) = t_grupo.id_unidade_orcamentaria
WHERE t_grupo.grupo_unidade_orcamentaria = "Universidade"
  AND t_uo.id_unidade_orcamentaria = CAST(@id_unidade_orcamentaria AS STRING)
  AND t_uo.ano BETWEEN 2023 AND 2025
GROUP BY t_uo.ano ORDER BY t_uo.ano'
```

**Resultado G4 (2023–2025):**
```
+------+----------------------+----------------------+------------+
| ano  |     obrigatorio      |    discricionario    |  emendas   |
+------+----------------------+----------------------+------------+
| 2023 | 1.5826118051599996E9 |       2.0075401771E8 | 4832890.67 |
| 2024 |      1.67581059282E9 | 1.9292314842000002E8 | 3335528.88 |
| 2025 |      1.93310299178E9 | 2.0190818925999996E8 |   500000.0 |
+------+----------------------+----------------------+------------+
```

---

#### P01 G5/G6 — Grupo de Despesa: Pessoal / Custeio / Capital

```bash
# P01 G5 — Período 2019–2021
bq query --use_legacy_sql=false \
  --parameter='id_unidade_orcamentaria:INT64:26242' \
'SELECT t_uo.ano,
  SUM(CASE WHEN t_uo.id_grupo_despesa = "1" THEN t_uo.despesa_empenhada ELSE 0 END) AS pessoal_encargos,
  SUM(CASE WHEN t_uo.id_grupo_despesa = "3" THEN t_uo.despesa_empenhada ELSE 0 END) AS custeio,
  SUM(CASE WHEN t_uo.id_grupo_despesa IN ("4","5") THEN t_uo.despesa_empenhada ELSE 0 END) AS capital
FROM `br-mec-segape.educacao_politica_tesouro.tesouro_orcamento_unidade_orcamentaria` AS t_uo
JOIN `br-mec-segape.educacao_politica_tesouro.tesouro_orcamento_universidade_federal_grupo` AS t_grupo
  ON CAST(t_uo.id_unidade_orcamentaria AS INT64) = t_grupo.id_unidade_orcamentaria
WHERE t_grupo.grupo_unidade_orcamentaria = "Universidade"
  AND t_uo.id_unidade_orcamentaria = CAST(@id_unidade_orcamentaria AS STRING)
  AND t_uo.ano BETWEEN 2019 AND 2021
GROUP BY t_uo.ano ORDER BY t_uo.ano'
```

**Resultado G5 (2019–2021):**
```
+------+------------------+----------------------+---------------------+
| ano  | pessoal_encargos |       custeio        |       capital       |
+------+------------------+----------------------+---------------------+
| 2019 |  1.37492548783E9 | 2.1921841334000003E8 | 1.3537354729999999E7 |
| 2020 |  1.39734663305E9 | 2.2195739105999994E8 |        1.988150355E7 |
| 2021 |  1.52984907827E9 |       1.8601517128E8 |        3.759744207E7 |
+------+------------------+----------------------+---------------------+
```

```bash
# P01 G6 — Período 2023–2025
bq query --use_legacy_sql=false \
  --parameter='id_unidade_orcamentaria:INT64:26242' \
'SELECT t_uo.ano,
  SUM(CASE WHEN t_uo.id_grupo_despesa = "1" THEN t_uo.despesa_empenhada ELSE 0 END) AS pessoal_encargos,
  SUM(CASE WHEN t_uo.id_grupo_despesa = "3" THEN t_uo.despesa_empenhada ELSE 0 END) AS custeio,
  SUM(CASE WHEN t_uo.id_grupo_despesa IN ("4","5") THEN t_uo.despesa_empenhada ELSE 0 END) AS capital
FROM `br-mec-segape.educacao_politica_tesouro.tesouro_orcamento_unidade_orcamentaria` AS t_uo
JOIN `br-mec-segape.educacao_politica_tesouro.tesouro_orcamento_universidade_federal_grupo` AS t_grupo
  ON CAST(t_uo.id_unidade_orcamentaria AS INT64) = t_grupo.id_unidade_orcamentaria
WHERE t_grupo.grupo_unidade_orcamentaria = "Universidade"
  AND t_uo.id_unidade_orcamentaria = CAST(@id_unidade_orcamentaria AS STRING)
  AND t_uo.ano BETWEEN 2023 AND 2025
GROUP BY t_uo.ano ORDER BY t_uo.ano'
```

**Resultado G6 (2023–2025):**
```
+------+----------------------+----------------------+---------------+
| ano  |   pessoal_encargos   |       custeio        |    capital    |
+------+----------------------+----------------------+---------------+
| 2023 | 1.5211272826899996E9 | 2.4682696149000007E8 | 2.024446936E7 |
| 2024 | 1.5872873659300003E9 |       2.6513078077E8 | 1.965112342E7 |
| 2025 |      1.83516698988E9 | 2.8614692040999985E8 | 1.419727075E7 |
+------+----------------------+----------------------+---------------+
```

---

#### P01 KPIs — Métricas (todos os anos)

```bash
bq query --use_legacy_sql=false \
  --parameter='id_unidade_orcamentaria:INT64:26242' \
'SELECT t_uo.ano, SUM(t_uo.despesa_empenhada) AS despesa_empenhada
FROM `br-mec-segape.educacao_politica_tesouro.tesouro_orcamento_unidade_orcamentaria` AS t_uo
JOIN `br-mec-segape.educacao_politica_tesouro.tesouro_orcamento_universidade_federal_grupo` AS t_grupo
  ON CAST(t_uo.id_unidade_orcamentaria AS INT64) = t_grupo.id_unidade_orcamentaria
WHERE t_grupo.grupo_unidade_orcamentaria = "Universidade"
  AND t_uo.id_unidade_orcamentaria = CAST(@id_unidade_orcamentaria AS STRING)
  AND t_uo.ano IN (2019, 2020, 2021, 2023, 2024, 2025)
GROUP BY t_uo.ano ORDER BY t_uo.ano'
```

**Resultado:**
```
+------+----------------------+
| ano  |  despesa_empenhada   |
+------+----------------------+
| 2019 | 1.6076812558999996E9 |
| 2020 |  1.639185527660001E9 |
| 2021 | 1.7534616916199996E9 |
| 2023 | 1.7881987135399992E9 |
| 2024 | 1.8720692701200001E9 |
| 2025 | 2.1355111810400004E9 |
+------+----------------------+
```

---

### P02 — Crédito Recebido Geral (UOs: 26101, 26290, 26291, 26298, 26443)

#### P02 G1/G2 — Destaque Recebido vs Despesa Empenhada

```bash
# P02 G1 — Período 2019–2021
bq query --use_legacy_sql=false \
  --parameter='id_uo_list:ARRAY<STRING>:["26101","26290","26291","26298","26443"]' \
'SELECT t_dest.ano,
  SUM(t_dest.destaque_recebido) AS destaque_recebido,
  SUM(t_dest.despesa_empenhada) AS despesa_empenhada
FROM `br-mec-segape.educacao_politica_tesouro.tesouro_orcamento_destaque_recebido_instituicao` AS t_dest
JOIN `br-mec-segape.educacao_politica_tesouro.tesouro_orcamento_universidade_federal_grupo` AS t_grupo
  ON t_dest.id_orgao_uge = CAST(t_grupo.id_unidade_orcamentaria AS STRING)
WHERE t_grupo.grupo_unidade_orcamentaria = "Universidade"
  AND t_dest.id_unidade_orcamentaria IN UNNEST(@id_uo_list)
  AND t_dest.ano BETWEEN 2019 AND 2021
GROUP BY t_dest.ano ORDER BY t_dest.ano'
```

**Resultado G1 (2019–2021):**
```
+------+----------------------+----------------------+
| ano  |  destaque_recebido   |  despesa_empenhada   |
+------+----------------------+----------------------+
| 2019 | 1.2439016367999973E9 | 1.2413557664299958E9 |
| 2020 | 1.3022801664200008E9 | 1.2992678011800003E9 |
| 2021 | 1.0400765012399985E9 | 1.0389165528199983E9 |
+------+----------------------+----------------------+
```

```bash
# P02 G2 — Período 2023–2025
bq query --use_legacy_sql=false \
  --parameter='id_uo_list:ARRAY<STRING>:["26101","26290","26291","26298","26443"]' \
'SELECT t_dest.ano,
  SUM(t_dest.destaque_recebido) AS destaque_recebido,
  SUM(t_dest.despesa_empenhada) AS despesa_empenhada
FROM `br-mec-segape.educacao_politica_tesouro.tesouro_orcamento_destaque_recebido_instituicao` AS t_dest
JOIN `br-mec-segape.educacao_politica_tesouro.tesouro_orcamento_universidade_federal_grupo` AS t_grupo
  ON t_dest.id_orgao_uge = CAST(t_grupo.id_unidade_orcamentaria AS STRING)
WHERE t_grupo.grupo_unidade_orcamentaria = "Universidade"
  AND t_dest.id_unidade_orcamentaria IN UNNEST(@id_uo_list)
  AND t_dest.ano BETWEEN 2023 AND 2025
GROUP BY t_dest.ano ORDER BY t_dest.ano'
```

**Resultado G2 (2023–2025):**
```
+------+----------------------+----------------------+
| ano  |  destaque_recebido   |  despesa_empenhada   |
+------+----------------------+----------------------+
| 2023 | 1.6431926454599993E9 | 1.6416015830599992E9 |
| 2024 |  1.725140758480001E9 | 1.7244206782900012E9 |
| 2025 | 1.9708201360800025E9 | 1.9696049725800018E9 |
+------+----------------------+----------------------+
```

---

#### P02 G3/G4 — Resultado Lei (Crédito Recebido)

```bash
# P02 G3 — Período 2019–2021
bq query --use_legacy_sql=false \
  --parameter='id_uo_list:ARRAY<STRING>:["26101","26290","26291","26298","26443"]' \
'SELECT t_dest.ano,
  SUM(CASE WHEN t_dest.id_resultado_lei IN ("0","1") THEN t_dest.despesa_empenhada ELSE 0 END) AS obrigatorio,
  SUM(CASE WHEN t_dest.id_resultado_lei IN ("2","3") THEN t_dest.despesa_empenhada ELSE 0 END) AS discricionario,
  SUM(CASE WHEN t_dest.id_resultado_lei IN ("6","7","8","9") THEN t_dest.despesa_empenhada ELSE 0 END) AS emendas
FROM `br-mec-segape.educacao_politica_tesouro.tesouro_orcamento_destaque_recebido_instituicao` AS t_dest
JOIN `br-mec-segape.educacao_politica_tesouro.tesouro_orcamento_universidade_federal_grupo` AS t_grupo
  ON t_dest.id_orgao_uge = CAST(t_grupo.id_unidade_orcamentaria AS STRING)
WHERE t_grupo.grupo_unidade_orcamentaria = "Universidade"
  AND t_dest.id_unidade_orcamentaria IN UNNEST(@id_uo_list)
  AND t_dest.ano BETWEEN 2019 AND 2021
GROUP BY t_dest.ano ORDER BY t_dest.ano'
```

**Resultado G3 (2019–2021):**
```
+------+---------------------+----------------------+---------------------+
| ano  |     obrigatorio     |    discricionario    |       emendas       |
+------+---------------------+----------------------+---------------------+
| 2019 |          2253627.32 | 1.1858529551699996E9 |       5.324918394E7 |
| 2020 |  1804171.4600000004 |  8.561569191500001E8 | 4.413067105700001E8 |
| 2021 | 2.936782054999999E7 |  9.538417205299989E8 | 5.570701174000001E7 |
+------+---------------------+----------------------+---------------------+
```

```bash
# P02 G4 — Período 2023–2025
bq query --use_legacy_sql=false \
  --parameter='id_uo_list:ARRAY<STRING>:["26101","26290","26291","26298","26443"]' \
'SELECT t_dest.ano,
  SUM(CASE WHEN t_dest.id_resultado_lei IN ("0","1") THEN t_dest.despesa_empenhada ELSE 0 END) AS obrigatorio,
  SUM(CASE WHEN t_dest.id_resultado_lei IN ("2","3") THEN t_dest.despesa_empenhada ELSE 0 END) AS discricionario,
  SUM(CASE WHEN t_dest.id_resultado_lei IN ("6","7","8","9") THEN t_dest.despesa_empenhada ELSE 0 END) AS emendas
FROM `br-mec-segape.educacao_politica_tesouro.tesouro_orcamento_destaque_recebido_instituicao` AS t_dest
JOIN `br-mec-segape.educacao_politica_tesouro.tesouro_orcamento_universidade_federal_grupo` AS t_grupo
  ON t_dest.id_orgao_uge = CAST(t_grupo.id_unidade_orcamentaria AS STRING)
WHERE t_grupo.grupo_unidade_orcamentaria = "Universidade"
  AND t_dest.id_unidade_orcamentaria IN UNNEST(@id_uo_list)
  AND t_dest.ano BETWEEN 2023 AND 2025
GROUP BY t_dest.ano ORDER BY t_dest.ano'
```

**Resultado G4 (2023–2025):**
```
+------+---------------------+----------------------+----------------------+
| ano  |     obrigatorio     |    discricionario    |       emendas        |
+------+---------------------+----------------------+----------------------+
| 2023 | 3.372557308999999E7 | 1.5113307294099987E9 |        9.654528056E7 |
| 2024 |   7685231.079999999 | 1.6270208653300018E9 |        8.971458188E7 |
| 2025 |       4.478274597E7 | 1.7997568416200016E9 | 1.2506538499000001E8 |
+------+---------------------+----------------------+----------------------+
```

---

#### P02 G5/G6 — Grupo de Despesa (Crédito Recebido)

```bash
# P02 G5 — Período 2019–2021
bq query --use_legacy_sql=false \
  --parameter='id_uo_list:ARRAY<STRING>:["26101","26290","26291","26298","26443"]' \
'SELECT t_dest.ano,
  SUM(CASE WHEN t_dest.id_grupo_despesa = "1" THEN t_dest.despesa_empenhada ELSE 0 END) AS pessoal_encargos,
  SUM(CASE WHEN t_dest.id_grupo_despesa = "3" THEN t_dest.despesa_empenhada ELSE 0 END) AS custeio,
  SUM(CASE WHEN t_dest.id_grupo_despesa IN ("4","5") THEN t_dest.despesa_empenhada ELSE 0 END) AS capital
FROM `br-mec-segape.educacao_politica_tesouro.tesouro_orcamento_destaque_recebido_instituicao` AS t_dest
JOIN `br-mec-segape.educacao_politica_tesouro.tesouro_orcamento_universidade_federal_grupo` AS t_grupo
  ON t_dest.id_orgao_uge = CAST(t_grupo.id_unidade_orcamentaria AS STRING)
WHERE t_grupo.grupo_unidade_orcamentaria = "Universidade"
  AND t_dest.id_unidade_orcamentaria IN UNNEST(@id_uo_list)
  AND t_dest.ano BETWEEN 2019 AND 2021
GROUP BY t_dest.ano ORDER BY t_dest.ano'
```

**Resultado G5 (2019–2021):**
```
+------+----------------------+---------------------+---------------------+
| ano  |   pessoal_encargos   |       custeio       |       capital       |
+------+----------------------+---------------------+---------------------+
| 2019 |             56593.39 | 9.452053882000005E8 | 2.960937848399999E8 |
| 2020 |            521761.63 | 1.016047599290001E9 |      2.8269844026E8 |
| 2021 | 2.6258290559999995E7 | 9.328706375699984E8 |       7.978762469E7 |
+------+----------------------+---------------------+---------------------+
```

```bash
# P02 G6 — Período 2023–2025
bq query --use_legacy_sql=false \
  --parameter='id_uo_list:ARRAY<STRING>:["26101","26290","26291","26298","26443"]' \
'SELECT t_dest.ano,
  SUM(CASE WHEN t_dest.id_grupo_despesa = "1" THEN t_dest.despesa_empenhada ELSE 0 END) AS pessoal_encargos,
  SUM(CASE WHEN t_dest.id_grupo_despesa = "3" THEN t_dest.despesa_empenhada ELSE 0 END) AS custeio,
  SUM(CASE WHEN t_dest.id_grupo_despesa IN ("4","5") THEN t_dest.despesa_empenhada ELSE 0 END) AS capital
FROM `br-mec-segape.educacao_politica_tesouro.tesouro_orcamento_destaque_recebido_instituicao` AS t_dest
JOIN `br-mec-segape.educacao_politica_tesouro.tesouro_orcamento_universidade_federal_grupo` AS t_grupo
  ON t_dest.id_orgao_uge = CAST(t_grupo.id_unidade_orcamentaria AS STRING)
WHERE t_grupo.grupo_unidade_orcamentaria = "Universidade"
  AND t_dest.id_unidade_orcamentaria IN UNNEST(@id_uo_list)
  AND t_dest.ano BETWEEN 2023 AND 2025
GROUP BY t_dest.ano ORDER BY t_dest.ano'
```

**Resultado G6 (2023–2025):**
```
+------+------------------+----------------------+----------------------+
| ano  | pessoal_encargos |       custeio        |       capital        |
+------+------------------+----------------------+----------------------+
| 2023 |    3.063754108E7 | 1.2650942812299988E9 |  3.458697607499998E8 |
| 2024 |       4812345.52 | 1.5185459157100008E9 | 2.0106241705999997E8 |
| 2025 |    4.239191047E7 |  1.481596322010001E9 | 4.4561674010000014E8 |
+------+------------------+----------------------+----------------------+
```

---

#### P02 KPIs — Métricas Crédito Recebido Geral

```bash
bq query --use_legacy_sql=false \
  --parameter='id_uo_list:ARRAY<STRING>:["26101","26290","26291","26298","26443"]' \
'SELECT t_dest.ano, SUM(t_dest.despesa_empenhada) AS despesa_empenhada
FROM `br-mec-segape.educacao_politica_tesouro.tesouro_orcamento_destaque_recebido_instituicao` AS t_dest
JOIN `br-mec-segape.educacao_politica_tesouro.tesouro_orcamento_universidade_federal_grupo` AS t_grupo
  ON t_dest.id_orgao_uge = CAST(t_grupo.id_unidade_orcamentaria AS STRING)
WHERE t_grupo.grupo_unidade_orcamentaria = "Universidade"
  AND t_dest.id_unidade_orcamentaria IN UNNEST(@id_uo_list)
  AND t_dest.ano IN (2019, 2020, 2021, 2023, 2024, 2025)
GROUP BY t_dest.ano ORDER BY t_dest.ano'
```

**Resultado:**
```
+------+----------------------+
| ano  |  despesa_empenhada   |
+------+----------------------+
| 2019 | 1.2413557664299958E9 |
| 2020 | 1.2992678011800003E9 |
| 2021 | 1.0389165528199983E9 |
| 2023 | 1.6416015830599992E9 |
| 2024 | 1.7244206782900012E9 |
| 2025 | 1.9696049725800018E9 |
+------+----------------------+
```

---

### P05 Extra — CAPES: Auxílios Financeiros ao Estudante e ao Pesquisador

```bash
# Sem parâmetro — filtro fixo: id_unidade_orcamentaria = '26291', id_elemento IN ('18','20')
bq query --use_legacy_sql=false \
'SELECT t_dest.ano,
  SUM(CASE WHEN t_dest.id_elemento = "18" THEN t_dest.despesa_empenhada ELSE 0 END) AS auxilio_estudante,
  SUM(CASE WHEN t_dest.id_elemento = "20" THEN t_dest.despesa_empenhada ELSE 0 END) AS auxilio_pesquisador
FROM `br-mec-segape.educacao_politica_tesouro.tesouro_orcamento_destaque_recebido_instituicao` AS t_dest
JOIN `br-mec-segape.educacao_politica_tesouro.tesouro_orcamento_universidade_federal_grupo` AS t_grupo
  ON t_dest.id_orgao_uge = CAST(t_grupo.id_unidade_orcamentaria AS STRING)
WHERE t_grupo.grupo_unidade_orcamentaria = "Universidade"
  AND t_dest.id_unidade_orcamentaria = "26291"
  AND t_dest.id_elemento IN ("18", "20")
GROUP BY t_dest.ano ORDER BY t_dest.ano'
```

**Resultado:**
```
+------+----------------------+----------------------+
| ano  |  auxilio_estudante   | auxilio_pesquisador  |
+------+----------------------+----------------------+
| 2019 | 1.5296852070000004E7 |    4302865.029999999 |
| 2020 |    7541751.719999999 |        1.025134127E7 |
| 2021 |    9615883.409999998 |        1.241015922E7 |
| 2023 | 1.6987420430000003E7 |        1.032540339E7 |
| 2024 | 1.9394114930000003E7 | 1.5431736650000002E7 |
| 2025 | 2.2178062499999993E7 |        2.107030965E7 |
+------+----------------------+----------------------+
```

---

## Seção 7 — Lógica de métricas (calculadas em Python — `executor.py`)

As métricas são calculadas em `_compute_metrics()` (`executor.py:263`) com base nos dados retornados pelas queries `metricas_orcamento.sql` e `metricas_credito_recebido.sql`.

### Fórmulas

| KPI | Fórmula | Parâmetro Typst gerado |
|-----|---------|------------------------|
| Acumulado Período 1 | `SUM(valor) WHERE ano IN (2019, 2020, 2021)` | `{noun_prefix}AcumuladoPeriodo1` |
| Acumulado Período 2 | `SUM(valor) WHERE ano IN (2023, 2024, 2025)` | `{noun_prefix}AcumuladoPeriodo2` |
| % Variação P1 | `(valor_2021 - valor_2019) / valor_2019 × 100` | `{page_prefix}PercentVariacaoOrcamentoPeriodo1` |
| % Variação P2 | `(valor_2025 - valor_2023) / valor_2023 × 100` | `{page_prefix}PercentVariacaoOrcamentoPeriodo2` |
| IPCA P1 (fixo) | `19,99%` | `{page_prefix}PercentIPCAPeriodo1` |
| IPCA P2 (fixo) | `14,35%` | `{page_prefix}PercentIPCAPeriodo2` |
| Incremento | `Acumulado_P2 - Acumulado_P1` | `{page_prefix}IncrementoOrcamentario` |
| % Incremento | `Incremento / Acumulado_P1 × 100` | `{page_prefix}PercentIncrementoOrcamentario` |

### Formatação

- Valores monetários: `R$ X,XX bi` (bilhões, separador decimal vírgula, milhar ponto)
- Percentuais: `X,XX%` (idem)

### Exemplo calculado — P01 UFPE (id_uo=26242)

| Ano | Despesa Empenhada (R$) |
|-----|------------------------|
| 2019 | 1.607.681.255,90 |
| 2020 | 1.639.185.527,66 |
| 2021 | 1.753.461.691,62 |
| 2023 | 1.788.198.713,54 |
| 2024 | 1.872.069.270,12 |
| 2025 | 2.135.511.181,04 |

```
Acumulado P1 = 1.607.681.255,90 + 1.639.185.527,66 + 1.753.461.691,62 = R$ 5.000.328.475,18
Acumulado P2 = 1.788.198.713,54 + 1.872.069.270,12 + 2.135.511.181,04 = R$ 5.795.779.164,70

% Variação P1 = (1.753.461.691,62 - 1.607.681.255,90) / 1.607.681.255,90 × 100 = 9,07%
% Variação P2 = (2.135.511.181,04 - 1.788.198.713,54) / 1.788.198.713,54 × 100 = 19,42%

Incremento = 5.795.779.164,70 - 5.000.328.475,18 = R$ 795.450.689,52
% Incremento = 795.450.689,52 / 5.000.328.475,18 × 100 = 15,91%
```

**Parâmetros gerados para o Typst (P01):**
```
p1OrcamentoAcumuladoPeriodo1        = "R$ 5,00 bi"
p1PercentVariacaoOrcamentoPeriodo1  = "9,07%"
p1PercentIPCAPeriodo1               = "19,99%"
p1OrcamentoAcumuladoPeriodo2        = "R$ 5,80 bi"
p1IncrementoOrcamentario            = "R$ 0,80 bi"
p1PercentVariacaoOrcamentoPeriodo2  = "19,42%"
p1PercentIPCAPeriodo2               = "14,35%"
p1PercentIncrementoOrcamentario     = "15,91%"
```

### Exemplo calculado — P02 Geral (UOs: 26101, 26290, 26291, 26298, 26443)

| Ano | Despesa Empenhada (R$) |
|-----|------------------------|
| 2019 | 1.241.355.766,43 |
| 2020 | 1.299.267.801,18 |
| 2021 | 1.038.916.552,82 |
| 2023 | 1.641.601.583,06 |
| 2024 | 1.724.420.678,29 |
| 2025 | 1.969.604.972,58 |

```
Acumulado P1 = 1.241.355.766,43 + 1.299.267.801,18 + 1.038.916.552,82 = R$ 3.579.540.120,43
Acumulado P2 = 1.641.601.583,06 + 1.724.420.678,29 + 1.969.604.972,58 = R$ 5.335.627.233,93

% Variação P1 = (1.038.916.552,82 - 1.241.355.766,43) / 1.241.355.766,43 × 100 = -16,31%
% Variação P2 = (1.969.604.972,58 - 1.641.601.583,06) / 1.641.601.583,06 × 100 = +19,98%

Incremento = 5.335.627.233,93 - 3.579.540.120,43 = R$ 1.756.087.113,50
% Incremento = 1.756.087.113,50 / 3.579.540.120,43 × 100 = 49,06%
```

**Parâmetros gerados para o Typst (P02):**
```
p2CreditoRecebidoAcumuladoPeriodo1        = "R$ 3,58 bi"
p2PercentVariacaoOrcamentoPeriodo1        = "-16,31%"
p2PercentIPCAPeriodo1                     = "19,99%"
p2CreditoRecebidoAcumuladoPeriodo2        = "R$ 5,34 bi"
p2IncrementoOrcamentario                  = "R$ 1,76 bi"
p2PercentVariacaoOrcamentoPeriodo2        = "19,98%"
p2PercentIPCAPeriodo2                     = "14,35%"
p2PercentIncrementoOrcamentario           = "49,06%"
```

---

## Seção 8 — Pontos de atenção / achados

### ✅ Verificados e consistentes

1. **Todas as 16 queries executam sem erro no BigQuery** com os parâmetros corretos (INT64 escalar para P01, ARRAY<STRING> para P02–P07, sem parâmetro para CAPES).

2. **Parâmetro `id_uo_list` é ARRAY<STRING>**, não INT64. O CLI BQ exige a sintaxe `--parameter='id_uo_list:ARRAY<STRING>:["26101","26290"]'`. No Python (`executor.py:226`), é passado como `bq.ArrayQueryParameter`.

3. **JOIN assimétrico entre tabelas:**
   - P01 usa: `CAST(t_uo.id_unidade_orcamentaria AS INT64) = t_grupo.id_unidade_orcamentaria`
   - P02–P07 usa: `t_dest.id_orgao_uge = CAST(t_grupo.id_unidade_orcamentaria AS STRING)`
   - As colunas de join têm tipos diferentes nas duas tabelas — as queries usam CAST corretamente em cada direção.

4. **`metricas_credito_recebido.sql` usa `despesa_empenhada`** (não `destaque_recebido`) para calcular os KPIs de crédito recebido. Isso é consistente com o código Python em `_compute_metrics()`.

5. **IPCA é valor fixo hardcoded** em `executor.py:31–32` (`_IPCA_PERIODO1 = 19.99`, `_IPCA_PERIODO2 = 14.35`). Não vem do BigQuery.

6. **`capes_auxilios_financeiros.sql` não usa parâmetro** — o filtro `id_unidade_orcamentaria = '26291'` está hardcoded na query. Retorna dados para todos os anos disponíveis.

7. **Todos os KPIs de P02–P07 conferem com o PDF de referência** — verificação realizada em 2026-03-10 executando as queries diretamente no BigQuery e comparando com os valores do `ATS Orçamento - Integração.pdf`.

### ⚠️ Pontos de atenção

8. **P01 não é comparável diretamente com o PDF:** O PDF mostra valores nacionais agregados (todas as universidades), enquanto P01 no Python filtra por `id_unidade_orcamentaria` individual. A query existe e funciona; os valores para UFPE (26242) são corretos, mas não podem ser confrontados linha a linha com o PDF.

9. **Queda no crédito recebido P02 em 2021 (–16% vs 2019):** O Acumulado P1 de Crédito Recebido (R$ 3,58 bi) é significativamente menor que o Acumulado P2 (R$ 5,34 bi, +49%). O percentual negativo de variação P1 (–16,31%) reflete queda real de 2021 vs 2019 — possivelmente reflexo de restrições orçamentárias do período.

10. **EBSERH (P07) mostra colapso quase total:** Variação P1 = -99,51% e Variação P2 = -99,78% refletem o fato de que os repasses da EBSERH para as universidades quase cessaram em 2021 e 2025 (apenas R$ 275 mil e R$ 113 mil, respectivamente, vs ~R$ 56 mi em 2019). Isso é dado real do BQ, consistente com o PDF.

11. **Nomenclatura `noun_prefix` vs `page_prefix` para P01:** Em P01, `noun_prefix = "p1Orcamento"` e `page_prefix = "p1"`. Para P02–P07, `noun_prefix = "{page}CreditoRecebido"` e `page_prefix = "{page}"`. Os nomes dos parâmetros gerados pelo executor devem corresponder exatamente ao esperado pelo Typst template — verificar `typst-template.typ` se novos parâmetros forem adicionados.

12. **Ano 2022 ausente:** O relatório cobre deliberadamente 2019–2021 e 2023–2025 (dois períodos de 3 anos), excluindo 2022. Isso está refletido explicitamente nos filtros `BETWEEN 2019 AND 2021` / `BETWEEN 2023 AND 2025` e no `IN (2019, 2020, 2021, 2023, 2024, 2025)` da query de métricas.
