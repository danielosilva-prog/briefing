-- Busca nome da universidade pelo id_unidade_orcamentaria
-- Parâmetro: @id_unidade_orcamentaria (INT64)
SELECT
  id_unidade_orcamentaria,
  unidade_orcamentaria AS nome_universidade
FROM `br-mec-segape.educacao_politica_tesouro.tesouro_orcamento_universidade_federal_grupo`
WHERE id_unidade_orcamentaria = @id_unidade_orcamentaria
LIMIT 1
