-- P01 G5: Créditos Totais por Grupo de Despesa (UO + Destaque) — Período 1 (2019–2022)
-- Retorna: {ano, pessoal_encargos, custeio, capital}
-- Para 2022: destaque=0 por design (TEDs de 2022 foram para IFs, não IFES).
-- Parâmetros:
--   @id_uo_list         — filtro de IFES destino (id_unidade_orcamentaria), vazio = todas
--   @id_uo_list_source  — UOs fonte dos TEDs (MEC, INEP, etc.)
SELECT
  anos.ano,
  COALESCE(uo.pessoal_encargos, 0) + COALESCE(dest.pessoal_encargos, 0) AS pessoal_encargos,
  COALESCE(uo.custeio, 0) + COALESCE(dest.custeio, 0) AS custeio,
  COALESCE(uo.capital, 0) + COALESCE(dest.capital, 0) AS capital
FROM (SELECT ano FROM UNNEST([2019, 2020, 2021, 2022]) AS ano) AS anos
LEFT JOIN (
  SELECT
    t_uo.ano,
    SUM(CASE WHEN t_uo.id_grupo_despesa = '1' THEN t_uo.despesa_empenhada ELSE 0 END) AS pessoal_encargos,
    SUM(CASE WHEN t_uo.id_grupo_despesa = '3' THEN t_uo.despesa_empenhada ELSE 0 END) AS custeio,
    SUM(CASE WHEN t_uo.id_grupo_despesa IN ('4', '5') THEN t_uo.despesa_empenhada ELSE 0 END) AS capital
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
    SUM(CASE WHEN t_dest.id_grupo_despesa = '1' THEN t_dest.despesa_empenhada ELSE 0 END) AS pessoal_encargos,
    SUM(CASE WHEN t_dest.id_grupo_despesa = '3' THEN t_dest.despesa_empenhada ELSE 0 END) AS custeio,
    SUM(CASE WHEN t_dest.id_grupo_despesa IN ('4', '5') THEN t_dest.despesa_empenhada ELSE 0 END) AS capital
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
