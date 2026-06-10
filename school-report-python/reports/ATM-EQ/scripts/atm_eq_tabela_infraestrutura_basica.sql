CREATE OR REPLACE TABLE `br-mec-segape-sandbox.projeto_segape_dmape_relat_automatico.atm_eq_tabela_infraestrutura_basica` AS
WITH anos_comuns AS (
  SELECT DISTINCT
    CAST(c.id_municipio AS STRING) AS cod_ibge,
    c.ano
  FROM `br-mec-segape.educacao_inep_dados_abertos.censo_escolar_escola` c
  JOIN `br-mec-segape.educacao_politica_inep_censo.inep_censo` i
    ON i.ano = c.ano
   AND i.cod_ibge = CAST(c.id_municipio AS STRING)
   AND i.dependencia_administrativa = "Municipal"
  WHERE CAST(c.tipo_situacao_funcionamento AS STRING) = "1"
    AND CAST(c.rede AS STRING) = "3"
),
ano_base AS (
  SELECT cod_ibge, MAX(ano) AS ano_ref
  FROM anos_comuns
  GROUP BY cod_ibge
),
escolas_base AS (
  SELECT
    CAST(c.id_municipio AS STRING) AS cod_ibge,
    c.ano,
    CAST(c.id_escola AS STRING) AS id_escola,
    IF(CAST(c.tipo_localizacao_diferenciada AS STRING) = "3", 1, 0) AS fl_quilombola,
    IF(c.agua_potavel = 1, 1, 0) AS criterio_agua_potavel,
    IF(c.energia_inexistente = 0, 1, 0) AS criterio_energia_eletrica,
    IF(c.esgoto_inexistente = 0, 1, 0) AS criterio_esgotamento_sanitario,
    IF(c.biblioteca_sala_leitura = 1, 1, 0) AS criterio_biblioteca_sala_leitura,
    IF(c.internet_alunos = 1, 1, 0) AS criterio_internet_alunos,
    IF(c.sala_professor = 1, 1, 0) AS criterio_sala_professor,
    IF(c.banheiro = 1, 1, 0) AS criterio_banheiro,
    CASE
      WHEN c.agua_potavel = 1
        AND c.energia_inexistente = 0
        AND c.esgoto_inexistente = 0
        AND c.biblioteca_sala_leitura = 1
        AND c.internet_alunos = 1
        AND c.sala_professor = 1
        AND c.banheiro = 1
      THEN 1
      ELSE 0
    END AS criterio_todos_requisitos
  FROM `br-mec-segape.educacao_inep_dados_abertos.censo_escolar_escola` c
  JOIN ano_base a
    ON a.cod_ibge = CAST(c.id_municipio AS STRING)
   AND a.ano_ref = c.ano
  WHERE CAST(c.tipo_situacao_funcionamento AS STRING) = "1"
    AND CAST(c.rede AS STRING) = "3"
),
alunos_enriquecidos AS (
  SELECT
    i.cod_ibge,
    i.identificacao_unica,
    CASE
      WHEN COALESCE(NULLIF(TRIM(i.etnia), ""), "Não declarada") IN (
        "Branca",
        "Preta",
        "Parda",
        "Amarela",
        "Indígena",
        "Não declarada"
      ) THEN COALESCE(NULLIF(TRIM(i.etnia), ""), "Não declarada")
      ELSE "Não declarada"
    END AS etnia,
    e.fl_quilombola,
    e.criterio_agua_potavel,
    e.criterio_energia_eletrica,
    e.criterio_esgotamento_sanitario,
    e.criterio_biblioteca_sala_leitura,
    e.criterio_internet_alunos,
    e.criterio_sala_professor,
    e.criterio_banheiro,
    e.criterio_todos_requisitos
  FROM `br-mec-segape.educacao_politica_inep_censo.inep_censo` i
  JOIN ano_base a
    ON a.cod_ibge = i.cod_ibge
   AND a.ano_ref = i.ano
  JOIN escolas_base e
    ON e.cod_ibge = i.cod_ibge
   AND e.ano = i.ano
   AND e.id_escola = CAST(i.id_escola AS STRING)
  WHERE i.dependencia_administrativa = "Municipal"
),
alunos_base AS (
  SELECT
    cod_ibge,
    identificacao_unica,
    CASE
      WHEN MAX(fl_quilombola) = 1 THEN "Quilombola"
      ELSE ANY_VALUE(etnia)
    END AS categoria,
    MAX(criterio_agua_potavel) AS criterio_agua_potavel,
    MAX(criterio_energia_eletrica) AS criterio_energia_eletrica,
    MAX(criterio_esgotamento_sanitario) AS criterio_esgotamento_sanitario,
    MAX(criterio_biblioteca_sala_leitura) AS criterio_biblioteca_sala_leitura,
    MAX(criterio_internet_alunos) AS criterio_internet_alunos,
    MAX(criterio_sala_professor) AS criterio_sala_professor,
    MAX(criterio_banheiro) AS criterio_banheiro,
    MAX(criterio_todos_requisitos) AS criterio_todos_requisitos
  FROM alunos_enriquecidos
  GROUP BY cod_ibge, identificacao_unica
),
criterios AS (
  SELECT "Água potável" AS indicador, 1 AS ordem, "criterio_agua_potavel" AS criterio UNION ALL
  SELECT "Energia elétrica", 2, "criterio_energia_eletrica" UNION ALL
  SELECT "Esgotamento sanitário", 3, "criterio_esgotamento_sanitario" UNION ALL
  SELECT "Biblioteca ou sala de leitura", 4, "criterio_biblioteca_sala_leitura" UNION ALL
  SELECT "Internet para alunos", 5, "criterio_internet_alunos" UNION ALL
  SELECT "Sala de professores", 6, "criterio_sala_professor" UNION ALL
  SELECT "Banheiro", 7, "criterio_banheiro" UNION ALL
  SELECT "Todos os requisitos", 8, "criterio_todos_requisitos"
),
base_pivot AS (
  SELECT
    a.cod_ibge,
    c.indicador,
    c.ordem,
    a.categoria,
    CASE c.criterio
      WHEN "criterio_agua_potavel" THEN a.criterio_agua_potavel
      WHEN "criterio_energia_eletrica" THEN a.criterio_energia_eletrica
      WHEN "criterio_esgotamento_sanitario" THEN a.criterio_esgotamento_sanitario
      WHEN "criterio_biblioteca_sala_leitura" THEN a.criterio_biblioteca_sala_leitura
      WHEN "criterio_internet_alunos" THEN a.criterio_internet_alunos
      WHEN "criterio_sala_professor" THEN a.criterio_sala_professor
      WHEN "criterio_banheiro" THEN a.criterio_banheiro
      WHEN "criterio_todos_requisitos" THEN a.criterio_todos_requisitos
      ELSE 0
    END AS atende_criterio
  FROM alunos_base a
  CROSS JOIN criterios c
),
agregados AS (
  SELECT
    cod_ibge,
    indicador,
    ordem,
    COUNTIF(categoria = "Branca") AS total_branca,
    COUNTIF(categoria = "Branca" AND atende_criterio = 1) AS total_branca_ok,
    COUNTIF(categoria = "Preta") AS total_preta,
    COUNTIF(categoria = "Preta" AND atende_criterio = 1) AS total_preta_ok,
    COUNTIF(categoria = "Parda") AS total_parda,
    COUNTIF(categoria = "Parda" AND atende_criterio = 1) AS total_parda_ok,
    COUNTIF(categoria = "Amarela") AS total_amarela,
    COUNTIF(categoria = "Amarela" AND atende_criterio = 1) AS total_amarela_ok,
    COUNTIF(categoria = "Indígena") AS total_indigena,
    COUNTIF(categoria = "Indígena" AND atende_criterio = 1) AS total_indigena_ok,
    COUNTIF(categoria = "Não declarada") AS total_nao_declarada,
    COUNTIF(categoria = "Não declarada" AND atende_criterio = 1) AS total_nao_declarada_ok,
    COUNTIF(categoria = "Quilombola") AS total_quilombola,
    COUNTIF(categoria = "Quilombola" AND atende_criterio = 1) AS total_quilombola_ok
  FROM base_pivot
  GROUP BY cod_ibge, indicador, ordem
)
SELECT
  a.cod_ibge,
  a.indicador,
  ROUND(SAFE_DIVIDE(total_branca_ok, NULLIF(total_branca, 0)) * 100, 2) AS percentualBranca,
  IF(total_branca = 0, "-", REPLACE(FORMAT("%.1f", ROUND(SAFE_DIVIDE(total_branca_ok, NULLIF(total_branca, 0)) * 100, 2)), ".", ",") || "%") AS percentualBrancaFmt,
  ROUND(SAFE_DIVIDE(total_preta_ok, NULLIF(total_preta, 0)) * 100, 2) AS percentualPreta,
  IF(total_preta = 0, "-", REPLACE(FORMAT("%.1f", ROUND(SAFE_DIVIDE(total_preta_ok, NULLIF(total_preta, 0)) * 100, 2)), ".", ",") || "%") AS percentualPretaFmt,
  ROUND(SAFE_DIVIDE(total_parda_ok, NULLIF(total_parda, 0)) * 100, 2) AS percentualParda,
  IF(total_parda = 0, "-", REPLACE(FORMAT("%.1f", ROUND(SAFE_DIVIDE(total_parda_ok, NULLIF(total_parda, 0)) * 100, 2)), ".", ",") || "%") AS percentualPardaFmt,
  ROUND(SAFE_DIVIDE(total_amarela_ok, NULLIF(total_amarela, 0)) * 100, 2) AS percentualAmarela,
  IF(total_amarela = 0, "-", REPLACE(FORMAT("%.1f", ROUND(SAFE_DIVIDE(total_amarela_ok, NULLIF(total_amarela, 0)) * 100, 2)), ".", ",") || "%") AS percentualAmarelaFmt,
  ROUND(SAFE_DIVIDE(total_indigena_ok, NULLIF(total_indigena, 0)) * 100, 2) AS percentualIndigena,
  IF(total_indigena = 0, "-", REPLACE(FORMAT("%.1f", ROUND(SAFE_DIVIDE(total_indigena_ok, NULLIF(total_indigena, 0)) * 100, 2)), ".", ",") || "%") AS percentualIndigenaFmt,
  ROUND(SAFE_DIVIDE(total_nao_declarada_ok, NULLIF(total_nao_declarada, 0)) * 100, 2) AS percentualNaoDeclarada,
  IF(total_nao_declarada = 0, "-", REPLACE(FORMAT("%.1f", ROUND(SAFE_DIVIDE(total_nao_declarada_ok, NULLIF(total_nao_declarada, 0)) * 100, 2)), ".", ",") || "%") AS percentualNaoDeclaradaFmt,
  ROUND(SAFE_DIVIDE(total_quilombola_ok, NULLIF(total_quilombola, 0)) * 100, 2) AS percentualQuilombola,
  IF(total_quilombola = 0, "-", REPLACE(FORMAT("%.1f", ROUND(SAFE_DIVIDE(total_quilombola_ok, NULLIF(total_quilombola, 0)) * 100, 2)), ".", ",") || "%") AS percentualQuilombolaFmt,
  b.ano_ref AS anoReferencia
FROM agregados a
JOIN ano_base b
  ON b.cod_ibge = a.cod_ibge;
