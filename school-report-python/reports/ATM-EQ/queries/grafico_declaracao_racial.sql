WITH historico_ate_2024 AS (
  SELECT
    ano AS anoReferencia,
    COALESCE(SUM(quantidade_matricula_amarela), 0) AS amarela,
    COALESCE(SUM(quantidade_matricula_branca), 0) AS branca,
    COALESCE(SUM(quantidade_matricula_indigena), 0) AS indigena,
    COALESCE(SUM(quantidade_matricula_nao_declarada), 0) AS nao_declarada,
    COALESCE(SUM(quantidade_matricula_parda), 0) AS parda,
    COALESCE(SUM(quantidade_matricula_preta), 0) AS preta
  FROM `br-mec-segape.educacao_inep_dados_abertos.censo_escolar_escola`
  WHERE id_municipio = @cod_ibge
    AND tipo_situacao_funcionamento = '1'
    AND rede = '3'
  GROUP BY ano
),
base_2025 AS (
  SELECT
    2025 AS anoReferencia,
    COALESCE(SUM(m.quantidade_matricula_educacao_basica_cor_amarela), 0) AS amarela,
    COALESCE(SUM(m.quantidade_matricula_educacao_basica_cor_branca), 0) AS branca,
    COALESCE(SUM(m.quantidade_matricula_educacao_basica_indigena), 0) AS indigena,
    COALESCE(SUM(m.quantidade_matricula_educacao_basica_cor_nao_declarada), 0) AS nao_declarada,
    COALESCE(SUM(m.quantidade_matricula_educacao_basica_cor_parda), 0) AS parda,
    COALESCE(SUM(m.quantidade_matricula_educacao_basica_cor_preta), 0) AS preta
  FROM `br-mec-segape.educacao_inep_dados_abertos.inep_censo_escolar_educacao_basica_escola` e
  JOIN `br-mec-segape.educacao_inep_dados_abertos.inep_censo_escolar_educacao_basica_matricula` m
    ON m.ano = e.ano
   AND CAST(m.id_entidade AS STRING) = CAST(e.id_entidade AS STRING)
  WHERE e.ano = 2025
    AND CAST(e.id_municipio AS STRING) = @cod_ibge
    AND e.id_tipo_situacao_funcionamento = 1
    AND e.id_tipo_dependencia = 3
),
historico AS (
  SELECT * FROM historico_ate_2024
  UNION ALL
  SELECT * FROM base_2025
),
calc AS (
  SELECT
    anoReferencia,
    (amarela + branca + indigena + nao_declarada + parda + preta) AS total_raca_cor,
    nao_declarada
  FROM historico
)
SELECT
  anoReferencia,
  COALESCE(
    ROUND(
      100
      - SAFE_DIVIDE(nao_declarada, NULLIF(total_raca_cor, 0)) * 100,
      2
    ),
    0
  ) AS percentualDeclaracaoRacial
FROM calc
ORDER BY anoReferencia;
