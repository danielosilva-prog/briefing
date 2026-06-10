-- P02 G1: Créditos Totais = UO + Destaque + Bolsas CAPES + EBSERH Pessoal (IFES) — Período 1 (2019–2022)
-- Retorna: {ano, creditos_totais}
-- Para 2022: destaque=0 (TEDs de 2022 foram para IFs, não IFES) — correto por design.
-- Parâmetros:
--   @id_uo_list         — filtro de IFES destino (id_unidade_orcamentaria), vazio = todas
--   @id_uo_list_source  — UOs fonte dos TEDs (MEC, INEP, etc.)
SELECT
  anos.ano,
  COALESCE(uo.despesa_empenhada, 0)
    + COALESCE(dest.destaque_recebido, 0)
    + COALESCE(capes.despesa_paga, 0)
    + COALESCE(ebserh.despesa_paga, 0) AS creditos_totais
FROM (SELECT ano FROM UNNEST([2019, 2020, 2021, 2022]) AS ano) AS anos
LEFT JOIN (
  SELECT t_uo.ano, SUM(t_uo.despesa_empenhada) AS despesa_empenhada
  FROM `br-mec-segape.educacao_politica_tesouro.tesouro_orcamento_unidade_orcamentaria` AS t_uo
  JOIN `br-mec-segape.educacao_politica_tesouro.tesouro_orcamento_universidade_federal_grupo` AS t_grupo
    ON CAST(t_uo.id_unidade_orcamentaria AS INT64) = t_grupo.id_unidade_orcamentaria
  WHERE t_grupo.grupo_unidade_orcamentaria = 'Universidade'
    AND (IFNULL(ARRAY_LENGTH(@id_uo_list), 0) = 0 OR CAST(t_grupo.id_unidade_orcamentaria AS STRING) IN UNNEST(@id_uo_list))
    AND t_uo.ano BETWEEN 2019 AND 2022
  GROUP BY t_uo.ano
) AS uo ON uo.ano = anos.ano
LEFT JOIN (
  SELECT t_dest.ano, SUM(t_dest.despesa_empenhada) AS destaque_recebido
  FROM `br-mec-segape.educacao_politica_tesouro.tesouro_orcamento_destaque_recebido_instituicao` AS t_dest
  JOIN `br-mec-segape.educacao_politica_tesouro.tesouro_orcamento_universidade_federal_grupo` AS t_grupo
    ON t_dest.id_orgao_uge = CAST(t_grupo.id_unidade_orcamentaria AS STRING)
  WHERE t_grupo.grupo_unidade_orcamentaria = 'Universidade'
    AND t_dest.id_unidade_orcamentaria IN UNNEST(@id_uo_list_source)
    AND (IFNULL(ARRAY_LENGTH(@id_uo_list), 0) = 0 OR CAST(t_grupo.id_unidade_orcamentaria AS STRING) IN UNNEST(@id_uo_list))
    AND t_dest.ano BETWEEN 2019 AND 2022
  GROUP BY t_dest.ano
) AS dest ON dest.ano = anos.ano
LEFT JOIN (
  SELECT bc.ano, SUM(bc.despesa_paga) AS despesa_paga
  FROM `br-mec-segape-sandbox.projeto_segape_dmape_relat_automatico.ats_orc_redux_bolsas_capes` AS bc
  WHERE CAST(bc.id_unidade_orcamentaria AS STRING) LIKE '26%'
    AND (IFNULL(ARRAY_LENGTH(@id_uo_list), 0) = 0 OR CAST(bc.id_unidade_orcamentaria AS STRING) IN UNNEST(@id_uo_list))
    AND bc.ano BETWEEN 2019 AND 2022
  GROUP BY bc.ano
) AS capes ON capes.ano = anos.ano
LEFT JOIN (
  SELECT eb.ano, SUM(eb.despesa_paga) AS despesa_paga
  FROM `br-mec-segape-sandbox.projeto_segape_dmape_relat_automatico.ats_orc_redux_ebserh_pessoal` AS eb
  WHERE eb.id_uo != 26443
    AND (IFNULL(ARRAY_LENGTH(@id_uo_list), 0) = 0 OR CAST(eb.id_uo AS STRING) IN UNNEST(@id_uo_list))
    AND eb.ano BETWEEN 2019 AND 2022
  GROUP BY eb.ano
) AS ebserh ON ebserh.ano = anos.ano
ORDER BY anos.ano
