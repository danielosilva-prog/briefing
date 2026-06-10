-- P01 G4: Resultado Lei — Obrigatório/Discricionário/Emendas (2023–2026)
-- Tabela: tesouro_orcamento_unidade_orcamentaria + sandbox 2026
-- Filtro: uo_grupo = 'Universidade'
-- Parâmetro opcional: @id_uo_list (ARRAY<STRING>) - se fornecido e não vazio, filtra para essas instituições
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
)
SELECT
  t_uo.ano,
  SUM(CASE
    WHEN t_uo.id_resultado_lei IN ('0', '1') THEN (CASE WHEN t_uo.ano < 2026 THEN t_uo.despesa_empenhada ELSE t_uo.dotacao_atualizada END)
    ELSE 0
  END) AS obrigatorio,
  SUM(CASE
    WHEN t_uo.id_resultado_lei IN ('2', '3') THEN (CASE WHEN t_uo.ano < 2026 THEN t_uo.despesa_empenhada ELSE t_uo.dotacao_atualizada END)
    ELSE 0
  END) AS discricionario,
  SUM(CASE
    WHEN t_uo.id_resultado_lei IN ('6', '7', '8', '9') THEN (CASE WHEN t_uo.ano < 2026 THEN t_uo.despesa_empenhada ELSE t_uo.dotacao_atualizada END)
    ELSE 0
  END) AS emendas
FROM combined_uo AS t_uo
JOIN `br-mec-segape.educacao_politica_tesouro.tesouro_orcamento_universidade_federal_grupo` AS t_grupo
  ON CAST(t_uo.id_unidade_orcamentaria AS INT64) = t_grupo.id_unidade_orcamentaria
WHERE
  t_grupo.grupo_unidade_orcamentaria = 'Universidade'
  AND (IFNULL(ARRAY_LENGTH(@id_uo_list), 0) = 0 OR CAST(t_grupo.id_unidade_orcamentaria AS STRING) IN UNNEST(@id_uo_list))
  AND t_uo.ano BETWEEN 2023 AND 2026
GROUP BY t_uo.ano
ORDER BY t_uo.ano
