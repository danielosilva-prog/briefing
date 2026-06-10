-- P01 G5: Grupo de Despesa — Pessoal/Custeio/Capital (2019–2022)
-- Tabela: tesouro_orcamento_unidade_orcamentaria
-- Filtro: uo_grupo = 'Universidade'
-- Parâmetro opcional: @id_uo_list (ARRAY<STRING>) - se fornecido e não vazio, filtra para essas instituições
SELECT
  anos.ano,
  COALESCE(d.pessoal_encargos, 0) AS pessoal_encargos,
  COALESCE(d.custeio, 0) AS custeio,
  COALESCE(d.capital, 0) AS capital
FROM (SELECT ano FROM UNNEST([2019, 2020, 2021, 2022]) AS ano) AS anos
LEFT JOIN (
  SELECT
    t_uo.ano,
    SUM(CASE
      WHEN t_uo.id_grupo_despesa = '1' THEN t_uo.despesa_empenhada
      ELSE 0
    END) AS pessoal_encargos,
    SUM(CASE
      WHEN t_uo.id_grupo_despesa = '3' THEN t_uo.despesa_empenhada
      ELSE 0
    END) AS custeio,
    SUM(CASE
      WHEN t_uo.id_grupo_despesa IN ('4', '5') THEN t_uo.despesa_empenhada
      ELSE 0
    END) AS capital
  FROM `br-mec-segape.educacao_politica_tesouro.tesouro_orcamento_unidade_orcamentaria` AS t_uo
  JOIN `br-mec-segape.educacao_politica_tesouro.tesouro_orcamento_universidade_federal_grupo` AS t_grupo
    ON CAST(t_uo.id_unidade_orcamentaria AS INT64) = t_grupo.id_unidade_orcamentaria
  WHERE
    t_grupo.grupo_unidade_orcamentaria = 'Universidade'
    AND (IFNULL(ARRAY_LENGTH(@id_uo_list), 0) = 0 OR CAST(t_grupo.id_unidade_orcamentaria AS STRING) IN UNNEST(@id_uo_list))
    AND t_uo.ano BETWEEN 2019 AND 2022
  GROUP BY t_uo.ano
) AS d ON d.ano = anos.ano
ORDER BY anos.ano
