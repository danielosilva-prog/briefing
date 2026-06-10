WITH max_ano_ref AS (
  SELECT MAX(r.ano) AS ano_ref
  FROM `br-mec-segape.educacao_inep_dados_abertos.inep_rendimento_escolar_escola` r
  WHERE CAST(r.id_municipio AS STRING) = @cod_ibge
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
    ROUND(r.taxa_aprovacao_ensino_fundamental_anos_iniciais, 2) AS taxaAprovacaoAnosIniciais,
    ROUND(r.taxa_aprovacao_ensino_fundamental_anos_finais, 2) AS taxaAprovacaoAnosFinais
  FROM `br-mec-segape.educacao_inep_dados_abertos.inep_rendimento_escolar_escola` r
  JOIN max_ano_ref m
    ON m.ano_ref = r.ano
  JOIN `br-mec-segape.educacao_inep_dados_abertos.censo_escolar_escola` c
    ON c.ano = r.ano
   AND CAST(c.id_escola AS STRING) = CAST(r.id_escola AS STRING)
  WHERE CAST(r.id_municipio AS STRING) = @cod_ibge
    AND CAST(c.id_municipio AS STRING) = @cod_ibge
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
    ROUND(AVG(taxaAprovacaoAnosIniciais), 2) AS taxaAprovacaoAnosIniciais,
    ROUND(AVG(taxaAprovacaoAnosFinais), 2) AS taxaAprovacaoAnosFinais
  FROM base_escola
  GROUP BY grupoEscola
)
SELECT
  grupoEscola,
  taxaAprovacaoAnosIniciais,
  taxaAprovacaoAnosFinais,
  (SELECT ano_ref FROM max_ano_ref) AS anoReferencia
FROM agregado
ORDER BY
  CASE grupoEscola
    WHEN 'PPI >= 60%' THEN 1
    WHEN 'PPI < 60%' THEN 2
    WHEN 'Quilombola' THEN 3
    ELSE 99
  END;
