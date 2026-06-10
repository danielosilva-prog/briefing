-- P02 CE G3: Crédito Recebido — TEDs + Bolsas CAPES + EBSERH Pessoal (2019–2022)
-- Tabela: tesouro_orcamento_destaque_recebido_instituicao + bolsas_capes + ebserh_pessoal
-- Filtro: UO Grupo = 'Universidade' (via JOIN com tesouro_orcamento_universidade_federal_grupo)
-- Parâmetros: @id_uo_list (source UOs), @id_orgao_uge_list (destination IFES)
-- UNNEST garante sempre 4 anos (2019–2022), preenchendo zeros para anos sem dados
SELECT
  anos.ano,
  COALESCE(d.despesa_empenhada, 0)
    + COALESCE(capes.despesa_paga, 0)
    + COALESCE(ebserh.despesa_paga, 0) AS despesa_empenhada
FROM (SELECT ano FROM UNNEST([2019, 2020, 2021, 2022]) AS ano) AS anos
LEFT JOIN (
  SELECT
    t_dest.ano,
    SUM(t_dest.despesa_empenhada) AS despesa_empenhada
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
LEFT JOIN (
  SELECT bc.ano, SUM(bc.despesa_paga) AS despesa_paga
  FROM `br-mec-segape-sandbox.projeto_segape_dmape_relat_automatico.ats_orc_redux_bolsas_capes` AS bc
  WHERE CAST(bc.id_unidade_orcamentaria AS STRING) LIKE '26%'
    AND (IFNULL(ARRAY_LENGTH(@id_orgao_uge_list), 0) = 0 OR CAST(bc.id_unidade_orcamentaria AS STRING) IN UNNEST(@id_orgao_uge_list))
    AND bc.ano BETWEEN 2019 AND 2022
  GROUP BY bc.ano
) AS capes ON capes.ano = anos.ano
LEFT JOIN (
  SELECT eb.ano, SUM(eb.despesa_paga) AS despesa_paga
  FROM `br-mec-segape-sandbox.projeto_segape_dmape_relat_automatico.ats_orc_redux_ebserh_pessoal` AS eb
  WHERE eb.id_uo != 26443
    AND (IFNULL(ARRAY_LENGTH(@id_orgao_uge_list), 0) = 0 OR CAST(eb.id_uo AS STRING) IN UNNEST(@id_orgao_uge_list))
    AND eb.ano BETWEEN 2019 AND 2022
  GROUP BY eb.ano
) AS ebserh ON ebserh.ano = anos.ano
ORDER BY anos.ano
