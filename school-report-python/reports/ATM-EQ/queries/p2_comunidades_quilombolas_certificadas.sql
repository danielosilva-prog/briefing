WITH base AS (
  SELECT
    id_municipio
  FROM `br-mec-segape-sandbox.projeto_segape_dmape_relat_automatico.comunidade_quilombola_certificada_municipio`
  WHERE CAST(id_municipio AS STRING) = @cod_ibge
)
SELECT
  REPLACE(
    FORMAT("%'d", COUNT(*)),
    ",",
    "."
  ) AS comunidadesQuilombolas,
  IF(COUNT(*) > 0, "2025", "-") AS comunidadesQuilombolasAno
FROM base
