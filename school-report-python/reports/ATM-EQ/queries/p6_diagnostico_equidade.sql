WITH municipio AS (
  SELECT *
  FROM `br-mec-segape-sandbox.projeto_segape_dmape_relat_automatico.atm_eq_pneerq_diagnostico_equidade_municipio`
  WHERE co_municipio = @cod_ibge
  QUALIFY ROW_NUMBER() OVER (PARTITION BY co_municipio ORDER BY dt_carga DESC) = 1
),
municipios_uf AS (
  SELECT *
  FROM `br-mec-segape-sandbox.projeto_segape_dmape_relat_automatico.atm_eq_pneerq_diagnostico_equidade_municipio`
  WHERE co_uf = (SELECT co_uf FROM municipio)
  QUALIFY ROW_NUMBER() OVER (PARTITION BY co_municipio ORDER BY dt_carga DESC) = 1
),
municipios_brasil AS (
  SELECT *
  FROM `br-mec-segape-sandbox.projeto_segape_dmape_relat_automatico.atm_eq_pneerq_diagnostico_equidade_municipio`
  QUALIFY ROW_NUMBER() OVER (PARTITION BY co_municipio ORDER BY dt_carga DESC) = 1
),
rede_uf AS (
  SELECT
    SAFE_CAST(i_erer_geral AS FLOAT64) AS i_erer_geral
  FROM `br-mec-segape-sandbox.projeto_segape_dmape_relat_automatico.atm_eq_pneerq_diagnostico_equidade_uf`
  WHERE co_uf = (SELECT co_uf FROM municipio)
  QUALIFY ROW_NUMBER() OVER (PARTITION BY co_uf ORDER BY dt_carga DESC) = 1
),
stats_geral AS (
  SELECT
    MIN(SAFE_CAST(i_erer_geral AS FLOAT64)) AS minimo_municipios_uf,
    MAX(SAFE_CAST(i_erer_geral AS FLOAT64)) AS maximo_municipios_uf,
    AVG(SAFE_CAST(i_erer_geral AS FLOAT64)) AS media_municipios_uf,
    APPROX_QUANTILES(SAFE_CAST(i_erer_geral AS FLOAT64), 2)[OFFSET(1)] AS mediana_municipios_uf
  FROM municipios_uf
  WHERE SAFE_CAST(i_erer_geral AS FLOAT64) IS NOT NULL
),
stats_geral_brasil AS (
  SELECT
    MIN(SAFE_CAST(i_erer_geral AS FLOAT64)) AS minimo_municipios_brasil,
    MAX(SAFE_CAST(i_erer_geral AS FLOAT64)) AS maximo_municipios_brasil,
    AVG(SAFE_CAST(i_erer_geral AS FLOAT64)) AS media_municipios_brasil
  FROM municipios_brasil
  WHERE SAFE_CAST(i_erer_geral AS FLOAT64) IS NOT NULL
),
base AS (
  SELECT
    SAFE_CAST(m.i_erer_geral AS FLOAT64) AS indice_erer_municipio,
    SAFE_CAST(r.i_erer_geral AS FLOAT64) AS indice_erer_rede_uf,
    s.minimo_municipios_uf,
    s.maximo_municipios_uf,
    s.media_municipios_uf,
    s.mediana_municipios_uf,
    sb.minimo_municipios_brasil,
    sb.maximo_municipios_brasil,
    sb.media_municipios_brasil,
    m.p2_a,
    m.p20_a,
    m.p29_b,
    [
      m.p18_a, m.p18_b, m.p18_c, m.p18_d, m.p18_e,
      m.p18_f, m.p18_g, m.p18_h, m.p18_i, m.p18_j, m.p18_k
    ] AS respostas_materiais
  FROM municipio m
  CROSS JOIN stats_geral s
  CROSS JOIN stats_geral_brasil sb
  LEFT JOIN rede_uf r ON TRUE
),
indice_municipio AS (
  SELECT 'geral' AS indice, SAFE_CAST(i_erer_geral AS FLOAT64) AS valor FROM municipio
  UNION ALL
  SELECT 'institucionalizacao', SAFE_CAST(i_erer_institucionalizacao AS FLOAT64) FROM municipio
  UNION ALL
  SELECT 'formacao', SAFE_CAST(i_erer_formacao AS FLOAT64) FROM municipio
  UNION ALL
  SELECT 'gestao_escolar', SAFE_CAST(i_erer_gestao_escolar AS FLOAT64) FROM municipio
  UNION ALL
  SELECT 'material_didatico_paradidatico', SAFE_CAST(i_erer_material_didatico_paradidatico AS FLOAT64) FROM municipio
  UNION ALL
  SELECT 'financiamento', SAFE_CAST(i_erer_financiamento AS FLOAT64) FROM municipio
  UNION ALL
  SELECT 'avaliacao_monitoramento', SAFE_CAST(i_erer_avaliacao_monitoramento AS FLOAT64) FROM municipio
),
indices_uf AS (
  SELECT 'geral' AS indice, SAFE_CAST(i_erer_geral AS FLOAT64) AS valor FROM municipios_uf
  UNION ALL
  SELECT 'institucionalizacao', SAFE_CAST(i_erer_institucionalizacao AS FLOAT64) FROM municipios_uf
  UNION ALL
  SELECT 'formacao', SAFE_CAST(i_erer_formacao AS FLOAT64) FROM municipios_uf
  UNION ALL
  SELECT 'gestao_escolar', SAFE_CAST(i_erer_gestao_escolar AS FLOAT64) FROM municipios_uf
  UNION ALL
  SELECT 'material_didatico_paradidatico', SAFE_CAST(i_erer_material_didatico_paradidatico AS FLOAT64) FROM municipios_uf
  UNION ALL
  SELECT 'financiamento', SAFE_CAST(i_erer_financiamento AS FLOAT64) FROM municipios_uf
  UNION ALL
  SELECT 'avaliacao_monitoramento', SAFE_CAST(i_erer_avaliacao_monitoramento AS FLOAT64) FROM municipios_uf
),
stats_indices AS (
  SELECT
    indice,
    MIN(valor) AS minimo,
    MAX(valor) AS maximo,
    APPROX_QUANTILES(valor, 2)[OFFSET(1)] AS mediana
  FROM indices_uf
  WHERE valor IS NOT NULL
  GROUP BY indice
),
cards AS (
  SELECT
    m.indice,
    m.valor AS valor_municipio,
    s.minimo,
    s.mediana,
    s.maximo
  FROM indice_municipio m
  LEFT JOIN stats_indices s USING (indice)
),
indice_eeq_municipio AS (
  SELECT 'institucionalizacao' AS indice, SAFE_CAST(i_eeq_institucionalizacao AS FLOAT64) AS valor FROM municipio
  UNION ALL
  SELECT 'formacao', SAFE_CAST(i_eeq_formacao AS FLOAT64) FROM municipio
  UNION ALL
  SELECT 'gestao_escolar', SAFE_CAST(i_eeq_gestao_escolar AS FLOAT64) FROM municipio
  UNION ALL
  SELECT 'material_didatico_paradidatico', SAFE_CAST(i_eeq_material_didatico_paradidatico AS FLOAT64) FROM municipio
),
indices_eeq_uf AS (
  SELECT 'institucionalizacao' AS indice, SAFE_CAST(i_eeq_institucionalizacao AS FLOAT64) AS valor FROM municipios_uf
  UNION ALL
  SELECT 'formacao', SAFE_CAST(i_eeq_formacao AS FLOAT64) FROM municipios_uf
  UNION ALL
  SELECT 'gestao_escolar', SAFE_CAST(i_eeq_gestao_escolar AS FLOAT64) FROM municipios_uf
  UNION ALL
  SELECT 'material_didatico_paradidatico', SAFE_CAST(i_eeq_material_didatico_paradidatico AS FLOAT64) FROM municipios_uf
),
stats_indices_eeq AS (
  SELECT
    indice,
    MIN(valor) AS minimo,
    MAX(valor) AS maximo,
    APPROX_QUANTILES(valor, 2)[OFFSET(1)] AS mediana,
    AVG(valor) AS media_uf
  FROM indices_eeq_uf
  WHERE valor IS NOT NULL
  GROUP BY indice
),
indices_eeq_brasil AS (
  SELECT 'institucionalizacao' AS indice, SAFE_CAST(i_eeq_institucionalizacao AS FLOAT64) AS valor FROM municipios_brasil
  UNION ALL
  SELECT 'formacao', SAFE_CAST(i_eeq_formacao AS FLOAT64) FROM municipios_brasil
  UNION ALL
  SELECT 'gestao_escolar', SAFE_CAST(i_eeq_gestao_escolar AS FLOAT64) FROM municipios_brasil
  UNION ALL
  SELECT 'material_didatico_paradidatico', SAFE_CAST(i_eeq_material_didatico_paradidatico AS FLOAT64) FROM municipios_brasil
),
stats_indices_eeq_brasil AS (
  SELECT
    indice,
    AVG(valor) AS media_brasil
  FROM indices_eeq_brasil
  WHERE valor IS NOT NULL
  GROUP BY indice
),
cards_eeq AS (
  SELECT
    m.indice,
    m.valor AS valor_municipio,
    s.minimo,
    s.mediana,
    s.maximo,
    s.media_uf,
    b.media_brasil
  FROM indice_eeq_municipio m
  LEFT JOIN stats_indices_eeq s USING (indice)
  LEFT JOIN stats_indices_eeq_brasil b USING (indice)
)
SELECT
  REPLACE(FORMAT('%.1f', indice_erer_municipio), '.', ',') AS mediaIndiceGeralERERMunicipal,
  REPLACE(FORMAT('%.1f', minimo_municipios_uf), '.', ',') AS minimoIndiceGeralERERMunicipal,
  REPLACE(FORMAT('%.1f', maximo_municipios_uf), '.', ',') AS maximoIndiceGeralERERMunicipal,
  REPLACE(FORMAT('%.1f', mediana_municipios_uf), '.', ',') AS medianaIndiceGeralERERMunicipal,
  REPLACE(FORMAT('%.1f', COALESCE(indice_erer_rede_uf, media_municipios_uf)), '.', ',') AS mediaIndiceGeralERERUF,
  REPLACE(FORMAT('%.1f', minimo_municipios_uf), '.', ',') AS minimoIndiceGeralERERUF,
  REPLACE(FORMAT('%.1f', maximo_municipios_uf), '.', ',') AS maximoIndiceGeralERERUF,
  REPLACE(FORMAT('%.1f', media_municipios_brasil), '.', ',') AS mediaIndiceGeralERERBrasil,
  REPLACE(FORMAT('%.1f', minimo_municipios_brasil), '.', ',') AS minimoIndiceGeralERERBrasil,
  REPLACE(FORMAT('%.1f', maximo_municipios_brasil), '.', ',') AS maximoIndiceGeralERERBrasil,
  CAST(
      ROUND(
        CASE
        WHEN maximo_municipios_uf IS NULL OR minimo_municipios_uf IS NULL THEN 0
        WHEN maximo_municipios_uf = minimo_municipios_uf THEN 50
        ELSE GREATEST(
          0,
          LEAST(
            100,
            100 * (
              indice_erer_municipio - minimo_municipios_uf
            ) / NULLIF(maximo_municipios_uf - minimo_municipios_uf, 0)
          )
        )
      END,
      2
    ) AS STRING
  ) AS percentualIndiceGeralERERMunicipal,
  CAST(
    ROUND(
      CASE
        WHEN maximo_municipios_uf IS NULL OR minimo_municipios_uf IS NULL THEN 0
        WHEN maximo_municipios_uf = minimo_municipios_uf THEN 50
        ELSE GREATEST(
          0,
          LEAST(
            100,
            100 * (
              COALESCE(indice_erer_rede_uf, media_municipios_uf) - minimo_municipios_uf
            ) / NULLIF(maximo_municipios_uf - minimo_municipios_uf, 0)
          )
        )
      END,
      2
    ) AS STRING
  ) AS percentualIndiceGeralERERUF,
  CAST(
    ROUND(
      CASE
        WHEN maximo_municipios_brasil IS NULL OR minimo_municipios_brasil IS NULL THEN 0
        WHEN maximo_municipios_brasil = minimo_municipios_brasil THEN 50
        ELSE GREATEST(
          0,
          LEAST(
            100,
            100 * (
              indice_erer_municipio - minimo_municipios_brasil
            ) / NULLIF(maximo_municipios_brasil - minimo_municipios_brasil, 0)
          )
        )
      END,
      2
    ) AS STRING
  ) AS percentualIndiceGeralERERBrasil,
  MAX(IF(cards.indice = 'institucionalizacao', REPLACE(FORMAT('%.1f', cards.valor_municipio), '.', ','), NULL)) AS mediaIndiceInstitucionalizacaoERERMunicipal,
  MAX(IF(cards.indice = 'institucionalizacao', REPLACE(FORMAT('%.1f', cards.minimo), '.', ','), NULL)) AS minimoIndiceInstitucionalizacaoERERMunicipal,
  MAX(IF(cards.indice = 'institucionalizacao', REPLACE(FORMAT('%.1f', cards.mediana), '.', ','), NULL)) AS medianaIndiceInstitucionalizacaoERERMunicipal,
  MAX(IF(cards.indice = 'institucionalizacao', REPLACE(FORMAT('%.1f', cards.maximo), '.', ','), NULL)) AS maximoIndiceInstitucionalizacaoERERMunicipal,
  MAX(IF(cards.indice = 'institucionalizacao', REPLACE(FORMAT('%.1f', cards.valor_municipio), '.', ','), NULL)) AS indiceERER1Media,
  MAX(IF(cards.indice = 'institucionalizacao', REPLACE(FORMAT('%.1f', cards.minimo), '.', ','), NULL)) AS indiceERER1Minimo,
  MAX(IF(cards.indice = 'institucionalizacao', REPLACE(FORMAT('%.1f', cards.mediana), '.', ','), NULL)) AS indiceERER1Mediana,
  MAX(IF(cards.indice = 'institucionalizacao', REPLACE(FORMAT('%.1f', cards.maximo), '.', ','), NULL)) AS indiceERER1Maximo,
  MAX(IF(cards.indice = 'formacao', REPLACE(FORMAT('%.1f', cards.valor_municipio), '.', ','), NULL)) AS mediaIndiceFormacaoERERMunicipal,
  MAX(IF(cards.indice = 'formacao', REPLACE(FORMAT('%.1f', cards.minimo), '.', ','), NULL)) AS minimoIndiceFormacaoERERMunicipal,
  MAX(IF(cards.indice = 'formacao', REPLACE(FORMAT('%.1f', cards.mediana), '.', ','), NULL)) AS medianaIndiceFormacaoERERMunicipal,
  MAX(IF(cards.indice = 'formacao', REPLACE(FORMAT('%.1f', cards.maximo), '.', ','), NULL)) AS maximoIndiceFormacaoERERMunicipal,
  MAX(IF(cards.indice = 'formacao', REPLACE(FORMAT('%.1f', cards.valor_municipio), '.', ','), NULL)) AS indiceERER2Media,
  MAX(IF(cards.indice = 'formacao', REPLACE(FORMAT('%.1f', cards.minimo), '.', ','), NULL)) AS indiceERER2Minimo,
  MAX(IF(cards.indice = 'formacao', REPLACE(FORMAT('%.1f', cards.mediana), '.', ','), NULL)) AS indiceERER2Mediana,
  MAX(IF(cards.indice = 'formacao', REPLACE(FORMAT('%.1f', cards.maximo), '.', ','), NULL)) AS indiceERER2Maximo,
  MAX(IF(cards.indice = 'gestao_escolar', REPLACE(FORMAT('%.1f', cards.valor_municipio), '.', ','), NULL)) AS mediaIndiceGestaoEscolarERERMunicipal,
  MAX(IF(cards.indice = 'gestao_escolar', REPLACE(FORMAT('%.1f', cards.minimo), '.', ','), NULL)) AS minimoIndiceGestaoEscolarERERMunicipal,
  MAX(IF(cards.indice = 'gestao_escolar', REPLACE(FORMAT('%.1f', cards.mediana), '.', ','), NULL)) AS medianaIndiceGestaoEscolarERERMunicipal,
  MAX(IF(cards.indice = 'gestao_escolar', REPLACE(FORMAT('%.1f', cards.maximo), '.', ','), NULL)) AS maximoIndiceGestaoEscolarERERMunicipal,
  MAX(IF(cards.indice = 'gestao_escolar', REPLACE(FORMAT('%.1f', cards.valor_municipio), '.', ','), NULL)) AS indiceERER3Media,
  MAX(IF(cards.indice = 'gestao_escolar', REPLACE(FORMAT('%.1f', cards.minimo), '.', ','), NULL)) AS indiceERER3Minimo,
  MAX(IF(cards.indice = 'gestao_escolar', REPLACE(FORMAT('%.1f', cards.mediana), '.', ','), NULL)) AS indiceERER3Mediana,
  MAX(IF(cards.indice = 'gestao_escolar', REPLACE(FORMAT('%.1f', cards.maximo), '.', ','), NULL)) AS indiceERER3Maximo,
  MAX(IF(cards.indice = 'material_didatico_paradidatico', REPLACE(FORMAT('%.1f', cards.valor_municipio), '.', ','), NULL)) AS mediaIndiceMaterialDidaticoParadidaticoERERMunicipal,
  MAX(IF(cards.indice = 'material_didatico_paradidatico', REPLACE(FORMAT('%.1f', cards.minimo), '.', ','), NULL)) AS minimoIndiceMaterialDidaticoParadidaticoERERMunicipal,
  MAX(IF(cards.indice = 'material_didatico_paradidatico', REPLACE(FORMAT('%.1f', cards.mediana), '.', ','), NULL)) AS medianaIndiceMaterialDidaticoParadidaticoERERMunicipal,
  MAX(IF(cards.indice = 'material_didatico_paradidatico', REPLACE(FORMAT('%.1f', cards.maximo), '.', ','), NULL)) AS maximoIndiceMaterialDidaticoParadidaticoERERMunicipal,
  MAX(IF(cards.indice = 'material_didatico_paradidatico', REPLACE(FORMAT('%.1f', cards.valor_municipio), '.', ','), NULL)) AS indiceERER4Media,
  MAX(IF(cards.indice = 'material_didatico_paradidatico', REPLACE(FORMAT('%.1f', cards.minimo), '.', ','), NULL)) AS indiceERER4Minimo,
  MAX(IF(cards.indice = 'material_didatico_paradidatico', REPLACE(FORMAT('%.1f', cards.mediana), '.', ','), NULL)) AS indiceERER4Mediana,
  MAX(IF(cards.indice = 'material_didatico_paradidatico', REPLACE(FORMAT('%.1f', cards.maximo), '.', ','), NULL)) AS indiceERER4Maximo,
  MAX(IF(cards.indice = 'financiamento', REPLACE(FORMAT('%.1f', cards.valor_municipio), '.', ','), NULL)) AS mediaIndiceFinanciamentoERERMunicipal,
  MAX(IF(cards.indice = 'financiamento', REPLACE(FORMAT('%.1f', cards.minimo), '.', ','), NULL)) AS minimoIndiceFinanciamentoERERMunicipal,
  MAX(IF(cards.indice = 'financiamento', REPLACE(FORMAT('%.1f', cards.mediana), '.', ','), NULL)) AS medianaIndiceFinanciamentoERERMunicipal,
  MAX(IF(cards.indice = 'financiamento', REPLACE(FORMAT('%.1f', cards.maximo), '.', ','), NULL)) AS maximoIndiceFinanciamentoERERMunicipal,
  MAX(IF(cards.indice = 'financiamento', REPLACE(FORMAT('%.1f', cards.valor_municipio), '.', ','), NULL)) AS indiceERER5Media,
  MAX(IF(cards.indice = 'financiamento', REPLACE(FORMAT('%.1f', cards.minimo), '.', ','), NULL)) AS indiceERER5Minimo,
  MAX(IF(cards.indice = 'financiamento', REPLACE(FORMAT('%.1f', cards.mediana), '.', ','), NULL)) AS indiceERER5Mediana,
  MAX(IF(cards.indice = 'financiamento', REPLACE(FORMAT('%.1f', cards.maximo), '.', ','), NULL)) AS indiceERER5Maximo,
  MAX(IF(cards.indice = 'avaliacao_monitoramento', REPLACE(FORMAT('%.1f', cards.valor_municipio), '.', ','), NULL)) AS mediaIndiceAvaliacaoMonitoramentoERERMunicipal,
  MAX(IF(cards.indice = 'avaliacao_monitoramento', REPLACE(FORMAT('%.1f', cards.minimo), '.', ','), NULL)) AS minimoIndiceAvaliacaoMonitoramentoERERMunicipal,
  MAX(IF(cards.indice = 'avaliacao_monitoramento', REPLACE(FORMAT('%.1f', cards.mediana), '.', ','), NULL)) AS medianaIndiceAvaliacaoMonitoramentoERERMunicipal,
  MAX(IF(cards.indice = 'avaliacao_monitoramento', REPLACE(FORMAT('%.1f', cards.maximo), '.', ','), NULL)) AS maximoIndiceAvaliacaoMonitoramentoERERMunicipal,
  MAX(IF(cards.indice = 'avaliacao_monitoramento', REPLACE(FORMAT('%.1f', cards.valor_municipio), '.', ','), NULL)) AS indiceERER6Media,
  MAX(IF(cards.indice = 'avaliacao_monitoramento', REPLACE(FORMAT('%.1f', cards.minimo), '.', ','), NULL)) AS indiceERER6Minimo,
  MAX(IF(cards.indice = 'avaliacao_monitoramento', REPLACE(FORMAT('%.1f', cards.mediana), '.', ','), NULL)) AS indiceERER6Mediana,
  MAX(IF(cards.indice = 'avaliacao_monitoramento', REPLACE(FORMAT('%.1f', cards.maximo), '.', ','), NULL)) AS indiceERER6Maximo,
  MAX(IF(cards_eeq.indice = 'institucionalizacao', REPLACE(FORMAT('%.1f', cards_eeq.valor_municipio), '.', ','), NULL)) AS indiceEEQ1Media,
  MAX(IF(cards_eeq.indice = 'institucionalizacao', REPLACE(FORMAT('%.1f', cards_eeq.minimo), '.', ','), NULL)) AS indiceEEQ1Minimo,
  MAX(IF(cards_eeq.indice = 'institucionalizacao', REPLACE(FORMAT('%.1f', cards_eeq.mediana), '.', ','), NULL)) AS indiceEEQ1Mediana,
  MAX(IF(cards_eeq.indice = 'institucionalizacao', REPLACE(FORMAT('%.1f', cards_eeq.maximo), '.', ','), NULL)) AS indiceEEQ1Maximo,
  MAX(IF(cards_eeq.indice = 'formacao', REPLACE(FORMAT('%.1f', cards_eeq.valor_municipio), '.', ','), NULL)) AS indiceEEQ2Media,
  MAX(IF(cards_eeq.indice = 'formacao', REPLACE(FORMAT('%.1f', cards_eeq.minimo), '.', ','), NULL)) AS indiceEEQ2Minimo,
  MAX(IF(cards_eeq.indice = 'formacao', REPLACE(FORMAT('%.1f', cards_eeq.mediana), '.', ','), NULL)) AS indiceEEQ2Mediana,
  MAX(IF(cards_eeq.indice = 'formacao', REPLACE(FORMAT('%.1f', cards_eeq.maximo), '.', ','), NULL)) AS indiceEEQ2Maximo,
  MAX(IF(cards_eeq.indice = 'gestao_escolar', REPLACE(FORMAT('%.1f', cards_eeq.valor_municipio), '.', ','), NULL)) AS indiceEEQ3Media,
  MAX(IF(cards_eeq.indice = 'gestao_escolar', REPLACE(FORMAT('%.1f', cards_eeq.minimo), '.', ','), NULL)) AS indiceEEQ3Minimo,
  MAX(IF(cards_eeq.indice = 'gestao_escolar', REPLACE(FORMAT('%.1f', cards_eeq.mediana), '.', ','), NULL)) AS indiceEEQ3Mediana,
  MAX(IF(cards_eeq.indice = 'gestao_escolar', REPLACE(FORMAT('%.1f', cards_eeq.maximo), '.', ','), NULL)) AS indiceEEQ3Maximo,
  MAX(IF(cards_eeq.indice = 'material_didatico_paradidatico', REPLACE(FORMAT('%.1f', cards_eeq.valor_municipio), '.', ','), NULL)) AS indiceEEQ4Media,
  MAX(IF(cards_eeq.indice = 'material_didatico_paradidatico', REPLACE(FORMAT('%.1f', cards_eeq.minimo), '.', ','), NULL)) AS indiceEEQ4Minimo,
  MAX(IF(cards_eeq.indice = 'material_didatico_paradidatico', REPLACE(FORMAT('%.1f', cards_eeq.mediana), '.', ','), NULL)) AS indiceEEQ4Mediana,
  MAX(IF(cards_eeq.indice = 'material_didatico_paradidatico', REPLACE(FORMAT('%.1f', cards_eeq.maximo), '.', ','), NULL)) AS indiceEEQ4Maximo,
  MAX(IF(cards_eeq.indice = 'institucionalizacao', REPLACE(FORMAT('%.1f', cards_eeq.valor_municipio), '.', ','), NULL)) AS indiceEEQ1Municipio,
  MAX(IF(cards_eeq.indice = 'institucionalizacao', REPLACE(FORMAT('%.1f', cards_eeq.media_uf), '.', ','), NULL)) AS indiceEEQ1MediaUF,
  MAX(IF(cards_eeq.indice = 'institucionalizacao', REPLACE(FORMAT('%.1f', cards_eeq.media_brasil), '.', ','), NULL)) AS indiceEEQ1MediaBrasil,
  MAX(IF(cards_eeq.indice = 'formacao', REPLACE(FORMAT('%.1f', cards_eeq.valor_municipio), '.', ','), NULL)) AS indiceEEQ2Municipio,
  MAX(IF(cards_eeq.indice = 'formacao', REPLACE(FORMAT('%.1f', cards_eeq.media_uf), '.', ','), NULL)) AS indiceEEQ2MediaUF,
  MAX(IF(cards_eeq.indice = 'formacao', REPLACE(FORMAT('%.1f', cards_eeq.media_brasil), '.', ','), NULL)) AS indiceEEQ2MediaBrasil,
  MAX(IF(cards_eeq.indice = 'gestao_escolar', REPLACE(FORMAT('%.1f', cards_eeq.valor_municipio), '.', ','), NULL)) AS indiceEEQ3Municipio,
  MAX(IF(cards_eeq.indice = 'gestao_escolar', REPLACE(FORMAT('%.1f', cards_eeq.media_uf), '.', ','), NULL)) AS indiceEEQ3MediaUF,
  MAX(IF(cards_eeq.indice = 'gestao_escolar', REPLACE(FORMAT('%.1f', cards_eeq.media_brasil), '.', ','), NULL)) AS indiceEEQ3MediaBrasil,
  MAX(IF(cards_eeq.indice = 'material_didatico_paradidatico', REPLACE(FORMAT('%.1f', cards_eeq.valor_municipio), '.', ','), NULL)) AS indiceEEQ4Municipio,
  MAX(IF(cards_eeq.indice = 'material_didatico_paradidatico', REPLACE(FORMAT('%.1f', cards_eeq.media_uf), '.', ','), NULL)) AS indiceEEQ4MediaUF,
  MAX(IF(cards_eeq.indice = 'material_didatico_paradidatico', REPLACE(FORMAT('%.1f', cards_eeq.media_brasil), '.', ','), NULL)) AS indiceEEQ4MediaBrasil,
  CASE
    WHEN SAFE_CAST((SELECT i_geral_eeq FROM municipio) AS FLOAT64) IS NULL
      AND SAFE_CAST((SELECT i_eeq_institucionalizacao FROM municipio) AS FLOAT64) IS NULL
      AND SAFE_CAST((SELECT i_eeq_formacao FROM municipio) AS FLOAT64) IS NULL
      AND SAFE_CAST((SELECT i_eeq_gestao_escolar FROM municipio) AS FLOAT64) IS NULL
      AND SAFE_CAST((SELECT i_eeq_material_didatico_paradidatico FROM municipio) AS FLOAT64) IS NULL
    THEN 'Não respondeu esta parte do Diagnóstico'
    ELSE 'Respondeu'
  END AS statusRespostaEEQ,
  CASE p2_a
    WHEN '0' THEN 'Nenhum'
    WHEN '1' THEN '1 a 5'
    WHEN '2' THEN '6 a 10'
    WHEN '3' THEN 'Mais de 10'
    ELSE 'Não respondeu'
  END AS formacoesERER,
  CASE p20_a
    WHEN '1' THEN 'Realizou'
    WHEN '0' THEN 'Não realizou'
    ELSE 'Não respondeu'
  END AS revisaoCurriculo,
  CASE
    WHEN EXISTS(SELECT 1 FROM UNNEST(respostas_materiais) AS resposta WHERE resposta = '1') THEN 'Realiza'
    WHEN EXISTS(SELECT 1 FROM UNNEST(respostas_materiais) AS resposta WHERE resposta = '0') THEN 'Não realiza'
    ELSE 'Não respondeu'
  END AS aquisicaoMateriais,
  CASE p29_b
    WHEN '1' THEN 'Não adota'
    WHEN '2' THEN 'Adota'
    WHEN '0' THEN 'Não há cadastro'
    ELSE 'Não respondeu'
  END AS adocaoCriterioPriorizacao
FROM base
LEFT JOIN cards ON TRUE
LEFT JOIN cards_eeq ON TRUE
GROUP BY
  indice_erer_municipio,
  indice_erer_rede_uf,
  minimo_municipios_uf,
  maximo_municipios_uf,
  media_municipios_uf,
  mediana_municipios_uf,
  minimo_municipios_brasil,
  maximo_municipios_brasil,
  media_municipios_brasil,
  p2_a,
  p20_a,
  p29_b,
  respostas_materiais
