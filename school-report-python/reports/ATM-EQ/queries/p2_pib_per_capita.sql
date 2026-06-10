WITH max_ano_pib AS (
  SELECT MAX(ano) AS ano_ref
  FROM `br-mec-segape.educacao_ibge_dados_abertos.ibge_pib_municipio`
  WHERE id_municipio = @cod_ibge
),
pib_municipio AS (
  SELECT
    CAST(p.ano AS INT64) AS ano_ref,
    COALESCE(p.produto_interno_bruto_per_capita_a_precos_correntes, 0) AS valor
  FROM `br-mec-segape.educacao_ibge_dados_abertos.ibge_pib_municipio` p
  JOIN max_ano_pib a ON a.ano_ref = p.ano
  WHERE p.id_municipio = @cod_ibge
)
SELECT
  CONCAT(
    "R$ ",
    REPLACE(FORMAT("%'d", CAST(ROUND(COALESCE((SELECT valor FROM pib_municipio), 0)) AS INT64)), ",", ".")
  ) AS p2PibPerCapita,
  CAST(COALESCE((SELECT ano_ref FROM pib_municipio), 0) AS STRING) AS p2PibPerCapitaAno
