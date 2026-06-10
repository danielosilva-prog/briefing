WITH ano_referencia AS (
  SELECT
    MAX(ano) AS ano
  FROM `br-mec-segape.educacao_politica_fundeb.fundeb_resultado_condicionalidade_iii_vaar`
  WHERE CAST(id_localidade AS STRING) = @cod_ibge
),
mapeamento_motivos AS (
  SELECT
    "Não reduziu a desigualdade racial e socioeconômica." AS motivo,
    "Não reduziu a desigualdade racial" AS reduziuDesigualdadeRacial,
    "Não reduziu a desigualdade socioeconômica" AS reduziuDesigualdadeSocioeconomica
  UNION ALL
  SELECT
    "Habilitado porque reduziu a desigualdade racial e socioeconômica.",
    "Reduziu a desigualdade racial",
    "Reduziu a desigualdade socioeconômica"
  UNION ALL
  SELECT
    "Não reduziu a desigualdade socioeconômica.",
    "Reduziu a desigualdade racial",
    "Não reduziu a desigualdade socioeconômica"
  UNION ALL
  SELECT
    "Habilitado porque reduziu a desigualdade socioeconômica e apresentou IDPPI_aj ajustado igual a zero (incluído na margem de erro).",
    "Desigualdade racial estável",
    "Reduziu a desigualdade socioeconômica"
  UNION ALL
  SELECT
    "Não reduziu a desigualdade racial.",
    "Não reduziu a desigualdade racial",
    "Reduziu a desigualdade socioeconômica"
  UNION ALL
  SELECT
    "Habilitado porque reduziu a desigualdade racial e apresentou IDNSE_aj ajustado igual a zero (incluído na margem de erro).",
    "Reduziu a desigualdade racial",
    "Desigualdade socioeconômica estável"
  UNION ALL
  SELECT
    "Habilitado porque apresentou IDPPI_aj ajustado e IDNSE_aj ajustado iguais a zero (incluído na margem de erro).",
    "Desigualdade racial estável",
    "Desigualdade socioeconômica estável"
  UNION ALL
  SELECT
    "Habilitado automaticamente por ausência de dados do Saeb 2019.",
    "Ausência de dados suficientes",
    "Ausência de dados suficientes"
  UNION ALL
  SELECT
    "Habilitado porque apresentou IDPPI_aj ajustado igual a zero (incluído na margem de erro). Não avaliado no IDNSE por insuficiência de dados (N < 10 no grupo).",
    "Desigualdade racial estável",
    "Ausência de dados suficientes"
  UNION ALL
  SELECT
    "Habilitado porque reduziu a desigualdade racial e não aumentou a desigualdade socioeconômica.",
    "Reduziu a desigualdade racial",
    "Desigualdade socioeconômica estável"
  UNION ALL
  SELECT
    "Habilitado automaticamente por ausência de dados do Saeb 2019 e Saeb 2023.",
    "Ausência de dados suficientes",
    "Ausência de dados suficientes"
  UNION ALL
  SELECT
    "Habilitado automaticamente por insuficiência de dados para o cálculo do IDPPI e IDNSE  (N < 10 nos grupos racial e socioeconômico).",
    "Ausência de dados suficientes",
    "Ausência de dados suficientes"
  UNION ALL
  SELECT
    "Habilitado porque reduziu a desigualdade racial. Não avaliado no IDNSE por insuficiência de dados (N < 10 no grupo).",
    "Reduziu a desigualdade racial",
    "Ausência de dados suficientes"
  UNION ALL
  SELECT
    "Habilitado porque apresentou IDNSE_aj ajustado igual a zero (incluído na margem de erro). Não avaliado no IDPPI por insuficiência de dados (N < 10 no grupo).",
    "Ausência de dados suficientes",
    "Desigualdade socioeconômica estável"
  UNION ALL
  SELECT
    "Habilitado automaticamente por ausência de dados do Saeb 2023.",
    "Ausência de dados suficientes",
    "Ausência de dados suficientes"
  UNION ALL
  SELECT
    "Habilitado porque reduziu a desigualdade socioeconômica. Não avaliado no IDPPI por insuficiência de dados (N < 10 no grupo).",
    "Ausência de dados suficientes",
    "Reduziu a desigualdade socioeconômica"
  UNION ALL
  SELECT
    "Habilitado porque reduziu a desigualdade socioeconômica e não aumentou a desigualdade racial.",
    "Desigualdade racial estável",
    "Reduziu a desigualdade socioeconômica"
  UNION ALL
  SELECT
    "Habilitado porque não aumentou a desigualdade socioeconômica. Não avaliado no IDPPI por insuficiência de dados (N < 10 no grupo).",
    "Ausência de dados suficientes",
    "Desigualdade socioeconômica estável"
),
base AS (
  SELECT *
  FROM `br-mec-segape.educacao_politica_fundeb.fundeb_resultado_condicionalidade_iii_vaar`
  WHERE CAST(id_localidade AS STRING) = @cod_ibge
    AND ano = (SELECT ano FROM ano_referencia)
),
base_com_margem AS (
  SELECT
    base.*,
    CASE
      WHEN base.numero_medio_estudante_saeb_2019_2023 IS NULL THEN NULL
      WHEN base.numero_medio_estudante_saeb_2019_2023 > 10000 THEN "Grupo 1"
      WHEN base.numero_medio_estudante_saeb_2019_2023 > 1000 THEN "Grupo 2"
      WHEN base.numero_medio_estudante_saeb_2019_2023 > 500 THEN "Grupo 3"
      WHEN base.numero_medio_estudante_saeb_2019_2023 > 200 THEN "Grupo 4"
      WHEN base.numero_medio_estudante_saeb_2019_2023 > 100 THEN "Grupo 5"
      ELSE "Grupo 6"
    END AS grupo_margem_erro,
    CASE
      WHEN base.numero_medio_estudante_saeb_2019_2023 IS NULL THEN NULL
      WHEN base.numero_medio_estudante_saeb_2019_2023 > 10000 THEN -0.010
      WHEN base.numero_medio_estudante_saeb_2019_2023 > 1000 THEN -0.025
      WHEN base.numero_medio_estudante_saeb_2019_2023 > 500 THEN -0.050
      WHEN base.numero_medio_estudante_saeb_2019_2023 > 200 THEN -0.075
      WHEN base.numero_medio_estudante_saeb_2019_2023 > 100 THEN -0.100
      ELSE -0.150
    END AS limite_inferior_margem_erro
  FROM base
)
SELECT
  CAST((SELECT ano FROM ano_referencia) AS STRING) AS p3AnoReferencia,
  base.total_estudante_saeb_2019 AS p3TotalEstudantesSaeb2019,
  base.total_estudante_saeb_2023 AS p3TotalEstudantesSaeb2023,
  base.numero_medio_estudante_saeb_2019_2023 AS p3NumeroMedioEstudantesSaeb2019_2023,
  base.grupo_margem_erro AS p3GrupoMargemErro,
  base.limite_inferior_margem_erro AS p3LimiteInferiorMargemErro,
  IF(base.limite_inferior_margem_erro IS NULL, NULL, 0.0) AS p3LimiteSuperiorMargemErro,
  CASE
    WHEN base.limite_inferior_margem_erro IS NULL THEN ""
    ELSE CONCAT(
      REPLACE(FORMAT("%.2f", 100 * base.limite_inferior_margem_erro), ".", ","),
      "%"
    )
  END AS p3MargemErroPercentual,
  base.total_estudante_ppi_saeb_2019 AS p3TotalEstudantesPpiSaeb2019,
  base.total_estudante_ppi_saeb_2023 AS p3TotalEstudantesPpiSaeb2023,
  CASE
    WHEN base.proporcao_estudante_ppi_desempenho_adequado_saeb_2019 IS NULL THEN "-%"
    ELSE CONCAT(
      REPLACE(FORMAT("%.2f", 100 * base.proporcao_estudante_ppi_desempenho_adequado_saeb_2019), ".", ","),
      "%"
    )
  END AS p3PercentualRacial2019,
  CASE
    WHEN base.proporcao_estudante_ppi_desempenho_adequado_saeb_2023 IS NULL THEN "-%"
    ELSE CONCAT(
      REPLACE(FORMAT("%.2f", 100 * base.proporcao_estudante_ppi_desempenho_adequado_saeb_2023), ".", ","),
      "%"
    )
  END AS p3PercentualRacial2023,
  CASE
    WHEN base.proporcao_estudante_ppi_desempenho_adequado_saeb_2019 IS NULL
      OR base.proporcao_estudante_ppi_desempenho_adequado_saeb_2023 IS NULL
      THEN "-%"
    ELSE CONCAT(
      REPLACE(FORMAT("%.2f", 100 * base.indice_ppi), ".", ","),
      "%"
    )
  END AS p3DiferencaPercentualRacial,
  base.indice_ppi AS p3IndiceRacial,
  base.indice_ppi_ajustado AS p3IndiceRacialAjustadoMargemErro,
  COALESCE(
    m.reduziuDesigualdadeRacial,
    CASE
      WHEN base.proporcao_estudante_ppi_desempenho_adequado_saeb_2019 IS NULL
        OR base.proporcao_estudante_ppi_desempenho_adequado_saeb_2023 IS NULL
        THEN "Ausência de dados suficientes"
      WHEN base.indicador_incluido_margem_ppi THEN "Desigualdade racial estável"
      WHEN COALESCE(base.indice_ppi, 0) > 0 THEN "Reduziu a desigualdade racial"
      ELSE "Não reduziu a desigualdade racial"
    END
  ) AS reduziuDesigualdadeRacial,
  CASE
    WHEN base.indicador_incluido_margem_ppi IS NULL THEN ""
    WHEN base.indicador_incluido_margem_ppi THEN "Sim"
    ELSE "Não"
  END AS margemDeErroDesigualdadeRacial,
  base.total_estudante_nse_baixo_saeb_2019 AS p3TotalEstudantesNseBaixoSaeb2019,
  base.total_estudante_nse_baixo_saeb_2023 AS p3TotalEstudantesNseBaixoSaeb2023,
  CASE
    WHEN base.proporcao_estudante_nse_baixo_desempenho_adequado_saeb_2019 IS NULL THEN "-%"
    ELSE CONCAT(
      REPLACE(FORMAT("%.2f", 100 * base.proporcao_estudante_nse_baixo_desempenho_adequado_saeb_2019), ".", ","),
      "%"
    )
  END AS p3PercentualSocioeconomica2019,
  CASE
    WHEN base.proporcao_estudante_nse_baixo_desempenho_adequado_saeb_2023 IS NULL THEN "-%"
    ELSE CONCAT(
      REPLACE(FORMAT("%.2f", 100 * base.proporcao_estudante_nse_baixo_desempenho_adequado_saeb_2023), ".", ","),
      "%"
    )
  END AS p3PercentualSocioeconomica2023,
  CASE
    WHEN base.proporcao_estudante_nse_baixo_desempenho_adequado_saeb_2019 IS NULL
      OR base.proporcao_estudante_nse_baixo_desempenho_adequado_saeb_2023 IS NULL
      THEN "-%"
    ELSE CONCAT(
      REPLACE(FORMAT("%.2f", 100 * base.indice_nse), ".", ","),
      "%"
    )
  END AS p3DiferencaPercentualSocioeconomica,
  base.indice_nse AS p3IndiceSocioeconomico,
  base.indice_nse_ajustado AS p3IndiceSocioeconomicoAjustadoMargemErro,
  COALESCE(
    m.reduziuDesigualdadeSocioeconomica,
    CASE
      WHEN base.proporcao_estudante_nse_baixo_desempenho_adequado_saeb_2019 IS NULL
        OR base.proporcao_estudante_nse_baixo_desempenho_adequado_saeb_2023 IS NULL
        THEN "Ausência de dados suficientes"
      WHEN base.indicador_incluido_margem_nse THEN "Desigualdade socioeconômica estável"
      WHEN COALESCE(base.indice_nse, 0) > 0 THEN "Reduziu a desigualdade socioeconômica"
      ELSE "Não reduziu a desigualdade socioeconômica"
    END
  ) AS reduziuDesigualdadeSocioeconomica,
  CASE
    WHEN base.indicador_incluido_margem_nse IS NULL THEN ""
    WHEN base.indicador_incluido_margem_nse THEN "Sim"
    ELSE "Não"
  END AS margemDeErroDesigualdadeSocioeconomica,
  IF(base.indicador_habilitado, "Sim", "Não") AS habilitadoCondicionalidade,
  COALESCE(base.motivo, "") AS habilitadoCondicionalidadeMotivo
FROM base_com_margem AS base
LEFT JOIN mapeamento_motivos m
  ON base.motivo = m.motivo
