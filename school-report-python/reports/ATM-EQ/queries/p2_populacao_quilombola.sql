WITH ano_referencia AS (
  SELECT
    MAX(ano) AS ano
  FROM `br-mec-segape.educacao_ibge_dados_abertos.ibge_censo_populacao_quilombola`
  WHERE CAST(id_municipio AS STRING) = @cod_ibge
),
populacao_quilombola AS (
  SELECT
    COALESCE(SUM(populacao), 0) AS valor
  FROM `br-mec-segape.educacao_ibge_dados_abertos.ibge_censo_populacao_quilombola`
  WHERE CAST(id_municipio AS STRING) = @cod_ibge
    AND ano = (SELECT ano FROM ano_referencia)
    AND idade IN (
      '0 a 4 anos',
      '5 a 9 anos',
      '10 a 14 anos',
      '15 a 19 anos',
      '20 a 24 anos',
      '25 a 29 anos',
      '30 a 34 anos',
      '35 a 39 anos',
      '40 a 44 anos',
      '45 a 49 anos',
      '50 a 54 anos',
      '55 a 59 anos',
      '60 a 64 anos',
      '65 a 69 anos',
      '70 a 74 anos',
      '75 a 79 anos',
      '80 a 84 anos',
      '85 a 89 anos',
      '90 a 94 anos',
      '95 a 99 anos',
      '100 anos ou mais'
    )
)
SELECT
  REPLACE(
    FORMAT(
      "%'d",
      CAST(COALESCE((SELECT valor FROM populacao_quilombola), 0) AS INT64)
    ),
    ",",
    "."
  ) AS populacaoQuilombola,
  COALESCE(CAST((SELECT ano FROM ano_referencia) AS STRING), "-") AS populacaoQuilombolaAno
