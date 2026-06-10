-- Crescimento da complementacao VAAR/FUNDEB (Brasil) - 2023 a 2026
-- Regra: valores nominais de "Previsto" para Estados e Municipios, usando
-- a ultima Portaria Interministerial de cada ano.
WITH anos_base AS (
  SELECT 2023 AS ano
  UNION ALL SELECT 2024
  UNION ALL SELECT 2025
  UNION ALL SELECT 2026
),
base_prevista AS (
  SELECT
    CAST(ano AS INT64) AS ano,
    CAST(portaria AS STRING) AS portaria,
    COALESCE(valor, 0) AS valor
  FROM `br-mec-segape-sandbox.projeto_segape_dmape_relat_automatico.fundeb_base_repasse_estimativa`
  WHERE
    status = "Previsto"
    AND tipo_transferencia = "Complementação VAAR"
    AND CAST(ano AS INT64) IN (2023, 2024)

  UNION ALL

  SELECT
    CAST(ano AS INT64) AS ano,
    CAST(portaria AS STRING) AS portaria,
    COALESCE(valor, 0) AS valor
  FROM `br-mec-segape.indicador_politica_fundeb_base.fundeb_base_repasse_estimativa`
  WHERE
    status = "Previsto"
    AND tipo_transferencia = "Complementação VAAR"
    AND CAST(ano AS INT64) IN (2025, 2026)
),
ultima_portaria_ano AS (
  SELECT ano, portaria
  FROM (
    SELECT
      ano,
      portaria,
      ROW_NUMBER() OVER (
        PARTITION BY ano
        ORDER BY
          COALESCE(SAFE_CAST(REGEXP_EXTRACT(portaria, r"^\s*(\d+)") AS INT64), 0) DESC,
          portaria DESC
      ) AS rn
    FROM (
      SELECT DISTINCT ano, portaria
      FROM base_prevista
    )
  )
  WHERE rn = 1
),
agregado AS (
  SELECT
    b.ano,
    SUM(b.valor) AS valorNominalVaar
  FROM base_prevista b
  JOIN ultima_portaria_ano u
    ON b.ano = u.ano
   AND b.portaria = u.portaria
  GROUP BY b.ano
)
SELECT
  a.ano AS anoReferencia,
  COALESCE(g.valorNominalVaar, 0) AS valorNominalVaar
FROM anos_base a
LEFT JOIN agregado g
  ON a.ano = g.ano
ORDER BY a.ano;
