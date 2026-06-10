WITH censo_escola_2025 AS (
  SELECT
    CAST(e.id_municipio AS STRING) AS cod_ibge,
    CAST(e.id_entidade AS STRING) AS id_escola,
    CAST(e.id_tipo_situacao_funcionamento AS STRING) AS tipo_situacao_funcionamento,
    CAST(e.id_tipo_dependencia AS STRING) AS rede,
    CAST(e.id_tipo_localizacao_diferenciada AS STRING) AS tipo_localizacao_diferenciada,
    COALESCE(m.quantidade_matricula_educacao_basica_cor_branca, 0) AS quantidade_matricula_branca,
    COALESCE(m.quantidade_matricula_educacao_basica_cor_preta, 0) AS quantidade_matricula_preta,
    COALESCE(m.quantidade_matricula_educacao_basica_cor_parda, 0) AS quantidade_matricula_parda,
    COALESCE(m.quantidade_matricula_educacao_basica_indigena, 0) AS quantidade_matricula_indigena
  FROM `br-mec-segape.educacao_inep_dados_abertos.inep_censo_escolar_educacao_basica_escola` e
  JOIN `br-mec-segape.educacao_inep_dados_abertos.inep_censo_escolar_educacao_basica_matricula` m
    ON m.ano = e.ano
   AND CAST(m.id_entidade AS STRING) = CAST(e.id_entidade AS STRING)
  WHERE e.ano = 2025
    AND CAST(e.id_municipio AS STRING) = @cod_ibge
),
base_escola AS (
  SELECT
    CASE
      WHEN CAST(c.tipo_localizacao_diferenciada AS STRING) = '3' THEN 'Quilombola'
      WHEN SAFE_DIVIDE(
        COALESCE(c.quantidade_matricula_preta, 0)
        + COALESCE(c.quantidade_matricula_parda, 0)
        + COALESCE(c.quantidade_matricula_indigena, 0),
        NULLIF(
          COALESCE(c.quantidade_matricula_branca, 0)
          + COALESCE(c.quantidade_matricula_preta, 0)
          + COALESCE(c.quantidade_matricula_parda, 0)
          + COALESCE(c.quantidade_matricula_indigena, 0),
          0
        )
      ) >= 0.6 THEN 'PPI >= 60%'
      ELSE 'PPI < 60%'
    END AS grupoEscola,
    ROUND(a.educacao_infantil_grupo_1, 2) AS infantil_grupo_1,
    ROUND(a.educacao_infantil_grupo_2, 2) AS infantil_grupo_2,
    ROUND(a.educacao_infantil_grupo_3, 2) AS infantil_grupo_3,
    ROUND(a.ensino_fundamental_anos_iniciais_grupo_1, 2) AS anos_iniciais_grupo_1,
    ROUND(a.ensino_fundamental_anos_iniciais_grupo_2, 2) AS anos_iniciais_grupo_2,
    ROUND(a.ensino_fundamental_anos_iniciais_grupo_3, 2) AS anos_iniciais_grupo_3
  FROM `br-mec-segape.educacao_inep_dados_abertos.inep_adequacao_formacao_docente_escola` a
  JOIN censo_escola_2025 c
    ON c.id_escola = CAST(a.id_escola AS STRING)
  WHERE CAST(a.id_municipio AS STRING) = @cod_ibge
    AND a.ano_censo = 2025
    AND c.cod_ibge = @cod_ibge
    AND c.tipo_situacao_funcionamento = '1'
    AND c.rede = '3'
    AND (
      CAST(c.tipo_localizacao_diferenciada AS STRING) = '3'
      OR (
        COALESCE(c.quantidade_matricula_branca, 0)
        + COALESCE(c.quantidade_matricula_preta, 0)
        + COALESCE(c.quantidade_matricula_parda, 0)
        + COALESCE(c.quantidade_matricula_indigena, 0)
      ) > 0
    )
),
agregado AS (
  SELECT
    grupoEscola,
    ROUND(AVG(COALESCE(infantil_grupo_1, 0) + COALESCE(infantil_grupo_2, 0) + COALESCE(infantil_grupo_3, 0)), 2)
      AS percentualEdInfantilAdequada,
    ROUND(AVG(
      COALESCE(anos_iniciais_grupo_1, 0)
      + COALESCE(anos_iniciais_grupo_2, 0)
      + COALESCE(anos_iniciais_grupo_3, 0)
    ), 2) AS percentualAnosIniciaisAdequada
  FROM base_escola
  GROUP BY grupoEscola
)
SELECT
  grupoEscola,
  percentualEdInfantilAdequada,
  percentualAnosIniciaisAdequada,
  2025 AS anoReferencia
FROM agregado
ORDER BY
  CASE grupoEscola
    WHEN 'PPI >= 60%' THEN 1
    WHEN 'PPI < 60%' THEN 2
    WHEN 'Quilombola' THEN 3
    ELSE 99
  END;
