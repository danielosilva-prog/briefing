-- P01 G6: Créditos Totais por Grupo de Despesa (UO + Destaque) — Período 2 (2023–2026)
-- Retorna: {ano, pessoal_encargos, custeio, capital}
-- Regra 2026: UO usa dotacao_atualizada; Destaque projeta 2025 × 1.0426
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
  SELECT
    t_dest.ano,
    SUM(CASE WHEN t_dest.id_grupo_despesa = '1' THEN t_dest.despesa_empenhada ELSE 0 END) AS pessoal_encargos,
    SUM(CASE WHEN t_dest.id_grupo_despesa = '3' THEN t_dest.despesa_empenhada ELSE 0 END) AS custeio,
    SUM(CASE WHEN t_dest.id_grupo_despesa IN ('4', '5') THEN t_dest.despesa_empenhada ELSE 0 END) AS capital
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
  SELECT ano, pessoal_encargos, custeio, capital FROM dest_raw
  UNION ALL
  SELECT 2026, pessoal_encargos * 1.0426, custeio * 1.0426, capital * 1.0426
  FROM dest_raw WHERE ano = 2025
)
SELECT
  anos.ano,
  COALESCE(uo.pessoal_encargos, 0) + COALESCE(dest.pessoal_encargos, 0) AS pessoal_encargos,
  COALESCE(uo.custeio, 0) + COALESCE(dest.custeio, 0) AS custeio,
  COALESCE(uo.capital, 0) + COALESCE(dest.capital, 0) AS capital
FROM (SELECT ano FROM UNNEST([2023, 2024, 2025, 2026]) AS ano) AS anos
LEFT JOIN (
  SELECT
    t_uo.ano,
    SUM(CASE WHEN t_uo.id_grupo_despesa = '1' THEN (CASE WHEN t_uo.ano < 2026 THEN t_uo.despesa_empenhada ELSE t_uo.dotacao_atualizada END) ELSE 0 END) AS pessoal_encargos,
    SUM(CASE WHEN t_uo.id_grupo_despesa = '3' THEN (CASE WHEN t_uo.ano < 2026 THEN t_uo.despesa_empenhada ELSE t_uo.dotacao_atualizada END) ELSE 0 END) AS custeio,
    SUM(CASE WHEN t_uo.id_grupo_despesa IN ('4', '5') THEN (CASE WHEN t_uo.ano < 2026 THEN t_uo.despesa_empenhada ELSE t_uo.dotacao_atualizada END) ELSE 0 END) AS capital
  FROM combined_uo AS t_uo
  JOIN `br-mec-segape.educacao_politica_tesouro.tesouro_orcamento_universidade_federal_grupo` AS t_grupo
    ON CAST(t_uo.id_unidade_orcamentaria AS INT64) = t_grupo.id_unidade_orcamentaria
  WHERE t_grupo.grupo_unidade_orcamentaria = 'Universidade'
    AND (IFNULL(ARRAY_LENGTH(@id_uo_list), 0) = 0 OR CAST(t_grupo.id_unidade_orcamentaria AS STRING) IN UNNEST(@id_uo_list))
    AND t_uo.ano BETWEEN 2023 AND 2026
  GROUP BY t_uo.ano
) AS uo ON uo.ano = anos.ano
LEFT JOIN dest_adj AS dest ON dest.ano = anos.ano
ORDER BY anos.ano
