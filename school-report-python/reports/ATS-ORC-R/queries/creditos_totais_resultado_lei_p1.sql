-- P01 G3: Créditos Totais por Resultado Lei (UO + Destaque) — Período 1 (2019–2022)
-- Retorna: {ano, obrigatorio, discricionario, emendas}
-- Para 2022: destaque=0 por design (TEDs de 2022 foram para IFs, não IFES).
-- Parâmetros:
--   @id_uo_list         — filtro de IFES destino (id_unidade_orcamentaria), vazio = todas
--   @id_uo_list_source  — UOs fonte dos TEDs (MEC, INEP, etc.)
SELECT
  anos.ano,
  COALESCE(uo.obrigatorio, 0) + COALESCE(dest.obrigatorio, 0) AS obrigatorio,
  COALESCE(uo.discricionario, 0) + COALESCE(dest.discricionario, 0) AS discricionario,
  COALESCE(uo.emendas, 0) + COALESCE(dest.emendas, 0) AS emendas
FROM (SELECT ano FROM UNNEST([2019, 2020, 2021, 2022]) AS ano) AS anos
LEFT JOIN (
  SELECT
    t_uo.ano,
    SUM(CASE WHEN t_uo.id_resultado_lei IN ('0', '1') THEN t_uo.despesa_empenhada ELSE 0 END) AS obrigatorio,
    SUM(CASE WHEN t_uo.id_resultado_lei IN ('2', '3') THEN t_uo.despesa_empenhada ELSE 0 END) AS discricionario,
    SUM(CASE WHEN t_uo.id_resultado_lei IN ('6', '7', '8', '9') THEN t_uo.despesa_empenhada ELSE 0 END) AS emendas
  FROM `br-mec-segape.educacao_politica_tesouro.tesouro_orcamento_unidade_orcamentaria` AS t_uo
  JOIN `br-mec-segape.educacao_politica_tesouro.tesouro_orcamento_universidade_federal_grupo` AS t_grupo
    ON CAST(t_uo.id_unidade_orcamentaria AS INT64) = t_grupo.id_unidade_orcamentaria
  WHERE t_grupo.grupo_unidade_orcamentaria = 'Universidade'
    AND (IFNULL(ARRAY_LENGTH(@id_uo_list), 0) = 0 OR CAST(t_grupo.id_unidade_orcamentaria AS STRING) IN UNNEST(@id_uo_list))
    AND t_uo.ano BETWEEN 2019 AND 2022
  GROUP BY t_uo.ano
) AS uo ON uo.ano = anos.ano
LEFT JOIN (
  SELECT
    t_dest.ano,
    SUM(CASE WHEN t_dest.id_resultado_lei IN ('0', '1') THEN t_dest.despesa_empenhada ELSE 0 END) AS obrigatorio,
    SUM(CASE WHEN t_dest.id_resultado_lei IN ('2', '3') THEN t_dest.despesa_empenhada ELSE 0 END) AS discricionario,
    SUM(CASE WHEN t_dest.id_resultado_lei IN ('6', '7', '8', '9') THEN t_dest.despesa_empenhada ELSE 0 END) AS emendas
  FROM `br-mec-segape.educacao_politica_tesouro.tesouro_orcamento_destaque_recebido_instituicao` AS t_dest
  JOIN `br-mec-segape.educacao_politica_tesouro.tesouro_orcamento_universidade_federal_grupo` AS t_grupo
    ON t_dest.id_orgao_uge = CAST(t_grupo.id_unidade_orcamentaria AS STRING)
  WHERE t_grupo.grupo_unidade_orcamentaria = 'Universidade'
    AND t_dest.id_unidade_orcamentaria IN UNNEST(@id_uo_list_source)
    AND (IFNULL(ARRAY_LENGTH(@id_uo_list), 0) = 0 OR CAST(t_grupo.id_unidade_orcamentaria AS STRING) IN UNNEST(@id_uo_list))
    AND t_dest.ano BETWEEN 2019 AND 2022
  GROUP BY t_dest.ano
) AS dest ON dest.ano = anos.ano
ORDER BY anos.ano
