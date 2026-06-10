-- Valor previsto de Complementacao VAAR para o municipio
-- Regra: ultima combinacao de ano + portaria com status "Previsto"
WITH base_prevista AS (
  SELECT
    CAST(ano AS INT64) AS ano,
    CAST(portaria AS STRING) AS portaria,
    COALESCE(valor, 0) AS valor
  FROM `br-mec-segape-sandbox.projeto_segape_dmape_relat_automatico.fundeb_base_repasse_estimativa`
  WHERE
    status = "Previsto"
    AND CAST(id_ibge AS STRING) = @cod_ibge
    AND tipo_transferencia = "Complementação VAAR"

  UNION ALL

  SELECT
    CAST(ano AS INT64) AS ano,
    CAST(portaria AS STRING) AS portaria,
    COALESCE(valor, 0) AS valor
  FROM `br-mec-segape.indicador_politica_fundeb_base.fundeb_base_repasse_estimativa`
  WHERE
    status = "Previsto"
    AND CAST(id_ibge AS STRING) = @cod_ibge
    AND tipo_transferencia = "Complementação VAAR"
    AND CAST(ano AS INT64) >= 2025
),
ultima_portaria AS (
  SELECT ano, portaria
  FROM (
    SELECT
      ano,
      portaria,
      ROW_NUMBER() OVER (
        ORDER BY
          ano DESC,
          COALESCE(SAFE_CAST(REGEXP_EXTRACT(portaria, r"^\s*(\d+)") AS INT64), 0) DESC,
          portaria DESC
      ) AS rn
    FROM (
      SELECT DISTINCT ano, portaria
      FROM base_prevista
    )
  )
  WHERE rn = 1
)
SELECT
  COALESCE(
    CAST((SELECT ano FROM ultima_portaria LIMIT 1) AS STRING),
    CAST(EXTRACT(YEAR FROM CURRENT_DATE("America/Sao_Paulo")) AS STRING)
  ) AS p2AnoReferencia,
  COALESCE(
    (SELECT portaria FROM ultima_portaria LIMIT 1),
    "-"
  ) AS p2PortariaReferencia,
  COALESCE(
    (
      SELECT SUM(b.valor)
      FROM base_prevista b
      JOIN ultima_portaria u
        ON b.ano = u.ano
       AND b.portaria = u.portaria
    ),
    0
  ) AS p2ValorComplementacaoVAARAnoReferencia;
