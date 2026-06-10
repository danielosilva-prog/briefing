CREATE OR REPLACE TABLE `br-mec-segape-sandbox.projeto_segape_dmape_relat_automatico.atm_eq_grafico_distribuicao_matriculas` AS
WITH anos_comuns AS (
  SELECT DISTINCT
    CAST(c.id_municipio AS STRING) AS cod_ibge,
    c.ano
  FROM `br-mec-segape.educacao_inep_dados_abertos.censo_escolar_escola` c
  JOIN `br-mec-segape.educacao_politica_inep_censo.inep_censo` i
    ON i.ano = c.ano
   AND i.cod_ibge = CAST(c.id_municipio AS STRING)
   AND i.dependencia_administrativa = "Municipal"
  WHERE CAST(c.tipo_situacao_funcionamento AS STRING) = "1"
),
ano_base AS (
  SELECT cod_ibge, MAX(ano) AS ano_ref
  FROM anos_comuns
  GROUP BY cod_ibge
),
matriculas_enriquecidas AS (
  SELECT
    i.cod_ibge,
    i.identificacao_unica,
    CASE
      WHEN COALESCE(NULLIF(TRIM(i.etnia), ""), "Não declarada") IN (
        "Branca",
        "Preta",
        "Parda",
        "Amarela",
        "Indígena",
        "Não declarada"
      ) THEN COALESCE(NULLIF(TRIM(i.etnia), ""), "Não declarada")
      ELSE "Não declarada"
    END AS etnia,
    IF(CAST(c.tipo_localizacao_diferenciada AS STRING) = "3", 1, 0) AS fl_quilombola
  FROM `br-mec-segape.educacao_politica_inep_censo.inep_censo` i
  JOIN ano_base a
    ON a.cod_ibge = i.cod_ibge
   AND a.ano_ref = i.ano
  JOIN `br-mec-segape.educacao_inep_dados_abertos.censo_escolar_escola` c
    ON c.ano = i.ano
   AND CAST(c.id_municipio AS STRING) = i.cod_ibge
   AND CAST(c.id_escola AS STRING) = CAST(i.id_escola AS STRING)
  WHERE i.dependencia_administrativa = "Municipal"
    AND CAST(c.tipo_situacao_funcionamento AS STRING) = "1"
),
matriculas_base AS (
  SELECT
    cod_ibge,
    identificacao_unica,
    CASE
      WHEN MAX(fl_quilombola) = 1 THEN "Quilombola"
      ELSE ANY_VALUE(etnia)
    END AS categoria
  FROM matriculas_enriquecidas
  GROUP BY cod_ibge, identificacao_unica
),
agregados AS (
  SELECT
    cod_ibge,
    COUNT(*) AS total_matriculas,
    COUNTIF(categoria = "Amarela") AS amarela,
    COUNTIF(categoria = "Branca") AS branca,
    COUNTIF(categoria = "Indígena") AS indigena,
    COUNTIF(categoria = "Não declarada") AS nao_declarada,
    COUNTIF(categoria = "Parda") AS parda,
    COUNTIF(categoria = "Preta") AS preta,
    COUNTIF(categoria = "Quilombola") AS quilombola
  FROM matriculas_base
  GROUP BY cod_ibge
)
SELECT
  a.cod_ibge,
  categoria,
  quantidade,
  COALESCE(ROUND(SAFE_DIVIDE(quantidade, NULLIF(total_matriculas, 0)) * 100, 2), 0) AS percentual,
  b.ano_ref AS anoReferencia
FROM agregados a
JOIN ano_base b
  ON b.cod_ibge = a.cod_ibge,
UNNEST([
  STRUCT("Amarela" AS categoria, amarela AS quantidade),
  STRUCT("Branca" AS categoria, branca AS quantidade),
  STRUCT("Indígena" AS categoria, indigena AS quantidade),
  STRUCT("Não declarada" AS categoria, nao_declarada AS quantidade),
  STRUCT("Parda" AS categoria, parda AS quantidade),
  STRUCT("Preta" AS categoria, preta AS quantidade),
  STRUCT("Quilombola" AS categoria, quilombola AS quantidade)
]);
