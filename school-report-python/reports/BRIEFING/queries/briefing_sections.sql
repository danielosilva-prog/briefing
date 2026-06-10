SELECT
  1 AS ordem,
  '1.1' AS numero,
  'ESCOLAS CONECTADAS' AS titulo,
  [
    STRUCT('Escolas Conectadas (Nível 4 e 5)' AS rotulo, '2.934 (78,8%)' AS valor, CAST(NULL AS STRING) AS complemento)
  ] AS indicadores
UNION ALL
SELECT
  2,
  '1.2',
  'ESCOLA EM TEMPO INTEGRAL (2023-2025)',
  [
    STRUCT('Matrículas fomentadas', '29.811', NULL),
    STRUCT('Valor fomentado', 'R$ 186,8 milhões', NULL)
  ]
UNION ALL
SELECT
  3,
  '1.3',
  'COMPROMISSO NACIONAL CRIANÇA ALFABETIZADA',
  [
    STRUCT('Cantinho de Leitura', '3.693', NULL),
    STRUCT('Escolas Apoiadas', '2.128', NULL),
    STRUCT('Valor Investido em Cantinhos da Leitura', 'R$ 4,56 milhões', NULL),
    STRUCT('Articuladores RENALFA (2025)', '267', NULL),
    STRUCT('Repasse para Articuladores RENALFA', 'R$ 9,02 milhões', NULL),
    STRUCT('Valor empenhado para aquisição de materiais', 'R$ 4,62 milhões', NULL),
    STRUCT('Valor empenhado para formação de profissionais da educação', 'R$ 26 mi', NULL),
    STRUCT('TOTAL INVESTIDO', 'R$ 44,20 milhões', NULL)
  ]
