WITH municipio_ref AS (
  SELECT
    CAST(id_municipio AS STRING) AS cod_ibge,
    sigla_uf AS uf
  FROM `br-mec-segape.educacao_dados_mestres.municipio`
  WHERE CAST(id_municipio AS STRING) = @cod_ibge
  LIMIT 1
),
max_ano_vaar AS (
  SELECT MAX(CAST(f.ano AS INT64)) AS ano_ref
  FROM `br-mec-segape.indicador_politica_fundeb_base.fundeb_base_repasse_estimativa` f
  WHERE
    f.status = "Previsto"
    AND REGEXP_CONTAINS(UPPER(f.tipo_transferencia), r"VAAR")
),
media_vaar_uf AS (
  SELECT
    AVG(mun.valor_municipio) AS valor
  FROM (
    SELECT
      CAST(f.id_ibge AS STRING) AS cod_ibge,
      SUM(COALESCE(f.valor, 0)) AS valor_municipio
    FROM `br-mec-segape.indicador_politica_fundeb_base.fundeb_base_repasse_estimativa` f
    JOIN `br-mec-segape.educacao_dados_mestres.municipio` m
      ON CAST(m.id_municipio AS STRING) = CAST(f.id_ibge AS STRING)
    JOIN municipio_ref r
      ON m.sigla_uf = r.uf
    JOIN max_ano_vaar a
      ON CAST(f.ano AS INT64) = a.ano_ref
    WHERE
      f.status = "Previsto"
      AND REGEXP_CONTAINS(UPPER(f.tipo_transferencia), r"VAAR")
    GROUP BY CAST(f.id_ibge AS STRING)
  ) AS mun
)
SELECT
  CONCAT(
    "R$ ",
    REPLACE(
      REPLACE(
        REPLACE(
          FORMAT("%'.2f", COALESCE((SELECT valor FROM media_vaar_uf), 0)),
          ",",
          "§"
        ),
        ".",
        ","
      ),
      "§",
      "."
    )
  ) AS p2ValorComplementacaoVAARMediaUF,
  CAST(COALESCE((SELECT ano_ref FROM max_ano_vaar), 0) AS STRING) AS p2ValorComplementacaoVAARMediaUFAno
