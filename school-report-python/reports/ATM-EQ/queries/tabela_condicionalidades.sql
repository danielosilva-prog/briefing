WITH
requisitos_unificados AS (
    SELECT
      CAST(ano_exercicio AS STRING) AS ano,
      CAST(id_municipio AS STRING) AS cod_ibge,
      CAST(condicionalidade AS STRING) AS condicionalidade,
      CAST(NULL AS STRING) AS indicador,
      cumprimento
    FROM `br-mec-segape.educacao_politica_fundeb.fundeb_condicionalidade`
    WHERE CAST(id_municipio AS STRING) = @cod_ibge
    
    UNION ALL

    SELECT
      CAST(ano_exercicio AS STRING) AS ano,
      CAST(id_ibge AS STRING) AS cod_ibge,
      CAST(NULL AS STRING) AS condicionalidade,
      indicador,
      cumprimento
    FROM `br-mec-segape.educacao_politica_fundeb.fundeb_indicador`
    WHERE CAST(id_ibge AS STRING) = @cod_ibge

),
-- Último ano disponível para o município
max_ano_ref AS (
  SELECT
    max(ano) AS ano_ref
  FROM requisitos_unificados
  WHERE CAST(cod_ibge AS STRING) = @cod_ibge
),
-- Base filtrada no último ano
base_condicionalidades AS (
  SELECT
    CASE
    WHEN req.condicionalidade = '1' THEN '1 - Seleção por critérios técnicos do cargo de diretor escolar'
    WHEN req.condicionalidade = '2' THEN '2 - Participação (≥80%) no Sistema de Avaliação da Educação Básica – Saeb'
    WHEN req.condicionalidade = '3' THEN '3 - Redução das desigualdades'
    WHEN req.condicionalidade = '4' THEN '4 - Regulamentação do ICMS Educacional no estado'
    WHEN req.condicionalidade = '5' THEN '5 - Referenciais curriculares alinhados à Base Nacional Comum Curricular'
    WHEN req.indicador = 'Atendimento' THEN 'Avanço no indicador de atendimento'
    WHEN req.indicador = 'Aprendizagem' THEN 'Avanço no indicador de aprendizagem'
    ELSE NULL
  END AS descricao_condicionalidade,
    cumprimento
  FROM requisitos_unificados req
  JOIN max_ano_ref a
    ON a.ano_ref = req.ano
  WHERE CAST(req.cod_ibge AS STRING) = @cod_ibge
)
SELECT
  CAST((SELECT ano_ref FROM max_ano_ref) AS STRING) AS anoReferencia,
  -- =====================================================
  -- CONDICIONALIDADES (BOOLEANAS)
  -- =====================================================

  COALESCE(MAX(
    CASE
      WHEN descricao_condicionalidade = '1 - Seleção por critérios técnicos do cargo de diretor escolar'
        AND cumprimento IN ('H', 'A') THEN "true"
      WHEN descricao_condicionalidade = '1 - Seleção por critérios técnicos do cargo de diretor escolar'
        AND cumprimento IN ('I', 'N') THEN "false"
    END
  ), "pendente") AS selecaoPorCriteriosTecnicosCargoDiretorEscolar,

  COALESCE(MAX(
    CASE
      WHEN descricao_condicionalidade = '2 - Participação (≥80%) no Sistema de Avaliação da Educação Básica – Saeb'
        AND cumprimento IN ('H', 'A') THEN "true"
      WHEN descricao_condicionalidade = '2 - Participação (≥80%) no Sistema de Avaliação da Educação Básica – Saeb'
        AND cumprimento IN ('I', 'N') THEN "false"
    END
  ), "pendente") AS participacaoNoSaeb,

  COALESCE(MAX(
    CASE
      WHEN descricao_condicionalidade = '3 - Redução das desigualdades'
        AND cumprimento IN ('H', 'A') THEN "true"
      WHEN descricao_condicionalidade = '3 - Redução das desigualdades'
        AND cumprimento IN ('I', 'N') THEN "false"     
    END
  ), "pendente") AS reducaoDesigualdades,

  COALESCE(MAX(
    CASE
      WHEN descricao_condicionalidade = '4 - Regulamentação do ICMS Educacional no estado'
        AND cumprimento IN ('H', 'A') THEN "true"
      WHEN descricao_condicionalidade = '4 - Regulamentação do ICMS Educacional no estado'
        AND cumprimento IN ('I', 'N') THEN "false"
      
    END
  ), "pendente") AS regulamentacaoICMSEducacionalEstado,

  COALESCE(MAX(
    CASE
      WHEN descricao_condicionalidade = '5 - Referenciais curriculares alinhados à Base Nacional Comum Curricular'
        AND cumprimento IN ('H', 'A') THEN "true"
      WHEN descricao_condicionalidade = '5 - Referenciais curriculares alinhados à Base Nacional Comum Curricular'
        AND cumprimento IN ('I', 'N') THEN "false"    
    END
  ), "pendente") AS referenciaisCurricularesAlinhadosBNCC,

  COALESCE(MAX(
    CASE
      WHEN descricao_condicionalidade = 'Avanço no indicador de atendimento'
        AND cumprimento IN ('H', 'A') THEN "true"
      WHEN descricao_condicionalidade = 'Avanço no indicador de atendimento'
        AND cumprimento IN ('I', 'N') THEN "false"
    END
  ), "pendente") AS avancarIndicadorAtendimento,

  COALESCE(MAX(
    CASE
      WHEN descricao_condicionalidade = 'Avanço no indicador de aprendizagem'
        AND cumprimento IN ('H', 'A') THEN "true"
      WHEN descricao_condicionalidade = 'Avanço no indicador de aprendizagem'
        AND cumprimento IN ('I', 'N') THEN "false"     
    END
  ), "pendente") AS avancarIndicadorAprendizagem

FROM base_condicionalidades
