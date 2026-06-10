WITH max_ano_pop AS (
  SELECT MAX(ano) AS ano_ref
  FROM `br-mec-segape.educacao_ibge_dados_abertos.ibge_estimativa_populacao`
  WHERE CAST(id_ibge AS STRING) = @cod_ibge
),
pop_municipio AS (
  SELECT
    CAST(p.ano AS INT64) AS ano_ref,
    COALESCE(p.populacao_estimada, 0) AS valor
  FROM `br-mec-segape.educacao_ibge_dados_abertos.ibge_estimativa_populacao` p
  JOIN max_ano_pop a ON a.ano_ref = p.ano
  WHERE CAST(p.id_ibge AS STRING) = @cod_ibge
)
SELECT
  REPLACE(FORMAT("%'d", CAST(ROUND(COALESCE((SELECT valor FROM pop_municipio), 0)) AS INT64)), ",", ".") AS p2NumeroHabitantes,
  CAST(COALESCE((SELECT ano_ref FROM pop_municipio), 0) AS STRING) AS p2NumeroHabitantesAno
