-- Valores previstos de VAAR por municipio (2023, 2024, 2025, 2026)
WITH anos_base AS (
  SELECT 2023 AS ano
  UNION ALL SELECT 2024
  UNION ALL SELECT 2025
  UNION ALL SELECT 2026
),
base_prevista AS (
  SELECT
    CAST(f.ano AS INT64) AS ano,
    CAST(f.portaria AS STRING) AS portaria,
    COALESCE(f.valor, 0) AS valor
  FROM `br-mec-segape-sandbox.projeto_segape_dmape_relat_automatico.fundeb_base_repasse_estimativa` f
  WHERE
    f.status = "Previsto"
    AND f.tipo_transferencia = "Complementação VAAR"
    AND CAST(f.id_ibge AS STRING) = @cod_ibge
    AND CAST(f.ano AS INT64) IN (2023, 2024)

  UNION ALL

  SELECT
    CAST(f.ano AS INT64) AS ano,
    CAST(f.portaria AS STRING) AS portaria,
    COALESCE(f.valor, 0) AS valor
  FROM `br-mec-segape.indicador_politica_fundeb_base.fundeb_base_repasse_estimativa` f
  WHERE
    f.status = "Previsto"
    AND f.tipo_transferencia = "Complementação VAAR"
    AND CAST(f.id_ibge AS STRING) = @cod_ibge
    AND CAST(f.ano AS INT64) >= 2025
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
vaar_previsto AS (
  SELECT
    b.ano,
    SUM(b.valor) AS valorPrevistoComplementacaoVAARMunicipio
  FROM base_prevista b
  JOIN ultima_portaria_ano u
    ON b.ano = u.ano
   AND b.portaria = u.portaria
  GROUP BY b.ano
)
SELECT
  a.ano AS anoReferencia,
  COALESCE(v.valorPrevistoComplementacaoVAARMunicipio, 0) AS valorPrevistoComplementacaoVAARMunicipio
FROM anos_base a
LEFT JOIN vaar_previsto v
  ON v.ano = a.ano
ORDER BY a.ano;
