CREATE OR REPLACE TABLE `br-mec-segape-sandbox.projeto_segape_dmape_relat_automatico.atm_eq_grafico_atendimento_creche_pre_escola` AS
WITH ultima_carga_2025 AS (
  SELECT MAX(mes_ref_carga) AS mes_ref_carga
  FROM `br-mec-segape.educacao_mds_cadunico.pessoa_historico`
  WHERE STARTS_WITH(mes_ref_carga, "2025")
),
parametros_carga AS (
  SELECT
    mes_ref_carga,
    EXTRACT(YEAR FROM PARSE_DATE("%Y%m%d", CONCAT(mes_ref_carga, "01"))) AS ano_referencia,
    DATE_SUB(
      DATE_ADD(PARSE_DATE("%Y%m%d", CONCAT(mes_ref_carga, "01")), INTERVAL 1 MONTH),
      INTERVAL 1 DAY
    ) AS data_referencia
  FROM ultima_carga_2025
),
pessoas_base AS (
  SELECT
    p.cd_ibge_cadastro AS cod_ibge,
    p.id_pessoa,
    p.dt_nasc_pessoa,
    p.co_raca_cor_pessoa,
    p.in_frequenta_escola_memb,
    c.mes_ref_carga,
    c.ano_referencia,
    c.data_referencia
  FROM `br-mec-segape.educacao_mds_cadunico.pessoa_historico` p
  JOIN parametros_carga c
    ON c.mes_ref_carga = p.mes_ref_carga
  WHERE p.cd_ibge_cadastro IS NOT NULL
    AND p.dt_nasc_pessoa IS NOT NULL
  QUALIFY ROW_NUMBER() OVER (
    PARTITION BY p.mes_ref_carga, p.id_pessoa
    ORDER BY p.data_ultima_atualizacao DESC, p.datetime_captura DESC
  ) = 1
),
pessoas_classificadas AS (
  SELECT
    cod_ibge,
    ano_referencia,
    mes_ref_carga,
    CASE
      WHEN DATE_DIFF(data_referencia, dt_nasc_pessoa, YEAR) BETWEEN 0 AND 3 THEN "Creche"
      WHEN DATE_DIFF(data_referencia, dt_nasc_pessoa, YEAR) BETWEEN 4 AND 6 THEN "Pré-Escola"
      ELSE NULL
    END AS etapa,
    CASE co_raca_cor_pessoa
      WHEN "1" THEN "Branca"
      WHEN "2" THEN "Preta"
      WHEN "3" THEN "Amarela"
      WHEN "4" THEN "Parda"
      WHEN "5" THEN "Indígena"
      ELSE NULL
    END AS categoria,
    CASE
      WHEN in_frequenta_escola_memb = "1" THEN "Estuda"
      WHEN in_frequenta_escola_memb IN ("3", "4") THEN "Não estuda"
      ELSE NULL
    END AS situacao
  FROM pessoas_base
),
base_filtrada AS (
  SELECT
    cod_ibge,
    ano_referencia,
    mes_ref_carga,
    etapa,
    categoria,
    situacao
  FROM pessoas_classificadas
  WHERE etapa IS NOT NULL
    AND categoria IS NOT NULL
    AND situacao IS NOT NULL
),
denominadores AS (
  SELECT
    cod_ibge,
    ano_referencia,
    mes_ref_carga,
    etapa,
    categoria,
    COUNT(*) AS total_grupo
  FROM base_filtrada
  GROUP BY 1, 2, 3, 4, 5
),
numeradores AS (
  SELECT
    cod_ibge,
    ano_referencia,
    mes_ref_carga,
    etapa,
    categoria,
    situacao,
    COUNT(*) AS quantidade
  FROM base_filtrada
  GROUP BY 1, 2, 3, 4, 5, 6
)
SELECT
  n.cod_ibge,
  n.etapa,
  n.categoria,
  n.situacao,
  n.quantidade,
  ROUND(SAFE_DIVIDE(n.quantidade, d.total_grupo) * 100, 2) AS percentual,
  n.ano_referencia AS anoReferencia,
  n.mes_ref_carga AS mesRefCarga
FROM numeradores n
JOIN denominadores d
  ON d.cod_ibge = n.cod_ibge
 AND d.ano_referencia = n.ano_referencia
 AND d.mes_ref_carga = n.mes_ref_carga
 AND d.etapa = n.etapa
 AND d.categoria = n.categoria;
