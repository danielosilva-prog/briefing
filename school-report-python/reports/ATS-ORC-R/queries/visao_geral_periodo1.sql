-- P01 G1: Visão Geral — Despesa Empenhada (2019–2022)
-- Tabela: tesouro_orcamento_unidade_orcamentaria
-- Filtro: uo_grupo = 'Universidade'
-- Parâmetro opcional: @id_uo_list (ARRAY<STRING>) - se fornecido e não vazio, filtra para essas instituições
SELECT
  anos.ano,
  COALESCE(d.despesa_empenhada, 0) AS despesa_empenhada
FROM (SELECT ano FROM UNNEST([2019, 2020, 2021, 2022]) AS ano) AS anos
LEFT JOIN (
  SELECT
    t_uo.ano,
    SUM(t_uo.despesa_empenhada) AS despesa_empenhada
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
