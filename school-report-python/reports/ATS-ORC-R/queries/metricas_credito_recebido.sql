-- Métricas pré-calculadas para Crédito Recebido (P02–P07): TEDs + Bolsas CAPES + EBSERH Pessoal
-- P1 = 2019–2022 (Governo Bolsonaro, 4 anos)
-- P2 = 2023–2026 (Governo Lula, 4 anos)
-- Regra 2026: Destaque projeta 2025 × 1.0426; CAPES e EBSERH projetam 2025 × 1.0426
-- Parâmetros: @id_uo_list (source UOs), @id_orgao_uge_list (destination IFES)

WITH combined_dest AS (
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
    SUM(t_dest.despesa_empenhada) AS valor
  FROM combined_dest AS t_dest
  JOIN `br-mec-segape.educacao_politica_tesouro.tesouro_orcamento_universidade_federal_grupo` AS t_grupo
    ON t_dest.id_orgao_uge = CAST(t_grupo.id_unidade_orcamentaria AS STRING)
  WHERE
    t_grupo.grupo_unidade_orcamentaria = 'Universidade'
    AND t_dest.id_unidade_orcamentaria IN UNNEST(@id_uo_list)
    AND (IFNULL(ARRAY_LENGTH(@id_orgao_uge_list), 0) = 0 OR t_dest.id_orgao_uge IN UNNEST(@id_orgao_uge_list))
    AND t_dest.ano IN (2019, 2020, 2021, 2022, 2023, 2024, 2025)
  GROUP BY t_dest.ano
),
dest_adj AS (
  SELECT ano, valor FROM dest_raw
  UNION ALL
  SELECT 2026, valor * 1.0426 FROM dest_raw WHERE ano = 2025
),
capes_raw AS (
  SELECT bc.ano, SUM(bc.despesa_paga) AS valor
  FROM `br-mec-segape-sandbox.projeto_segape_dmape_relat_automatico.ats_orc_redux_bolsas_capes` AS bc
  WHERE CAST(bc.id_unidade_orcamentaria AS STRING) LIKE '26%'
    AND (IFNULL(ARRAY_LENGTH(@id_orgao_uge_list), 0) = 0 OR CAST(bc.id_unidade_orcamentaria AS STRING) IN UNNEST(@id_orgao_uge_list))
    AND bc.ano IN (2019, 2020, 2021, 2022, 2023, 2024, 2025)
  GROUP BY bc.ano
),
capes_adj AS (
  SELECT ano, valor FROM capes_raw
  UNION ALL
  SELECT 2026, valor * 1.0426 FROM capes_raw WHERE ano = 2025
),
ebserh_raw AS (
  SELECT eb.ano, SUM(eb.despesa_paga) AS valor
  FROM `br-mec-segape-sandbox.projeto_segape_dmape_relat_automatico.ats_orc_redux_ebserh_pessoal` AS eb
  WHERE eb.id_uo != 26443
    AND (IFNULL(ARRAY_LENGTH(@id_orgao_uge_list), 0) = 0 OR CAST(eb.id_uo AS STRING) IN UNNEST(@id_orgao_uge_list))
    AND eb.ano IN (2019, 2020, 2021, 2022, 2023, 2024, 2025)
  GROUP BY eb.ano
),
ebserh_adj AS (
  SELECT ano, valor FROM ebserh_raw
  UNION ALL
  SELECT 2026, valor * 1.0426 FROM ebserh_raw WHERE ano = 2025
)
SELECT
  anos.ano,
  COALESCE(d.valor, 0) + COALESCE(c.valor, 0) + COALESCE(e.valor, 0) AS valor
FROM (SELECT ano FROM UNNEST([2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]) AS ano) AS anos
LEFT JOIN dest_adj AS d ON d.ano = anos.ano
LEFT JOIN capes_adj AS c ON c.ano = anos.ano
LEFT JOIN ebserh_adj AS e ON e.ano = anos.ano
ORDER BY anos.ano
