-- P02 G2: Créditos Totais = UO + Destaque + Bolsas CAPES + EBSERH Pessoal (IFES) — Período 2 (2023–2026)
-- Retorna: {ano, creditos_totais}
-- Regra 2026: UO usa dotacao_atualizada; Destaque, CAPES e EBSERH projetam 2025 × 1.0426
-- Parâmetros:
--   @id_uo_list         — filtro de IFES destino (id_unidade_orcamentaria), vazio = todas
--   @id_uo_list_source  — UOs fonte dos TEDs (MEC, INEP, etc.)
WITH combined_uo AS (
  SELECT * FROM `br-mec-segape.educacao_politica_tesouro.tesouro_orcamento_unidade_orcamentaria`
  UNION ALL
  SELECT ano, CAST(id_orgao_uge AS STRING), orgao_uge, CAST(id_unidade_orcamentaria AS STRING), unidade_orcamentaria,
         CAST(id_resultado_lei AS STRING), resultado_lei, CAST(id_funcao AS STRING), funcao,
         CAST(id_subfuncao AS STRING), subfuncao, CAST(id_programa AS STRING), programa,
         id_acao, acao, id_plano_orcamentario, plano_orcamentario,
         CAST(id_fonte AS STRING), fonte, CAST(id_grupo_despesa AS STRING), grupo_despesa,
         CAST(id_elemento AS STRING), elemento, ploa, loa, dotacao_atualizada, despesa_empenhada, data_ultima_atualizacao
  FROM `br-mec-segape-sandbox.projeto_segape_dmape_relat_automatico.ats_orc_redux_unidade_orcamentaria_2026`
),
combined_dest AS (
  SELECT * FROM `br-mec-segape.educacao_politica_tesouro.tesouro_orcamento_destaque_recebido_instituicao`
  UNION ALL
  SELECT ano, CAST(id_orgao_uge AS STRING), orgao_uge, CAST(id_unidade_orcamentaria AS STRING), unidade_orcamentaria,
         CAST(id_resultado_lei AS STRING), resultado_lei, CAST(id_funcao AS STRING), funcao,
         CAST(id_subfuncao AS STRING), subfuncao, CAST(id_programa AS STRING), programa,
         id_acao, acao, id_plano_orcamentario, plano_orcamentario,
         CAST(id_fonte AS STRING), fonte, CAST(id_grupo_despesa AS STRING), grupo_despesa,
         CAST(id_elemento AS STRING), elemento, destaque_recebido, despesa_empenhada, data_ultima_atualizacao
  FROM `br-mec-segape-sandbox.projeto_segape_dmape_relat_automatico.ats_orc_redux_destaque_recebido_2026`
),
dest_raw AS (
  SELECT t_dest.ano, SUM(t_dest.despesa_empenhada) AS valor
  FROM combined_dest AS t_dest
  JOIN `br-mec-segape.educacao_politica_tesouro.tesouro_orcamento_universidade_federal_grupo` AS t_grupo
    ON t_dest.id_orgao_uge = CAST(t_grupo.id_unidade_orcamentaria AS STRING)
  WHERE t_grupo.grupo_unidade_orcamentaria = 'Universidade'
    AND t_dest.id_unidade_orcamentaria IN UNNEST(@id_uo_list_source)
    AND (IFNULL(ARRAY_LENGTH(@id_uo_list), 0) = 0 OR CAST(t_grupo.id_unidade_orcamentaria AS STRING) IN UNNEST(@id_uo_list))
    AND t_dest.ano BETWEEN 2023 AND 2025
  GROUP BY t_dest.ano
),
dest_adj AS (
  SELECT ano, valor FROM dest_raw
  UNION ALL
  SELECT 2026, valor * 1.0426 FROM dest_raw WHERE ano = 2025
),
capes_raw AS (
  SELECT bc.ano, SUM(bc.despesa_paga) AS despesa_paga
  FROM `br-mec-segape-sandbox.projeto_segape_dmape_relat_automatico.ats_orc_redux_bolsas_capes` AS bc
  WHERE CAST(bc.id_unidade_orcamentaria AS STRING) LIKE '26%'
    AND (IFNULL(ARRAY_LENGTH(@id_uo_list), 0) = 0 OR CAST(bc.id_unidade_orcamentaria AS STRING) IN UNNEST(@id_uo_list))
    AND bc.ano BETWEEN 2023 AND 2025
  GROUP BY bc.ano
),
capes_adj AS (
  SELECT ano, despesa_paga FROM capes_raw
  UNION ALL
  SELECT 2026, despesa_paga * 1.0426 FROM capes_raw WHERE ano = 2025
),
ebserh_raw AS (
  SELECT eb.ano, SUM(eb.despesa_paga) AS despesa_paga
  FROM `br-mec-segape-sandbox.projeto_segape_dmape_relat_automatico.ats_orc_redux_ebserh_pessoal` AS eb
  WHERE eb.id_uo != 26443
    AND (IFNULL(ARRAY_LENGTH(@id_uo_list), 0) = 0 OR CAST(eb.id_uo AS STRING) IN UNNEST(@id_uo_list))
    AND eb.ano BETWEEN 2023 AND 2025
  GROUP BY eb.ano
),
ebserh_adj AS (
  SELECT ano, despesa_paga FROM ebserh_raw
  UNION ALL
  SELECT 2026, despesa_paga * 1.0426 FROM ebserh_raw WHERE ano = 2025
)
SELECT
  anos.ano,
  COALESCE(uo.despesa_empenhada, 0)
    + COALESCE(dest.valor, 0)
    + COALESCE(capes.despesa_paga, 0)
    + COALESCE(ebserh.despesa_paga, 0) AS creditos_totais
FROM (SELECT ano FROM UNNEST([2023, 2024, 2025, 2026]) AS ano) AS anos
LEFT JOIN (
  SELECT t_uo.ano, SUM(CASE WHEN t_uo.ano < 2026 THEN t_uo.despesa_empenhada ELSE t_uo.dotacao_atualizada END) AS despesa_empenhada
  FROM combined_uo AS t_uo
  JOIN `br-mec-segape.educacao_politica_tesouro.tesouro_orcamento_universidade_federal_grupo` AS t_grupo
    ON CAST(t_uo.id_unidade_orcamentaria AS INT64) = t_grupo.id_unidade_orcamentaria
  WHERE t_grupo.grupo_unidade_orcamentaria = 'Universidade'
    AND (IFNULL(ARRAY_LENGTH(@id_uo_list), 0) = 0 OR CAST(t_grupo.id_unidade_orcamentaria AS STRING) IN UNNEST(@id_uo_list))
    AND t_uo.ano BETWEEN 2023 AND 2026
  GROUP BY t_uo.ano
) AS uo ON uo.ano = anos.ano
LEFT JOIN dest_adj AS dest ON dest.ano = anos.ano
LEFT JOIN capes_adj AS capes ON capes.ano = anos.ano
LEFT JOIN ebserh_adj AS ebserh ON ebserh.ano = anos.ano
ORDER BY anos.ano
