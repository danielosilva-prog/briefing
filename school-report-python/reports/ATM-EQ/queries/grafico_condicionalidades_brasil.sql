-- Percentual por condicionalidade (1 a 5) para o Brasil.
-- Saida em linhas (1 linha por condicionalidade x atendimento), com nomes unicos.
WITH base_brasil AS (
  SELECT
    CAST(fc.ano_exercicio AS INT64) AS ano_exercicio,
    CAST(fc.id_municipio AS STRING) AS cod_ibge,
    CAST(fc.condicionalidade AS STRING) AS condicionalidade,
    fc.cumprimento
  FROM `br-mec-segape.educacao_politica_fundeb.fundeb_condicionalidade` fc
  WHERE CAST(fc.condicionalidade AS STRING) IN ("1", "2", "3", "4", "5")
),
max_ano AS (
  SELECT MAX(ano_exercicio) AS ano_ref
  FROM base_brasil
),
classificada AS (
  SELECT
    b.condicionalidade,
    CASE
      WHEN b.cumprimento IN ("H", "A") THEN "true"
      WHEN b.cumprimento IN ("I", "N") THEN "false"
      ELSE "pendente"
    END AS atendimento
  FROM base_brasil b
  JOIN max_ano a
    ON b.ano_exercicio = a.ano_ref
),
cond_base AS (
  SELECT "1" AS condicionalidade
  UNION ALL SELECT "2"
  UNION ALL SELECT "3"
  UNION ALL SELECT "4"
  UNION ALL SELECT "5"
),
status_base AS (
  SELECT "true" AS atendimento
  UNION ALL SELECT "false"
  UNION ALL SELECT "pendente"
),
contagem AS (
  SELECT
    c.condicionalidade,
    s.atendimento,
    COALESCE(COUNT(x.atendimento), 0) AS quantidade
  FROM cond_base c
  CROSS JOIN status_base s
  LEFT JOIN classificada x
    ON x.condicionalidade = c.condicionalidade
   AND x.atendimento = s.atendimento
  GROUP BY c.condicionalidade, s.atendimento
),
totais AS (
  SELECT
    condicionalidade,
    atendimento,
    quantidade,
    SUM(quantidade) OVER (PARTITION BY condicionalidade) AS total_condicionalidade
  FROM contagem
),
pct_calc AS (
  SELECT
    condicionalidade AS condicionalidadeBrasil,
    atendimento AS atendimentoBrasil,
    quantidade AS quantidadeBrasil,
    CASE
      WHEN total_condicionalidade = 0 THEN 0.0
      WHEN atendimento = "pendente" THEN
        100.0
        - SUM(
            CASE
              WHEN atendimento IN ("true", "false")
                THEN ROUND(100.0 * SAFE_DIVIDE(quantidade, NULLIF(total_condicionalidade, 0)), 2)
              ELSE 0.0
            END
          ) OVER (PARTITION BY condicionalidade)
      ELSE ROUND(100.0 * SAFE_DIVIDE(quantidade, NULLIF(total_condicionalidade, 0)), 2)
    END AS percentualBrasil
  FROM totais
)
SELECT
  (SELECT ano_ref FROM max_ano) AS anoReferencia,
  condicionalidadeBrasil,
  atendimentoBrasil,
  quantidadeBrasil,
  percentualBrasil
FROM pct_calc
ORDER BY
  CAST(condicionalidadeBrasil AS INT64),
  CASE atendimentoBrasil
    WHEN "true" THEN 1
    WHEN "false" THEN 2
    ELSE 3
  END;
