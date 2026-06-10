WITH escolas_base AS (
  SELECT
    ano,
    CAST(id_municipio AS STRING) AS cod_ibge,
    CAST(id_entidade AS STRING) AS id_entidade,
    CAST(id_tipo_localizacao_diferenciada AS STRING) AS tipo_localizacao_diferenciada
  FROM `br-mec-segape.educacao_inep_dados_abertos.inep_censo_escolar_educacao_basica_escola`
  WHERE ano = 2025
    AND CAST(id_municipio AS STRING) = @cod_ibge
    AND id_tipo_dependencia = 3
    AND id_tipo_situacao_funcionamento = 1
),
matriculas_base AS (
  SELECT
    ano,
    CAST(id_entidade AS STRING) AS id_entidade,
    COALESCE(quantidade_matricula_educacao_basica, 0) AS total_matriculas,
    COALESCE(quantidade_matricula_educacao_basica_cor_amarela, 0) AS amarela,
    COALESCE(quantidade_matricula_educacao_basica_cor_branca, 0) AS branca,
    COALESCE(quantidade_matricula_educacao_basica_indigena, 0) AS indigena,
    COALESCE(quantidade_matricula_educacao_basica_cor_nao_declarada, 0) AS nao_declarada,
    COALESCE(quantidade_matricula_educacao_basica_cor_parda, 0) AS parda,
    COALESCE(quantidade_matricula_educacao_basica_cor_preta, 0) AS preta
  FROM `br-mec-segape.educacao_inep_dados_abertos.inep_censo_escolar_educacao_basica_matricula`
  WHERE ano = 2025
),
base AS (
  SELECT
    e.cod_ibge,
    m.total_matriculas,
    m.amarela,
    m.branca,
    m.indigena,
    m.nao_declarada,
    m.parda,
    m.preta,
    IF(e.tipo_localizacao_diferenciada = "3", m.total_matriculas, 0) AS quilombola
  FROM escolas_base e
  JOIN matriculas_base m
    ON m.ano = e.ano
   AND m.id_entidade = e.id_entidade
),
agregados AS (
  SELECT
    cod_ibge,
    SUM(total_matriculas) AS total_matriculas,
    SUM(amarela) AS amarela,
    SUM(branca) AS branca,
    SUM(indigena) AS indigena,
    SUM(nao_declarada) AS nao_declarada,
    SUM(parda) AS parda,
    SUM(preta) AS preta,
    SUM(quilombola) AS quilombola,
    -- Denominador das categorias raciais (igual ao gráfico de declaração racial)
    SUM(amarela + branca + indigena + nao_declarada + parda + preta) AS total_raca_cor
  FROM base
  GROUP BY cod_ibge
)
SELECT
  categoria,
  quantidade,
  CASE
    WHEN categoria = "Quilombola"
      THEN COALESCE(ROUND(SAFE_DIVIDE(quantidade, NULLIF(total_matriculas, 0)) * 100, 2), 0)
    ELSE COALESCE(ROUND(SAFE_DIVIDE(quantidade, NULLIF(total_raca_cor,    0)) * 100, 2), 0)
  END AS percentual,
  2025 AS anoReferencia
FROM agregados,
UNNEST([
  STRUCT("Amarela" AS categoria, amarela AS quantidade),
  STRUCT("Branca" AS categoria, branca AS quantidade),
  STRUCT("Indígena" AS categoria, indigena AS quantidade),
  STRUCT("Não declarada" AS categoria, nao_declarada AS quantidade),
  STRUCT("Parda" AS categoria, parda AS quantidade),
  STRUCT("Preta" AS categoria, preta AS quantidade),
  STRUCT("Quilombola" AS categoria, quilombola AS quantidade)
])
ORDER BY
  CASE categoria
    WHEN "Amarela" THEN 1
    WHEN "Branca" THEN 2
    WHEN "Indígena" THEN 3
    WHEN "Não declarada" THEN 4
    WHEN "Parda" THEN 5
    WHEN "Preta" THEN 6
    WHEN "Quilombola" THEN 7
    ELSE 99
  END;
