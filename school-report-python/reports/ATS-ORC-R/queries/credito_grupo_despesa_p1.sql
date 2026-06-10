-- P02 G5: Grupo de Despesa — Pessoal/Custeio/Capital (2019–2022)
-- Para 2022: zeros esperados (TEDs de 2022 foram para IFs, não IFES) — correto por design.
-- Tabela: tesouro_orcamento_destaque_recebido_instituicao
-- Parâmetros: @id_uo_list (source UOs), @id_orgao_uge_list (destination IFES)
SELECT
  anos.ano,
  COALESCE(d.pessoal_encargos, 0) AS pessoal_encargos,
  COALESCE(d.custeio, 0) AS custeio,
  COALESCE(d.capital, 0) AS capital
FROM (SELECT ano FROM UNNEST([2019, 2020, 2021, 2022]) AS ano) AS anos
LEFT JOIN (
  SELECT
    t_dest.ano,
    SUM(CASE
      WHEN t_dest.id_grupo_despesa = '1' THEN t_dest.despesa_empenhada
      ELSE 0
    END) AS pessoal_encargos,
    SUM(CASE
      WHEN t_dest.id_grupo_despesa = '3' THEN t_dest.despesa_empenhada
      ELSE 0
    END) AS custeio,
    SUM(CASE
      WHEN t_dest.id_grupo_despesa IN ('4', '5') THEN t_dest.despesa_empenhada
      ELSE 0
    END) AS capital
  FROM `br-mec-segape.educacao_politica_tesouro.tesouro_orcamento_destaque_recebido_instituicao` AS t_dest
  JOIN `br-mec-segape.educacao_politica_tesouro.tesouro_orcamento_universidade_federal_grupo` AS t_grupo
    ON t_dest.id_orgao_uge = CAST(t_grupo.id_unidade_orcamentaria AS STRING)
  WHERE
    t_grupo.grupo_unidade_orcamentaria = 'Universidade'
    AND t_dest.id_unidade_orcamentaria IN UNNEST(@id_uo_list)
    AND (IFNULL(ARRAY_LENGTH(@id_orgao_uge_list), 0) = 0 OR t_dest.id_orgao_uge IN UNNEST(@id_orgao_uge_list))
    AND t_dest.ano BETWEEN 2019 AND 2022
  GROUP BY t_dest.ano
) AS d ON d.ano = anos.ano
ORDER BY anos.ano
