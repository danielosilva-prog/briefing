-- Resolve sigla da universidade para id_unidade_orcamentaria
-- Parâmetro: @sigla (STRING)
SELECT
  id_unidade_orcamentaria,
  unidade_orcamentaria AS nome_universidade,
  sigla
FROM `br-mec-segape.educacao_politica_tesouro.tesouro_orcamento_universidade_federal_grupo`
WHERE UPPER(sigla) = UPPER(@sigla)
LIMIT 1
