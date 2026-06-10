SELECT
  'SESU'              AS secretaria,
  sigla_uf,
  instituicao,
  nome_empreendimento AS descricao_empreendimento,
  municipio_obra      AS municipio,
  valor_previsto
FROM `br-mec-segape.projeto_painel_ministro.painel_novopac_sesu`
WHERE id = '99'

UNION ALL

SELECT
  'SETEC'             AS secretaria,
  sigla_uf,
  instituicao,
  nome_empreendimento AS descricao_empreendimento,
  municipio_obra      AS municipio,
  valor_previsto
FROM `br-mec-segape.projeto_painel_ministro.painel_novopac_setec`
WHERE id = '99'
  AND categoria_resumido = 'Consolidação'

ORDER BY secretaria, sigla_uf, instituicao, municipio, descricao_empreendimento;