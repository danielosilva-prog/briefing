-- (Documentação consolidada via Engenharia Reversa do DBT e Inspeção de Metadados)
--
-- [1. PADRÕES GEOGRÁFICOS DE 'ID' - COMO EVITAR DUPLICAÇÕES]
-- * BRASIL: Obrigatório usar o filtro `id = '99'`. Acessa a linha pré-agregada e deduplicada 
--   pelo dbt. Nunca faça SUM() dos estados para chegar ao Brasil.
-- * ESTADO (UF): Obrigatório usar `LENGTH(CAST(id AS STRING)) = 2 AND id != '99'`.
-- * MUNICÍPIO: Código IBGE (`LENGTH = 7`) ou cruzamento de string (UPPER TRIM).
--
-- [2. REGRAS DE NEGÓCIO E ANOMALIAS DA BASE (PROVADAS POR AUDITORIA NO DBT)]
-- A) INDICADORES INEP (ETI e Distorção Idade-Série):
--    - O dbt possui um filtro hardcoded: `id_tipo_dependencia != 4` e `dependencia = 'Pública'`.
--    - Logo, a REDE PRIVADA é 100% ignorada nos indicadores do painel (mesmo no denominador).
--    - Erro do PDF Oficial: O PDF costuma colar por erro humano a queda da Taxa de Distorção 
--      no campo de evolução do ETI. O nosso script calcula a evolução real do ETI.
--
-- B) COMPROMISSO CRIANÇA ALFABETIZADA (CNCA):
--    - O painel filtra EXCLUSIVAMENTE as redes 'MUNICIPAL' e 'ESTADUAL'. 
--    - A execução direta do Governo Federal é ignorada, o que explica por que a soma 
--      dinâmica BR no dbt gera R$ 1,29 Bi e o PDF oficial reporta R$ 1,56 Bi.
--    - A tabela usa lógica "Snapshot" (QUALIFY MAX dt_ref) por ano (não acumula meses).
--
-- C) NOVO PAC (Pacto, Seleções e Sesu):
--    - Seleções (PERIGO): O dbt consolida o Edital 1 inteiro sem filtros (trazendo lixo).
--      É OBRIGATÓRIO manter o `WHERE situacao NOT IN ('Prop. Cancelada'...)` no nosso SQL.
--    - Sesu: Omissão de dados de 'Expansão' na tabela principal, requerendo compensação.
--    - Pacto: O `indicador_aprovada = TRUE` espelha o status 'DEFERIDO' (ignora 'Em Análise').
--
-- D) ENEC (Escolas Conectadas):
--    - A variável `indicador_booleano` do dbt só aceita escolas de Nível 4 ou 5. As restantes,
--      mesmo que tenham internet (Nível 1 a 3), entram no balde das "Não conectadas".
--
-- E) FUNDEB, PNAE e PNATE:
--    - Fundeb: `status = 'Realizado'` é a tradução exata do `id_status = 1` mapeado no dbt.
--    - PNAE/PNATE: Extraímos direto da origem já unpivotada para não duplicar repasses financeiros.
--
-- [3. AUDITORIA DE ANOMALIAS MASSIVAS E PERFORMANCE (PÉ-DE-MEIA)]
--    - A tabela de histórico do PDM possui ~1 Bilião de linhas (287 GB).
--    - Auditorias revelaram 16,5 milhões de registos com `id_pessoa` NULL e 
--      alguns CPFs específicos duplicados mais de 400 vezes na mesma carga (produto cartesiano/bug).
--    - SALVA-VIDAS: O uso de `COUNT(DISTINCT id_pessoa)` neste script é a ÚNICA garantia 
--      matemática contra essa anomalia de replicação.
--    - Taxa de Adesão (%): Omitida. O dbt importa "alunos fantasmas" via FULL OUTER JOIN 
--      mas não traz o denominador (Censo Escolar). Usar apenas os valores absolutos reportados.
-- ======================

DECLARE target_mun STRING DEFAULT 'Campo Grande';
DECLARE target_uf STRING DEFAULT 'MS';
DECLARE target_mun_uf STRING DEFAULT CONCAT(target_mun, ' - ', target_uf);

WITH mapeamento_uf AS (
  SELECT 'AC' AS sigla_uf, 'ACRE' AS nome UNION ALL SELECT 'AL', 'ALAGOAS' UNION ALL SELECT 'AP', 'AMAPÁ' UNION ALL SELECT 'AM', 'AMAZONAS' UNION ALL SELECT 'BA', 'BAHIA' UNION ALL SELECT 'CE', 'CEARÁ' UNION ALL SELECT 'DF', 'DISTRITO FEDERAL' UNION ALL SELECT 'ES', 'ESPÍRITO SANTO' UNION ALL SELECT 'GO', 'GOIÁS' UNION ALL SELECT 'MA', 'MARANHÃO' UNION ALL SELECT 'MT', 'MATO GROSSO' UNION ALL SELECT 'MS', 'MATO GROSSO DO SUL' UNION ALL SELECT 'MG', 'MINAS GERAIS' UNION ALL SELECT 'PA', 'PARÁ' UNION ALL SELECT 'PB', 'PARAÍBA' UNION ALL SELECT 'PR', 'PARANÁ' UNION ALL SELECT 'PE', 'PERNAMBUCO' UNION ALL SELECT 'PI', 'PIAUÍ' UNION ALL SELECT 'RJ', 'RIO DE JANEIRO' UNION ALL SELECT 'RN', 'RIO GRANDE DO NORTE' UNION ALL SELECT 'RS', 'RIO GRANDE DO SUL' UNION ALL SELECT 'RO', 'RONDÔNIA' UNION ALL SELECT 'RR', 'RORAIMA' UNION ALL SELECT 'SC', 'SANTA CATARINA' UNION ALL SELECT 'SP', 'SÃO PAULO' UNION ALL SELECT 'SE', 'SERGIPE' UNION ALL SELECT 'TO', 'TOCANTINS'
),


mun_ibge AS (
    SELECT  id_municipio_6 as cod_ibge 
    FROM `br-mec-segape.educacao_dados_mestres.municipio` 
    WHERE nome = target_mun and sigla_uf = target_uf
),


-- ====================================================================================
-- 1. ESCOLAS CONECTADAS
-- ====================================================================================
escola_conectada AS (
  SELECT
    (SELECT COUNTIF(escolas_conectadas_nivel IN ('Escola com velocidade adequada e rede Wi-Fi insuficiente', 'Escola com velocidade e rede Wi-Fi adequados')) FROM `br-mec-segape.educacao_politica_enec.enec_conectividade` WHERE sigla_uf = target_uf AND UPPER(TRIM(municipio)) = UPPER(target_mun)) AS con_m,
    (SELECT COUNT(*) FROM `br-mec-segape.educacao_politica_enec.enec_conectividade` WHERE sigla_uf = target_uf AND UPPER(TRIM(municipio)) = UPPER(target_mun)) AS tot_m,
    (SELECT COUNTIF(escolas_conectadas_nivel IN ('Escola com velocidade adequada e rede Wi-Fi insuficiente', 'Escola com velocidade e rede Wi-Fi adequados')) FROM `br-mec-segape.educacao_politica_enec.enec_conectividade` WHERE sigla_uf = target_uf) AS con_e,
    (SELECT COUNT(*) FROM `br-mec-segape.educacao_politica_enec.enec_conectividade` WHERE sigla_uf = target_uf) AS tot_e
),

-- ====================================================================================
-- 2. ESCOLA EM TEMPO INTEGRAL (ETI)
-- ====================================================================================
eti AS (
  SELECT
    (SELECT COALESCE(SUM(peti_07_qtd_matricula_declarada_ciclo), 0) FROM `br-mec-segape.projeto_gaia.gaia_peti` WHERE uf = target_uf AND peti_04_ciclo = '2023/2024' AND UPPER(TRIM(nome)) = UPPER(target_mun)) AS mat_m,
    (SELECT COALESCE(SUM(peti_09_valor_pago_ciclo), 0) FROM `br-mec-segape.projeto_gaia.gaia_peti` WHERE uf = target_uf AND peti_04_ciclo = '2023/2024' AND UPPER(TRIM(nome)) = UPPER(target_mun)) AS val_m,
    (SELECT SUM(mat) FROM (SELECT peti_07_qtd_matricula_declarada_ciclo AS mat FROM `br-mec-segape.projeto_gaia.gaia_peti` WHERE uf = target_uf AND uf != 'BR' AND peti_04_ciclo IN ('2023/2024', '2023', '2024') UNION ALL SELECT CAST(matriculas_fundeb AS INT64) FROM `br-mec-segape-sandbox.sandbox_segape_dmape.andre_teste_eti_valores_2025_csv` WHERE uf = target_uf AND tipo_registro = 'repasse' AND nivel_territorial IN ('municipio', 'estadual'))) AS mat_e,
    (SELECT SUM(val) FROM (SELECT peti_09_valor_pago_ciclo AS val FROM `br-mec-segape.projeto_gaia.gaia_peti` WHERE uf = target_uf AND uf != 'BR' AND peti_04_ciclo IN ('2023/2024', '2023', '2024') UNION ALL SELECT CAST(valor_total_fomento AS FLOAT64) FROM `br-mec-segape-sandbox.sandbox_segape_dmape.andre_teste_eti_valores_2025_csv` WHERE uf = target_uf AND tipo_registro = 'repasse' AND nivel_territorial IN ('municipio', 'estadual'))) AS val_e
),

-- ====================================================================================
-- 3. CNCA
-- ====================================================================================
cnca AS (
  SELECT
    (SELECT COALESCE(SUM(qtd_cantinho_leitura_apoiado),0) FROM `br-mec-segape.projeto_painel_ministro.painel_cnca` WHERE sigla_uf = target_uf AND UPPER(TRIM(municipio)) = UPPER(target_mun_uf)) AS cant_m,
    (SELECT COALESCE(SUM(qtd_escolas_apoiadas_cantinho_leitura),0) FROM `br-mec-segape.projeto_painel_ministro.painel_cnca` WHERE sigla_uf = target_uf AND UPPER(TRIM(municipio)) = UPPER(target_mun_uf)) AS esc_m,
    (SELECT COALESCE(SUM(valor_pago_escolas_cantinho_leitura),0) FROM `br-mec-segape.projeto_painel_ministro.painel_cnca` WHERE sigla_uf = target_uf AND UPPER(TRIM(municipio)) = UPPER(target_mun_uf)) AS vcant_m,
    (SELECT COALESCE(SUM(CASE WHEN ano = 2026 THEN qtd_articuladores_total ELSE 0 END),0) FROM `br-mec-segape.projeto_painel_ministro.painel_cnca` WHERE sigla_uf = target_uf AND UPPER(TRIM(municipio)) = UPPER(target_mun_uf)) AS art_m,
    (SELECT COALESCE(SUM(valor_repasse_bolsistas_total),0) FROM `br-mec-segape.projeto_painel_ministro.painel_cnca` WHERE sigla_uf = target_uf AND UPPER(TRIM(municipio)) = UPPER(target_mun_uf)) AS vbol_m,
    (SELECT COALESCE(SUM(valor_empenhado_materiais),0) FROM `br-mec-segape.projeto_painel_ministro.painel_cnca` WHERE sigla_uf = target_uf AND UPPER(TRIM(municipio)) = UPPER(target_mun_uf)) AS vmat_m,
    (SELECT COALESCE(SUM(valor_empenhado_formacoes),0) FROM `br-mec-segape.projeto_painel_ministro.painel_cnca` WHERE sigla_uf = target_uf AND UPPER(TRIM(municipio)) = UPPER(target_mun_uf)) AS vform_m,

    (SELECT SUM(qtd_cantinho_leitura_apoiado) FROM `br-mec-segape.projeto_painel_ministro.painel_cnca` WHERE sigla_uf = target_uf AND id != '99' AND (municipio != 'Todos' OR sigla_uf = 'DF')) AS cant_e,
    (SELECT SUM(qtd_escolas_apoiadas_cantinho_leitura) FROM `br-mec-segape.projeto_painel_ministro.painel_cnca` WHERE sigla_uf = target_uf AND id != '99' AND (municipio != 'Todos' OR sigla_uf = 'DF')) AS esc_e,
    (SELECT SUM(valor_pago_escolas_cantinho_leitura) FROM `br-mec-segape.projeto_painel_ministro.painel_cnca` WHERE sigla_uf = target_uf AND id != '99' AND (municipio != 'Todos' OR sigla_uf = 'DF')) AS vcant_e,
    
    (SELECT SUM(qtd_articuladores_total) FROM `br-mec-segape.projeto_painel_ministro.painel_cnca` WHERE sigla_uf = target_uf AND ano = 2026 AND id != '99' AND (municipio != 'Todos' OR sigla_uf = 'DF')) + (SELECT COALESCE(SUM(qtd_articuladores_renalfa_regional), 0) + COALESCE(SUM(qtd_articuladores_renalfa_estadual), 0) FROM `br-mec-segape.projeto_painel_ministro.painel_cnca` WHERE sigla_uf = target_uf AND ano = 2026 AND id != '99') AS art_e,

    (SELECT SUM(valor_repasse_bolsistas_total) FROM `br-mec-segape.projeto_painel_ministro.painel_cnca` WHERE sigla_uf = target_uf AND id != '99' AND municipio = 'Todos') AS vbol_e,
    (SELECT SUM(valor_empenhado_materiais) FROM `br-mec-segape.projeto_painel_ministro.painel_cnca` WHERE sigla_uf = target_uf AND id != '99') AS vmat_e,
    (SELECT SUM(valor_empenhado_formacoes) FROM `br-mec-segape.projeto_painel_ministro.painel_cnca` WHERE sigla_uf = target_uf AND id != '99') AS vform_e
),

-- ====================================================================================
-- 4. PÉ-DE-MEIA
-- ====================================================================================
pdm AS (
  SELECT
    (SELECT COUNT(DISTINCT iehc.id_pessoa)
     FROM `br-mec-segape.educacao_politica_pdm.incentivo_estudante_historico_completo` iehc
     JOIN `br-mec-segape.educacao_dados_mestres.municipio` m
       ON CAST(iehc.id AS STRING) = CAST(m.id_municipio AS STRING)
     WHERE m.sigla_uf = target_uf
       AND UPPER(TRIM(m.nome)) = UPPER(target_mun)
       AND iehc.ultima_carga IS TRUE
       AND iehc.id_tipo_status_parcela IN ('105','115')) AS est_m,
    (SELECT COALESCE(SUM(iehc.valor_enviado),0)
     FROM `br-mec-segape.educacao_politica_pdm.incentivo_estudante_historico_completo` iehc
     JOIN `br-mec-segape.educacao_dados_mestres.municipio` m
       ON CAST(iehc.id AS STRING) = CAST(m.id_municipio AS STRING)
     WHERE m.sigla_uf = target_uf
       AND UPPER(TRIM(m.nome)) = UPPER(target_mun)
       AND iehc.ultima_carga IS TRUE
       AND iehc.id_tipo_status_parcela IN ('105','115')) AS val_m,
    (SELECT COUNT(DISTINCT mup.id_pessoa)
     FROM `br-mec-segape.educacao_politica_pdm.matricula_unica_pdm` mup
     JOIN `br-mec-segape.educacao_dados_mestres.municipio` m
       ON CAST(mup.id_municipio AS STRING) = CAST(m.id_municipio AS STRING)
     WHERE m.sigla_uf = target_uf
       AND UPPER(TRIM(m.nome)) = UPPER(target_mun)) AS mat_m,
    (SELECT COUNT(DISTINCT iehc.id_pessoa)
     FROM `br-mec-segape.educacao_politica_pdm.incentivo_estudante_historico_completo` iehc
     LEFT JOIN (SELECT DISTINCT id_uf, sigla_uf FROM `br-mec-segape.educacao_dados_mestres.municipio`) m
       ON iehc.id = m.id_uf
     WHERE iehc.ultima_carga is true
       AND iehc.id_tipo_status_parcela IN ('105','115')
       AND iehc.id != '99'
       AND LENGTH(id) = 2
       AND m.sigla_uf = target_uf) AS est_e,
    (SELECT COALESCE(SUM(iehc.valor_enviado),0)
     FROM `br-mec-segape.educacao_politica_pdm.incentivo_estudante_historico_completo` iehc
     LEFT JOIN (SELECT DISTINCT id_uf, sigla_uf FROM `br-mec-segape.educacao_dados_mestres.municipio`) m
       ON iehc.id = m.id_uf
     WHERE iehc.ultima_carga is true
       AND iehc.id_tipo_status_parcela IN ('105','115')
       AND iehc.id != '99'
       AND LENGTH(id) = 2
       AND m.sigla_uf = target_uf) AS val_e,
    (SELECT COUNT(DISTINCT mup.id_pessoa)
     FROM `br-mec-segape.educacao_politica_pdm.matricula_unica_pdm` mup
     JOIN (SELECT DISTINCT id_uf, sigla_uf FROM `br-mec-segape.educacao_dados_mestres.municipio`) m
       ON mup.id_uf = m.id_uf
     WHERE m.sigla_uf = target_uf) AS mat_e
),
pdm_referencia_abrangencia AS (
SELECT
   CONCAT(min(ciclo_pdm), '-', max(ciclo_pdm)) pdm_abrangencia,
    CASE EXTRACT(MONTH FROM MAX(data_referencia))
      WHEN 1 THEN 'Janeiro' WHEN 2 THEN 'Fevereiro' WHEN 3 THEN 'Março'
      WHEN 4 THEN 'Abril' WHEN 5 THEN 'Maio' WHEN 6 THEN 'Junho'
      WHEN 7 THEN 'Julho' WHEN 8 THEN 'Agosto' WHEN 9 THEN 'Setembro'
      WHEN 10 THEN 'Outubro' WHEN 11 THEN 'Novembro' WHEN 12 THEN 'Dezembro'
    END
   || '/' || EXTRACT(YEAR FROM MAX(data_referencia)) AS pdm_referencia
  FROM `br-mec-segape.educacao_politica_pdm.incentivo_estudante_historico_completo` iehc
  LEFT JOIN (SELECT DISTINCT id_uf, sigla_uf FROM `br-mec-segape.educacao_dados_mestres.municipio`) m ON iehc.id = m.id_uf
  WHERE ultima_carga is true AND id_tipo_status_parcela IN ('105','115') AND id != '99' AND LENGTH(id) = 2
),


-- ====================================================================================
-- 5. NOVO PAC PACTO
-- ====================================================================================
pacto AS (
  SELECT
    (SELECT COUNT(id_obra) FROM `br-mec-segape.projeto_painel_ministro.painel_novopac_pacto` WHERE indicador_aprovada = TRUE AND sigla_uf = target_uf AND UPPER(TRIM(municipio)) = UPPER(target_mun_uf)) AS ob_m,
    (SELECT COALESCE(SUM(valor_previsto),0) FROM `br-mec-segape.projeto_painel_ministro.painel_novopac_pacto` WHERE indicador_aprovada = TRUE AND sigla_uf = target_uf AND UPPER(TRIM(municipio)) = UPPER(target_mun_uf)) AS vp_m,
    (SELECT COALESCE(SUM(valor_repasse),0) FROM `br-mec-segape.projeto_painel_ministro.painel_novopac_pacto` WHERE indicador_aprovada = TRUE AND sigla_uf = target_uf AND UPPER(TRIM(municipio)) = UPPER(target_mun_uf)) AS vr_m,
    (SELECT COUNT(*) FROM (SELECT id_obra FROM `br-mec-segape.projeto_painel_ministro.painel_novopac_pacto` WHERE indicador_aprovada = TRUE AND LENGTH(CAST(id AS STRING)) = 2 AND id != '99' AND sigla_uf = target_uf GROUP BY id_obra)) AS ob_e,
    (SELECT COALESCE(SUM(valor_previsto),0) FROM (SELECT id_obra, MAX(valor_previsto) AS valor_previsto FROM `br-mec-segape.projeto_painel_ministro.painel_novopac_pacto` WHERE indicador_aprovada = TRUE AND LENGTH(CAST(id AS STRING)) = 2 AND id != '99' AND sigla_uf = target_uf GROUP BY id_obra)) AS vp_e,
    (SELECT COALESCE(SUM(valor_repasse),0) FROM (SELECT id_obra, MAX(valor_repasse) AS valor_repasse FROM `br-mec-segape.projeto_painel_ministro.painel_novopac_pacto` WHERE indicador_aprovada = TRUE AND LENGTH(CAST(id AS STRING)) = 2 AND id != '99' AND sigla_uf = target_uf GROUP BY id_obra)) AS vr_e
),

-- ====================================================================================
-- 6. NOVO PAC SELEÇÕES
-- ====================================================================================
selecoes AS (
  SELECT
    (SELECT COALESCE(SUM(CASE WHEN modalidade = 'Creches' THEN 1 ELSE 0 END),0) FROM `br-mec-segape.projeto_painel_ministro.painel_novopac_selecoes_consolidado` WHERE sigla_uf = target_uf AND UPPER(TRIM(municipio)) = UPPER(target_mun_uf) AND situacao NOT IN ('Prop. Cancelada','Desclassificado/ Perda De Prazo','Convenio Anulado','Convenio Rescindido')) AS cr_m,
    (SELECT COALESCE(SUM(CASE WHEN modalidade = 'Creches' THEN valor_repasse ELSE 0 END),0) FROM `br-mec-segape.projeto_painel_ministro.painel_novopac_selecoes_consolidado` WHERE sigla_uf = target_uf AND UPPER(TRIM(municipio)) = UPPER(target_mun_uf) AND situacao NOT IN ('Prop. Cancelada','Desclassificado/ Perda De Prazo','Convenio Anulado','Convenio Rescindido')) AS vcr_m,
    (SELECT COALESCE(SUM(CASE WHEN modalidade = 'Escolas Tempo Integral' THEN 1 ELSE 0 END),0) FROM `br-mec-segape.projeto_painel_ministro.painel_novopac_selecoes_consolidado` WHERE sigla_uf = target_uf AND UPPER(TRIM(municipio)) = UPPER(target_mun_uf) AND situacao NOT IN ('Prop. Cancelada','Desclassificado/ Perda De Prazo','Convenio Anulado','Convenio Rescindido')) AS eti_m,
    (SELECT COALESCE(SUM(CASE WHEN modalidade = 'Escolas Tempo Integral' THEN valor_repasse ELSE 0 END),0) FROM `br-mec-segape.projeto_painel_ministro.painel_novopac_selecoes_consolidado` WHERE sigla_uf = target_uf AND UPPER(TRIM(municipio)) = UPPER(target_mun_uf) AND situacao NOT IN ('Prop. Cancelada','Desclassificado/ Perda De Prazo','Convenio Anulado','Convenio Rescindido')) AS veti_m,
    (SELECT COALESCE(SUM(CASE WHEN modalidade = 'Ônibus' THEN 1 ELSE 0 END),0) FROM `br-mec-segape.projeto_painel_ministro.painel_novopac_selecoes_consolidado` WHERE sigla_uf = target_uf AND UPPER(TRIM(municipio)) = UPPER(target_mun_uf) AND situacao NOT IN ('Prop. Cancelada','Desclassificado/ Perda De Prazo','Convenio Anulado','Convenio Rescindido')) AS on_m,
    (SELECT COALESCE(SUM(CASE WHEN modalidade = 'Ônibus' THEN valor_investimento ELSE 0 END),0) FROM `br-mec-segape.projeto_painel_ministro.painel_novopac_selecoes_consolidado` WHERE sigla_uf = target_uf AND UPPER(TRIM(municipio)) = UPPER(target_mun_uf) AND situacao NOT IN ('Prop. Cancelada','Desclassificado/ Perda De Prazo','Convenio Anulado','Convenio Rescindido')) AS von_m,
   
    (SELECT COALESCE(SUM(CASE WHEN modalidade = 'Creches' THEN 1 ELSE 0 END),0) FROM `br-mec-segape.projeto_painel_ministro.painel_novopac_selecoes_consolidado` WHERE sigla_uf = target_uf AND id = '99' AND situacao NOT IN ('Prop. Cancelada','Desclassificado/ Perda De Prazo','Convenio Anulado','Convenio Rescindido')) AS cr_e,
    (SELECT COALESCE(SUM(CASE WHEN modalidade = 'Creches' THEN valor_repasse ELSE 0 END),0) FROM `br-mec-segape.projeto_painel_ministro.painel_novopac_selecoes_consolidado` WHERE sigla_uf = target_uf AND id = '99' AND situacao NOT IN ('Prop. Cancelada','Desclassificado/ Perda De Prazo','Convenio Anulado','Convenio Rescindido')) AS vcr_e,
    (SELECT COALESCE(SUM(CASE WHEN modalidade = 'Escolas Tempo Integral' THEN 1 ELSE 0 END),0) FROM `br-mec-segape.projeto_painel_ministro.painel_novopac_selecoes_consolidado` WHERE sigla_uf = target_uf AND id = '99' AND situacao NOT IN ('Prop. Cancelada','Desclassificado/ Perda De Prazo','Convenio Anulado','Convenio Rescindido')) AS eti_e,
    (SELECT COALESCE(SUM(CASE WHEN modalidade = 'Escolas Tempo Integral' THEN valor_repasse ELSE 0 END),0) FROM `br-mec-segape.projeto_painel_ministro.painel_novopac_selecoes_consolidado` WHERE sigla_uf = target_uf AND id = '99' AND situacao NOT IN ('Prop. Cancelada','Desclassificado/ Perda De Prazo','Convenio Anulado','Convenio Rescindido')) AS veti_e,
    (SELECT COALESCE(SUM(CASE WHEN modalidade = 'Ônibus' THEN 1 ELSE 0 END),0) FROM `br-mec-segape.projeto_painel_ministro.painel_novopac_selecoes_consolidado` WHERE sigla_uf = target_uf AND id = '99' AND situacao NOT IN ('Prop. Cancelada','Desclassificado/ Perda De Prazo','Convenio Anulado','Convenio Rescindido')) AS on_e,
    (SELECT COALESCE(SUM(CASE WHEN modalidade = 'Ônibus' THEN valor_investimento ELSE 0 END),0) FROM `br-mec-segape.projeto_painel_ministro.painel_novopac_selecoes_consolidado` WHERE sigla_uf = target_uf AND id = '99' AND situacao NOT IN ('Prop. Cancelada','Desclassificado/ Perda De Prazo','Convenio Anulado','Convenio Rescindido')) AS von_e
),

-- ====================================================================================
-- 7. SESU
-- ====================================================================================
sesu AS (
  SELECT
    (SELECT COALESCE(SUM(CASE WHEN categoria = 'Consolidação' THEN valor_previsto ELSE 0 END),0) FROM `br-mec-segape.projeto_painel_ministro.painel_novopac_sesu` WHERE sigla_uf = target_uf AND UPPER(TRIM(municipio_obra)) = UPPER(target_mun) AND id >= '99') AS cons_m,
    (SELECT COALESCE(SUM(CASE WHEN categoria = 'Expansão' THEN valor_previsto ELSE 0 END),0) FROM `br-mec-segape.projeto_painel_ministro.painel_novopac_sesu` WHERE sigla_uf = target_uf AND UPPER(TRIM(municipio_obra)) = UPPER(target_mun) AND id >= '99') AS exp_m,
    (SELECT COALESCE(SUM(CASE WHEN categoria = 'Consolidação' THEN valor_previsto ELSE 0 END),0) FROM `br-mec-segape.projeto_painel_ministro.painel_novopac_sesu` WHERE sigla_uf = target_uf AND id = '99') AS cons_e,
    (SELECT COALESCE(SUM(CASE WHEN categoria = 'Expansão' THEN valor_previsto ELSE 0 END),0) FROM `br-mec-segape.projeto_painel_ministro.painel_novopac_sesu` WHERE sigla_uf = target_uf AND id = '99') AS exp_e,
    (SELECT COALESCE(SUM(valor_previsto),0) FROM `br-mec-segape.projeto_painel_ministro.painel_novopac_sesu` WHERE sigla_uf = target_uf AND id = '99') AS tot_e
),

-- ====================================================================================
-- 8. SETEC (Deduplicado via DISTINCT para corrigir triplicação de valores)
-- ====================================================================================
setec AS (
  SELECT
    (SELECT COALESCE(SUM(v_prev),0) FROM (SELECT DISTINCT municipio_obra, categoria_resumido, valor_previsto AS v_prev FROM `br-mec-segape.projeto_painel_ministro.painel_novopac_setec` WHERE sigla_uf = target_uf AND UPPER(TRIM(municipio_obra)) = UPPER(target_mun) AND categoria_resumido = 'Consolidação')) AS cons_m,
    (SELECT COALESCE(SUM(v_prev),0) FROM (SELECT DISTINCT municipio_obra, categoria_resumido, valor_previsto AS v_prev FROM `br-mec-segape.projeto_painel_ministro.painel_novopac_setec` WHERE sigla_uf = target_uf AND UPPER(TRIM(municipio_obra)) = UPPER(target_mun) AND categoria_resumido = 'Expansão')) AS exp_m,
    (SELECT COALESCE(SUM(CASE WHEN categoria_resumido = 'Consolidação' THEN valor_previsto ELSE 0 END),0) FROM `br-mec-segape.projeto_painel_ministro.painel_novopac_setec` WHERE sigla_uf = target_uf AND id = '99') AS cons_e,
    (SELECT COALESCE(SUM(CASE WHEN categoria_resumido = 'Expansão' THEN valor_previsto ELSE 0 END),0) FROM `br-mec-segape.projeto_painel_ministro.painel_novopac_setec` WHERE sigla_uf = target_uf AND id = '99') AS exp_e,
    (SELECT COALESCE(SUM(valor_previsto),0) FROM `br-mec-segape.projeto_painel_ministro.painel_novopac_setec` WHERE sigla_uf = target_uf AND id = '99') AS tot_e
),

-- ====================================================================================
-- 9. HU (Hospitais Universitários)
-- ====================================================================================
hu AS (
  SELECT
    (SELECT COALESCE(SUM(valor_novo_pac),0) FROM `br-mec-segape.projeto_painel_ministro.painel_novopac_ebserh` WHERE sigla_uf = target_uf AND UPPER(TRIM(municipio)) = UPPER(target_mun_uf)) AS val_m,
    (SELECT COALESCE(SUM(valor_novo_pac),0) FROM `br-mec-segape.projeto_painel_ministro.painel_novopac_ebserh` WHERE sigla_uf = target_uf AND id = '99') AS val_e
),

-- ====================================================================================
-- 10. FUNDEB
-- ====================================================================================
fundeb AS (
  SELECT
    (SELECT COALESCE(SUM(CASE WHEN ano = 2022 THEN valor ELSE 0 END),0) FROM `br-mec-segape.indicador_politica_fundeb_base.fundeb_base_repasse_estimativa` WHERE sigla_uf = target_uf AND status = 'Realizado' AND UPPER(TRIM(nome_entidade)) = UPPER(target_mun)) AS v22_m,
    (SELECT COALESCE(SUM(CASE WHEN ano = 2023 THEN valor ELSE 0 END),0) FROM `br-mec-segape.indicador_politica_fundeb_base.fundeb_base_repasse_estimativa` WHERE sigla_uf = target_uf AND status = 'Realizado' AND UPPER(TRIM(nome_entidade)) = UPPER(target_mun)) AS v23_m,
    (SELECT COALESCE(SUM(CASE WHEN ano = 2024 THEN valor ELSE 0 END),0) FROM `br-mec-segape.indicador_politica_fundeb_base.fundeb_base_repasse_estimativa` WHERE sigla_uf = target_uf AND status = 'Realizado' AND UPPER(TRIM(nome_entidade)) = UPPER(target_mun)) AS v24_m,
    (SELECT COALESCE(SUM(CASE WHEN ano = 2025 THEN valor ELSE 0 END),0) FROM `br-mec-segape.indicador_politica_fundeb_base.fundeb_base_repasse_estimativa` WHERE sigla_uf = target_uf AND status = 'Realizado' AND UPPER(TRIM(nome_entidade)) = UPPER(target_mun)) AS v25_m,
    (SELECT COALESCE(SUM(CASE WHEN tipo_transferencia = 'Complementação VAAF' AND ano = 2026 THEN valor ELSE 0 END),0) FROM `br-mec-segape.indicador_politica_fundeb_base.fundeb_base_repasse_estimativa` WHERE sigla_uf = target_uf AND status = 'Realizado' AND UPPER(TRIM(nome_entidade)) = UPPER(target_mun)) AS vaaf_m,
    (SELECT COALESCE(SUM(CASE WHEN tipo_transferencia = 'Complementação VAAT' AND ano = 2026 THEN valor ELSE 0 END),0) FROM `br-mec-segape.indicador_politica_fundeb_base.fundeb_base_repasse_estimativa` WHERE sigla_uf = target_uf AND status = 'Realizado' AND UPPER(TRIM(nome_entidade)) = UPPER(target_mun)) AS vaat_m,
    (SELECT COALESCE(SUM(CASE WHEN tipo_transferencia = 'Complementação VAAR' AND ano = 2026 THEN valor ELSE 0 END),0) FROM `br-mec-segape.indicador_politica_fundeb_base.fundeb_base_repasse_estimativa` WHERE sigla_uf = target_uf AND status = 'Realizado' AND UPPER(TRIM(nome_entidade)) = UPPER(target_mun)) AS vaar_m,
    (SELECT COALESCE(SUM(repasse),0) FROM `br-mec-segape.projeto_painel_ministro.painel_fundeb` WHERE uf = target_uf AND ano = 2026 AND status = 'Realizado' AND UPPER(TRIM(municipio)) = UPPER(target_mun_uf)) AS v26_m,
    
    (SELECT COALESCE(SUM(CASE WHEN ano = 2022 THEN valor ELSE 0 END),0) FROM `br-mec-segape.indicador_politica_fundeb_base.fundeb_base_repasse_estimativa` WHERE sigla_uf = target_uf AND status = 'Realizado') AS v22_e,
    (SELECT COALESCE(SUM(CASE WHEN ano = 2023 THEN valor ELSE 0 END),0) FROM `br-mec-segape.indicador_politica_fundeb_base.fundeb_base_repasse_estimativa` WHERE sigla_uf = target_uf AND status = 'Realizado') AS v23_e,
    (SELECT COALESCE(SUM(CASE WHEN ano = 2024 THEN valor ELSE 0 END),0) FROM `br-mec-segape.indicador_politica_fundeb_base.fundeb_base_repasse_estimativa` WHERE sigla_uf = target_uf AND status = 'Realizado') AS v24_e,
    (SELECT COALESCE(SUM(CASE WHEN ano = 2025 THEN valor ELSE 0 END),0) FROM `br-mec-segape.indicador_politica_fundeb_base.fundeb_base_repasse_estimativa` WHERE sigla_uf = target_uf AND status = 'Realizado') AS v25_e,
    (SELECT COALESCE(SUM(CASE WHEN tipo_transferencia = 'Complementação VAAF' AND ano = 2026 THEN valor ELSE 0 END),0) FROM `br-mec-segape.indicador_politica_fundeb_base.fundeb_base_repasse_estimativa` WHERE sigla_uf = target_uf AND status = 'Realizado') AS vaaf_e,
    (SELECT COALESCE(SUM(CASE WHEN tipo_transferencia = 'Complementação VAAT' AND ano = 2026 THEN valor ELSE 0 END),0) FROM `br-mec-segape.indicador_politica_fundeb_base.fundeb_base_repasse_estimativa` WHERE sigla_uf = target_uf AND status = 'Realizado') AS vaat_e,
    (SELECT COALESCE(SUM(CASE WHEN tipo_transferencia = 'Complementação VAAR' AND ano = 2026 THEN valor ELSE 0 END),0) FROM `br-mec-segape.indicador_politica_fundeb_base.fundeb_base_repasse_estimativa` WHERE sigla_uf = target_uf AND status = 'Realizado') AS vaar_e,
    (SELECT COALESCE(SUM(repasse),0) FROM `br-mec-segape.projeto_painel_ministro.painel_fundeb` WHERE uf = target_uf AND ano = 2026 AND status = 'Realizado' AND municipio = 'Todos' AND estado != 'Todos') AS v26_e
),

-- ====================================================================================
-- 11. PNAE e 12. PNATE
-- Ajuste para coerência com o BriefingEstado:
--   - escolas/alunos continuam como retrato município x estado;
--   - repasse financeiro passa a ser retornado por ano desde 2022;
--   - a referência comparativa deixa de ser Brasil e passa a ser ESTADO.
-- ====================================================================================
pnae_base AS (
  SELECT
    (SELECT COALESCE(SUM(qtd_escola),0)
     FROM `br-mec-segape.projeto_painel_ministro.painel_pnae` p
     JOIN mapeamento_uf mp ON UPPER(p.estado) = mp.nome
     WHERE mp.sigla_uf = target_uf
       AND UPPER(TRIM(p.municipio)) = UPPER(target_mun_uf)) AS esc_m,
    (SELECT COALESCE(SUM(p.qtd_escola),0)
     FROM `br-mec-segape.projeto_painel_ministro.painel_pnae` p
     JOIN mapeamento_uf mp ON UPPER(p.estado) = mp.nome
     WHERE mp.sigla_uf = target_uf
       AND p.municipio = 'Todos'
       AND p.estado != 'Todos') AS esc_e
),
pnae_repasse_mun_ano AS (
  SELECT
    LEFT(dt_ref,4) AS ano,
    SUM(pnae_03_val_repasse) AS valor_m
  FROM `br-mec-segape.projeto_gaia.gaia_pnae`
  WHERE uf = target_uf
    AND UPPER(TRIM(nome)) = UPPER(target_mun)
    AND UPPER(pnae_04_dependencia_adm) = 'MUNICIPAL'
  GROUP BY 1
),
pnae_repasse_estado_ano AS (
  SELECT
    LEFT(dt_ref,4) AS ano,
    SUM(pnae_03_val_repasse) AS valor_e
  FROM `br-mec-segape.projeto_gaia.gaia_pnae`
  WHERE uf = target_uf
  GROUP BY 1
),
pnae_valor_ano AS (
  SELECT CONCAT(
    STRING_AGG(CONCAT(e.ano, ': ',
      CASE WHEN COALESCE(m.valor_m,0) >= 1e9 THEN REPLACE(FORMAT('R$ %.2f bilhões', COALESCE(m.valor_m,0)/1e9), '.', ',')
           WHEN COALESCE(m.valor_m,0) >= 1e6 THEN REPLACE(FORMAT('R$ %.2f milhões', COALESCE(m.valor_m,0)/1e6), '.', ',')
           WHEN COALESCE(m.valor_m,0) >= 1e3 THEN REPLACE(FORMAT('R$ %.2f mil', COALESCE(m.valor_m,0)/1e3), '.', ',')
           ELSE 'R$ 0' END
    ), ' | ' ORDER BY e.ano),
    ' - ESTADO: ',
    STRING_AGG(CONCAT(e.ano, ': ',
      CASE WHEN COALESCE(e.valor_e,0) >= 1e9 THEN REPLACE(FORMAT('R$ %.2f bilhões', COALESCE(e.valor_e,0)/1e9), '.', ',')
           ELSE REPLACE(FORMAT('R$ %.2f milhões', COALESCE(e.valor_e,0)/1e6), '.', ',') END
    ), ' | ' ORDER BY e.ano)
  ) AS valor_ano
  FROM pnae_repasse_estado_ano e
  LEFT JOIN pnae_repasse_mun_ano m USING(ano)
),
pnae AS (
  SELECT b.esc_m, b.esc_e, v.valor_ano
  FROM pnae_base b CROSS JOIN pnae_valor_ano v
),

pnate_base AS (
  SELECT
    (SELECT COALESCE(SUM(p.qtd_aluno),0)
     FROM `br-mec-segape.projeto_painel_ministro.painel_pnate` p
     JOIN `br-mec-segape.educacao_dados_mestres.municipio` m
       ON CAST(p.id AS STRING) = CAST(m.id_municipio AS STRING)
     WHERE m.sigla_uf = target_uf
       AND LENGTH(CAST(p.id AS STRING)) = 7
       AND UPPER(TRIM(m.nome)) = UPPER(target_mun)) AS al_m,
    (SELECT COALESCE(SUM(p.qtd_aluno),0)
     FROM `br-mec-segape.projeto_painel_ministro.painel_pnate` p
     JOIN mapeamento_uf m ON UPPER(p.estado) = m.nome
     WHERE m.sigla_uf = target_uf
       AND SAFE_CAST(p.id AS INT64) < 99) AS al_e
),
pnate_repasse_mun_ano AS (
  SELECT
    LEFT(dt_ref,4) AS ano,
    SUM(COALESCE(pnate_03_val_repasse_municipio,0) + COALESCE(pnate_04_val_repasse_estado,0)) AS valor_m
  FROM `br-mec-segape.projeto_gaia.gaia_pnate`
  WHERE uf = target_uf
    AND UPPER(TRIM(nome)) = UPPER(target_mun)
  GROUP BY 1
),
pnate_repasse_estado_ano AS (
  SELECT
    LEFT(dt_ref,4) AS ano,
    SUM(COALESCE(pnate_03_val_repasse_municipio,0) + COALESCE(pnate_04_val_repasse_estado,0)) AS valor_e
  FROM `br-mec-segape.projeto_gaia.gaia_pnate`
  WHERE uf = target_uf
  GROUP BY 1
),
pnate_valor_ano AS (
  SELECT CONCAT(
    STRING_AGG(CONCAT(e.ano, ': ',
      CASE WHEN COALESCE(m.valor_m,0) >= 1e9 THEN REPLACE(FORMAT('R$ %.2f bilhões', COALESCE(m.valor_m,0)/1e9), '.', ',')
           WHEN COALESCE(m.valor_m,0) >= 1e6 THEN REPLACE(FORMAT('R$ %.2f milhões', COALESCE(m.valor_m,0)/1e6), '.', ',')
           WHEN COALESCE(m.valor_m,0) >= 1e3 THEN REPLACE(FORMAT('R$ %.2f mil', COALESCE(m.valor_m,0)/1e3), '.', ',')
           ELSE 'R$ 0' END
    ), ' | ' ORDER BY e.ano),
    ' - ESTADO: ',
    STRING_AGG(CONCAT(e.ano, ': ',
      CASE WHEN COALESCE(e.valor_e,0) >= 1e9 THEN REPLACE(FORMAT('R$ %.2f bilhões', COALESCE(e.valor_e,0)/1e9), '.', ',')
           ELSE REPLACE(FORMAT('R$ %.2f milhões', COALESCE(e.valor_e,0)/1e6), '.', ',') END
    ), ' | ' ORDER BY e.ano)
  ) AS valor_ano
  FROM pnate_repasse_estado_ano e
  LEFT JOIN pnate_repasse_mun_ano m USING(ano)
),
pnate AS (
  SELECT b.al_m, b.al_e, v.valor_ano
  FROM pnate_base b CROSS JOIN pnate_valor_ano v
),

-- ====================================================================================
-- 13. INSTITUTOS FEDERAIS E UNIVERSIDADES
-- ====================================================================================
inst AS (
  SELECT
    (SELECT COALESCE(SUM(pnp.numero_matriculas),0) FROM `br-mec-segape.educacao_politica_pnp_painel.pnp_painel_situacao_matricula` pnp JOIN `br-mec-segape.educacao_politica_pnp_painel.pnp_painel_instituicao` p ON p.chave_unidade = pnp.chave_unidade JOIN `br-mec-segape.educacao_politica_pnp_painel.pnp_painel_organizacao_administrativa` e ON e.chave_unidade = pnp.chave_unidade WHERE pnp.ano = 2024 AND e.organizacao_administrativa IN ('Institutos') AND p.sigla_uf = target_uf AND UPPER(TRIM(p.municipio)) = UPPER(target_mun)) AS mat_m,
    (SELECT COUNT(DISTINCT p.id_instituicao) FROM `br-mec-segape.educacao_politica_pnp_painel.pnp_painel_situacao_matricula` pnp JOIN `br-mec-segape.educacao_politica_pnp_painel.pnp_painel_instituicao` p ON p.chave_unidade = pnp.chave_unidade JOIN `br-mec-segape.educacao_politica_pnp_painel.pnp_painel_organizacao_administrativa` e ON e.chave_unidade = pnp.chave_unidade WHERE pnp.ano = 2024 AND e.organizacao_administrativa IN ('Institutos') AND p.sigla_uf = target_uf AND UPPER(TRIM(p.municipio)) = UPPER(target_mun)) AS if_m,
    (SELECT COUNT(DISTINCT pnp.id_unidade) FROM `br-mec-segape.educacao_politica_pnp_painel.pnp_painel_situacao_matricula` pnp JOIN `br-mec-segape.educacao_politica_pnp_painel.pnp_painel_instituicao` p ON p.chave_unidade = pnp.chave_unidade JOIN `br-mec-segape.educacao_politica_pnp_painel.pnp_painel_organizacao_administrativa` e ON e.chave_unidade = pnp.chave_unidade WHERE pnp.ano = 2024 AND e.organizacao_administrativa IN ('Institutos') AND p.sigla_uf = target_uf AND UPPER(TRIM(p.municipio)) = UPPER(target_mun)) AS campi_m,
    (SELECT COALESCE(SUM(pnp.numero_matriculas),0) FROM `br-mec-segape.educacao_politica_pnp_painel.pnp_painel_situacao_matricula` pnp JOIN `br-mec-segape.educacao_politica_pnp_painel.pnp_painel_instituicao` p ON p.chave_unidade = pnp.chave_unidade JOIN `br-mec-segape.educacao_politica_pnp_painel.pnp_painel_organizacao_administrativa` e ON e.chave_unidade = pnp.chave_unidade WHERE pnp.ano = 2024 AND e.organizacao_administrativa IN ('Institutos') AND p.sigla_uf = target_uf) AS mat_e,
    (SELECT COUNT(DISTINCT p.id_instituicao) FROM `br-mec-segape.educacao_politica_pnp_painel.pnp_painel_situacao_matricula` pnp JOIN `br-mec-segape.educacao_politica_pnp_painel.pnp_painel_instituicao` p ON p.chave_unidade = pnp.chave_unidade JOIN `br-mec-segape.educacao_politica_pnp_painel.pnp_painel_organizacao_administrativa` e ON e.chave_unidade = pnp.chave_unidade WHERE pnp.ano = 2024 AND e.organizacao_administrativa IN ('Institutos') AND p.sigla_uf = target_uf) AS if_e,
    (SELECT COUNT(DISTINCT pnp.id_unidade) FROM `br-mec-segape.educacao_politica_pnp_painel.pnp_painel_situacao_matricula` pnp JOIN `br-mec-segape.educacao_politica_pnp_painel.pnp_painel_instituicao` p ON p.chave_unidade = pnp.chave_unidade JOIN `br-mec-segape.educacao_politica_pnp_painel.pnp_painel_organizacao_administrativa` e ON e.chave_unidade = pnp.chave_unidade WHERE pnp.ano = 2024 AND e.organizacao_administrativa IN ('Institutos') AND p.sigla_uf = target_uf) AS campi_e
),
uni AS (
  SELECT
    (SELECT COUNT(DISTINCT campus) FROM `br-mec-segape.educacao_dados_mestres.campus_universidade_federal` WHERE sigla_uf = target_uf AND UPPER(TRIM(municipio)) = UPPER(target_mun)) AS campi_m,
    (SELECT COUNT(DISTINCT ies.id_ies) FROM `br-mec-segape.educacao_inep_dados_abertos.inep_censo_educacao_superior_curso` curso JOIN `br-mec-segape.educacao_inep_dados_abertos.inep_censo_educacao_superior_ies` ies ON curso.id_ies = ies.id_ies AND ies.ano_censo = 2024 WHERE curso.ano_censo = 2024 AND curso.id_tipo_nivel_academico = 1 AND curso.id_tipo_categoria_administrativa = 1 AND curso.id_tipo_organizacao_academica = 1 AND curso.id_tipo_modalidade_ensino IN (1, 2) AND ies.sigla_uf_ies = target_uf AND UPPER(TRIM(curso.municipio)) = UPPER(target_mun)) AS inst_m,
    (SELECT COALESCE(SUM(curso.quantidade_matriculas),0) FROM `br-mec-segape.educacao_inep_dados_abertos.inep_censo_educacao_superior_curso` curso JOIN `br-mec-segape.educacao_inep_dados_abertos.inep_censo_educacao_superior_ies` ies ON curso.id_ies = ies.id_ies AND ies.ano_censo = 2024 WHERE curso.ano_censo = 2024 AND curso.id_tipo_nivel_academico = 1 AND curso.id_tipo_categoria_administrativa = 1 AND curso.id_tipo_organizacao_academica = 1 AND curso.id_tipo_modalidade_ensino IN (1, 2) AND ies.sigla_uf_ies = target_uf AND UPPER(TRIM(curso.municipio)) = UPPER(target_mun)) AS mat_m,
    (SELECT COUNT(DISTINCT CONCAT(sigla_ies, '|', campus)) FROM `sandbox_segape_dmape.projeto_painel_ministro_painel_universidades_campus` WHERE sigla_uf = target_uf ) AS campi_e, 
    --AND status_funcionamento NOT IN ('Em Transformação Para Campus', 'Previsto - Expansão')) AS campi_e,
    (SELECT COUNT(DISTINCT ies.id_ies) FROM `br-mec-segape.educacao_inep_dados_abertos.inep_censo_educacao_superior_curso` curso JOIN `br-mec-segape.educacao_inep_dados_abertos.inep_censo_educacao_superior_ies` ies ON curso.id_ies = ies.id_ies AND ies.ano_censo = 2024 WHERE curso.ano_censo = 2024 AND curso.id_tipo_nivel_academico = 1 AND curso.id_tipo_categoria_administrativa = 1 AND curso.id_tipo_organizacao_academica = 1 AND curso.id_tipo_modalidade_ensino IN (1, 2) AND ies.sigla_uf_ies = target_uf) AS inst_e,
    (SELECT COALESCE(SUM(curso.quantidade_matriculas),0) FROM `br-mec-segape.educacao_inep_dados_abertos.inep_censo_educacao_superior_curso` curso JOIN `br-mec-segape.educacao_inep_dados_abertos.inep_censo_educacao_superior_ies` ies ON curso.id_ies = ies.id_ies AND ies.ano_censo = 2024 WHERE curso.ano_censo = 2024 AND curso.id_tipo_nivel_academico = 1 AND curso.id_tipo_categoria_administrativa = 1 AND curso.id_tipo_organizacao_academica = 1 AND curso.id_tipo_modalidade_ensino IN (1, 2) AND curso.sigla_uf = target_uf) AS mat_e
),

-- ====================================================================================
-- 14. INDICADORES DE RESULTADO SÉRIE HISTÓRICA
-- ====================================================================================
ind_eti_base AS (
  SELECT 
    CASE WHEN id = '99' THEN 'BR' ELSE id END AS id_norm,
    ano,
    quantidade_matricula_integral AS qtd_integral,
    quantidade_matricula_integral * 100.0 / NULLIF(quantidade_matricula, 0) AS pct
  FROM `br-mec-segape.projeto_painel_ministro.painel_matricula_integral_percentual`
  WHERE ano IN (2019, 2022, 2023, 2025)
    AND etapa = 'Todas as etapas'
),
ind_eti_m AS (
  SELECT
    MAX(CASE WHEN b.ano = 2019 THEN b.pct END) AS pct_2019,
    MAX(CASE WHEN b.ano = 2019 THEN b.qtd_integral END) AS qtd_2019,

    MAX(CASE WHEN b.ano = 2022 THEN b.pct END) AS pct_2022,
    MAX(CASE WHEN b.ano = 2022 THEN b.qtd_integral END) AS qtd_2022,

    MAX(CASE WHEN b.ano = 2023 THEN b.pct END) AS pct_2023,
    MAX(CASE WHEN b.ano = 2023 THEN b.qtd_integral END) AS qtd_2023,

    MAX(CASE WHEN b.ano = 2025 THEN b.pct END) AS pct_2026,
    MAX(CASE WHEN b.ano = 2025 THEN b.qtd_integral END) AS qtd_2026
  FROM ind_eti_base b
  JOIN `br-mec-segape.educacao_dados_mestres.municipio` m
    ON b.id_norm = CAST(m.id_municipio AS STRING)
  WHERE m.sigla_uf = target_uf
    AND UPPER(TRIM(m.nome)) = UPPER(target_mun)
),
ind_eti_e AS (
  SELECT
    MAX(CASE WHEN b.ano = 2019 THEN b.pct END) AS pct_2019,
    MAX(CASE WHEN b.ano = 2019 THEN b.qtd_integral END) AS qtd_2019,

    MAX(CASE WHEN b.ano = 2022 THEN b.pct END) AS pct_2022,
    MAX(CASE WHEN b.ano = 2022 THEN b.qtd_integral END) AS qtd_2022,

    MAX(CASE WHEN b.ano = 2023 THEN b.pct END) AS pct_2023,
    MAX(CASE WHEN b.ano = 2023 THEN b.qtd_integral END) AS qtd_2023,

    MAX(CASE WHEN b.ano = 2025 THEN b.pct END) AS pct_2026,
    MAX(CASE WHEN b.ano = 2025 THEN b.qtd_integral END) AS qtd_2026
  FROM ind_eti_base b
  JOIN (SELECT DISTINCT id_uf, sigla_uf FROM `br-mec-segape.educacao_dados_mestres.municipio`) uf
    ON b.id_norm = CAST(uf.id_uf AS STRING)
  WHERE uf.sigla_uf = target_uf
),
ind_eti AS (
  SELECT CONCAT(
      '2019: ',
        IFNULL(REPLACE(FORMAT('%.2f', m.pct_2019), '.', ','), '-'), '% (',
        IFNULL(REPLACE(FORMAT("%'d", CAST(m.qtd_2019 AS INT64)), ',', '.'), '-'), ' matrículas)',

      ' | 2022: ',
        IFNULL(REPLACE(FORMAT('%.2f', m.pct_2022), '.', ','), '-'), '% (',
        IFNULL(REPLACE(FORMAT("%'d", CAST(m.qtd_2022 AS INT64)), ',', '.'), '-'), ' matrículas)',

      ' | 2023: ',
        IFNULL(REPLACE(FORMAT('%.2f', m.pct_2023), '.', ','), '-'), '% (',
        IFNULL(REPLACE(FORMAT("%'d", CAST(m.qtd_2023 AS INT64)), ',', '.'), '-'), ' matrículas)',

      ' | 2026: ',
        IFNULL(REPLACE(FORMAT('%.2f', m.pct_2026), '.', ','), '-'), '% (',
        IFNULL(REPLACE(FORMAT("%'d", CAST(m.qtd_2026 AS INT64)), ',', '.'), '-'), ' matrículas)(*)',

      ' || ESTADO: 2019: ',
        IFNULL(REPLACE(FORMAT('%.2f', e.pct_2019), '.', ','), '-'), '% (',
        IFNULL(REPLACE(FORMAT("%'d", CAST(e.qtd_2019 AS INT64)), ',', '.'), '-'), ' matrículas)',

      ' | 2022: ',
        IFNULL(REPLACE(FORMAT('%.2f', e.pct_2022), '.', ','), '-'), '% (',
        IFNULL(REPLACE(FORMAT("%'d", CAST(e.qtd_2022 AS INT64)), ',', '.'), '-'), ' matrículas)',

      ' | 2023: ',
        IFNULL(REPLACE(FORMAT('%.2f', e.pct_2023), '.', ','), '-'), '% (',
        IFNULL(REPLACE(FORMAT("%'d", CAST(e.qtd_2023 AS INT64)), ',', '.'), '-'), ' matrículas)',

      ' | 2026: ',
        IFNULL(REPLACE(FORMAT('%.2f', e.pct_2026), '.', ','), '-'), '% (',
        IFNULL(REPLACE(FORMAT("%'d", CAST(e.qtd_2026 AS INT64)), ',', '.'), '-'), ' matrículas)',
      ' (*) 2026 com dado mais recente de 2025; 2026 ainda não publicado.'
    ) AS eti_serie_historica_alunos
  FROM ind_eti_m m CROSS JOIN ind_eti_e e
),

ind_dis_m AS (
  SELECT MAX(CASE WHEN b.ano = 2022 THEN b.taxa_distorcao END) AS pct_23, MAX(CASE WHEN b.ano = 2025 THEN b.taxa_distorcao END) AS pct_25
  FROM `br-mec-segape.projeto_painel_ministro.painel_taxa_distorcao` b JOIN `br-mec-segape.educacao_dados_mestres.municipio` m ON b.id = CAST(m.id_municipio AS STRING) WHERE m.sigla_uf = target_uf AND UPPER(TRIM(m.nome)) = UPPER(target_mun) AND b.etapa = 'Ensino Médio'
),
ind_dis_e AS (
  SELECT MAX(CASE WHEN b.ano = 2022 THEN b.taxa_distorcao END) AS pct_23, MAX(CASE WHEN b.ano = 2025 THEN b.taxa_distorcao END) AS pct_25
  FROM `br-mec-segape.projeto_painel_ministro.painel_taxa_distorcao` b JOIN (SELECT DISTINCT id_uf, sigla_uf FROM `br-mec-segape.educacao_dados_mestres.municipio`) m ON b.id = CAST(m.id_uf AS STRING) WHERE m.sigla_uf = target_uf AND b.etapa = 'Ensino Médio'
),
ind_dis AS (
  SELECT CONCAT(
      'De ', REPLACE(FORMAT('%.2f', m.pct_23), '.', ','), '% em 2022 para ', REPLACE(FORMAT('%.2f', m.pct_25), '.', ','), '% em 2025 - ESTADO: De ', REPLACE(FORMAT('%.2f', e.pct_23), '.', ','), '% em 2022 para ', REPLACE(FORMAT('%.2f', e.pct_25), '.', ','), '% em 2025'
    ) AS distorcao_idade_serie
  FROM ind_dis_m m CROSS JOIN ind_dis_e e
),

rendimento_base AS (
  SELECT
    b.id,
    b.ano,
    b.tipo_taxa,
    b.valor
  FROM `br-mec-segape.projeto_painel_ministro.painel_rendimento` b
  WHERE b.ano IN (2023, 2024)
    AND b.etapa = 'Ensino Médio'
    AND b.tipo_taxa IN ('Reprovação', 'Abandono')
),
rendimento_m AS (
  SELECT
    MAX(CASE WHEN b.ano=2023 AND b.tipo_taxa='Reprovação' THEN b.valor END) AS reprov_ini,
    MAX(CASE WHEN b.ano=2024 AND b.tipo_taxa='Reprovação' THEN b.valor END) AS reprov_fim,
    MAX(CASE WHEN b.ano=2023 AND b.tipo_taxa='Abandono' THEN b.valor END) AS aband_ini,
    MAX(CASE WHEN b.ano=2024 AND b.tipo_taxa='Abandono' THEN b.valor END) AS aband_fim
  FROM rendimento_base b
  JOIN `br-mec-segape.educacao_dados_mestres.municipio` m
    ON b.id = CAST(m.id_municipio AS STRING)
  WHERE m.sigla_uf = target_uf
    AND UPPER(TRIM(m.nome)) = UPPER(target_mun)
),
rendimento_e AS (
  SELECT
    MAX(CASE WHEN b.ano=2023 AND b.tipo_taxa='Reprovação' THEN b.valor END) AS reprov_ini,
    MAX(CASE WHEN b.ano=2024 AND b.tipo_taxa='Reprovação' THEN b.valor END) AS reprov_fim,
    MAX(CASE WHEN b.ano=2023 AND b.tipo_taxa='Abandono' THEN b.valor END) AS aband_ini,
    MAX(CASE WHEN b.ano=2024 AND b.tipo_taxa='Abandono' THEN b.valor END) AS aband_fim
  FROM rendimento_base b
  JOIN (SELECT DISTINCT id_uf, sigla_uf FROM `br-mec-segape.educacao_dados_mestres.municipio`) m
    ON b.id = CAST(m.id_uf AS STRING)
  WHERE m.sigla_uf = target_uf
),
ind_ren AS (
  SELECT
    CONCAT('Ensino Médio: De ', REPLACE(FORMAT('%.2f', m.reprov_ini*100), '.', ','), '% em 2023 para ',
           REPLACE(FORMAT('%.2f', m.reprov_fim*100), '.', ','), '% em 2024 - ESTADO: De ',
           REPLACE(FORMAT('%.2f', e.reprov_ini*100), '.', ','), '% em 2023 para ',
           REPLACE(FORMAT('%.2f', e.reprov_fim*100), '.', ','), '% em 2024') AS taxa_reprovacao,
    CONCAT('Ensino Médio: De ', REPLACE(FORMAT('%.2f', m.aband_ini*100), '.', ','), '% em 2023 para ',
           REPLACE(FORMAT('%.2f', m.aband_fim*100), '.', ','), '% em 2024 - ESTADO: De ',
           REPLACE(FORMAT('%.2f', e.aband_ini*100), '.', ','), '% em 2023 para ',
           REPLACE(FORMAT('%.2f', e.aband_fim*100), '.', ','), '% em 2024') AS taxa_abandono_evasao
  FROM rendimento_m m CROSS JOIN rendimento_e e
),

ind_ica_m AS (
  SELECT MAX(CASE WHEN b.ano = 2023 THEN b.valor END) AS pct_23, MAX(CASE WHEN b.ano = 2025 THEN b.valor END) AS pct_25
  FROM `br-mec-segape.projeto_painel_ministro.painel_cnca_meta` b JOIN `br-mec-segape.educacao_dados_mestres.municipio` m ON b.id = CAST(m.id_municipio AS STRING) WHERE m.sigla_uf = target_uf AND UPPER(TRIM(m.nome)) = UPPER(target_mun) AND b.definicao_valor = 'REALIZADO - ICA'
),
ind_ica_e AS (
  SELECT MAX(CASE WHEN b.ano = 2023 THEN b.valor END) AS pct_23, MAX(CASE WHEN b.ano = 2025 THEN b.valor END) AS pct_25
  FROM `br-mec-segape.projeto_painel_ministro.painel_cnca_meta` b JOIN (SELECT DISTINCT id_uf, sigla_uf FROM `br-mec-segape.educacao_dados_mestres.municipio`) m ON b.id = CAST(m.id_uf AS STRING) WHERE m.sigla_uf = target_uf AND b.definicao_valor = 'REALIZADO - ICA'
),
ind_ica AS (
  SELECT CONCAT(
      'De ', REPLACE(FORMAT('%.2f', m.pct_23 * 100), '.', ','), '%* em 2023 para ', REPLACE(FORMAT('%g', m.pct_25 * 100), '.', ','), '% em 2025 - ESTADO: De ', REPLACE(FORMAT('%.2f', e.pct_23 * 100), '.', ','), '%* em 2023 para ', REPLACE(FORMAT('%g', e.pct_25 * 100), '.', ','), '% em 2025'
    ) AS ica_alfabetizacao
  FROM ind_ica_m m CROSS JOIN ind_ica_e e
)

-- ====================================================================================
-- SELECT FINAL (FORMATAÇÃO)
-- ====================================================================================
SELECT
  target_mun AS municipio,
  mun_ibge.cod_ibge AS cod_ibge,
  target_uf AS uf,
  CONCAT('BRIEFING – Visita Ministerial - ', target_mun, ' (', target_uf, ')') AS titulo,
  
  CONCAT(REPLACE(FORMAT("%'d", ec.con_m), ',', '.'), ' (', REPLACE(FORMAT("%.1f", ROUND(ec.con_m / NULLIF(ec.tot_m, 0) * 100, 1)), '.', ','), '%) - ESTADO: ', REPLACE(FORMAT("%'d", ec.con_e), ',', '.'), ' (', REPLACE(FORMAT("%.1f", ROUND(ec.con_e / NULLIF(ec.tot_e, 0) * 100, 1)), '.', ','), '%)') AS escolas_conectadas_nivel_4_5,
  
  CONCAT(REPLACE(FORMAT("%'d", CAST(eti.mat_m AS INT64)), ',', '.'), ' - ESTADO: ', REPLACE(FORMAT("%'d", CAST(eti.mat_e AS INT64)), ',', '.')) AS eti_matriculas_fomentadas,
  CONCAT(CASE WHEN eti.val_m >= 1e9 THEN REPLACE(FORMAT('R$ %.2f bilhões', eti.val_m/1e9), '.', ',') WHEN eti.val_m >= 1e6 THEN REPLACE(FORMAT('R$ %.2f milhões', eti.val_m/1e6), '.', ',') WHEN eti.val_m >= 1e3 THEN REPLACE(FORMAT('R$ %.2f mil', eti.val_m/1e3), '.', ',') ELSE REPLACE(FORMAT('R$ %.2f', CAST(eti.val_m AS FLOAT64)), '.', ',') END, ' - ESTADO: ', CASE WHEN eti.val_e >= 1e9 THEN REPLACE(FORMAT('R$ %.2f bilhões', eti.val_e/1e9), '.', ',') ELSE REPLACE(FORMAT('R$ %.2f milhões', eti.val_e/1e6), '.', ',') END) AS eti_valor_fomentado,
  
  CONCAT(REPLACE(FORMAT("%'d", CAST(c.cant_m AS INT64)), ',', '.'), ' - ESTADO: ', REPLACE(FORMAT("%'d", CAST(c.cant_e AS INT64)), ',', '.')) AS cnca_cantinhos,
  CONCAT(REPLACE(FORMAT("%'d", CAST(c.esc_m AS INT64)), ',', '.'), ' - ESTADO: ', REPLACE(FORMAT("%'d", CAST(c.esc_e AS INT64)), ',', '.')) AS cnca_escolas,
  
  -- Formatação Dinâmica Aplicada para CNCA
  CONCAT(CASE WHEN c.vcant_m >= 1e6 THEN REPLACE(FORMAT('R$ %.2f milhões', c.vcant_m/1e6), '.', ',') WHEN c.vcant_m >= 1e3 THEN REPLACE(FORMAT('R$ %.2f mil', c.vcant_m/1e3), '.', ',') ELSE 'R$ 0' END, ' - ESTADO: ', CASE WHEN c.vcant_e >= 1e6 THEN REPLACE(FORMAT('R$ %.2f milhões', c.vcant_e/1e6), '.', ',') WHEN c.vcant_e >= 1e3 THEN REPLACE(FORMAT('R$ %.2f mil', c.vcant_e/1e3), '.', ',') ELSE 'R$ 0' END) AS cnca_val_cantinhos,
  CONCAT(REPLACE(FORMAT("%'d", CAST(c.art_m AS INT64)), ',', '.'), ' - ESTADO: ', REPLACE(FORMAT("%'d", CAST(c.art_e AS INT64)), ',', '.')) AS cnca_articuladores,
  CONCAT(CASE WHEN c.vbol_m >= 1e6 THEN REPLACE(FORMAT('R$ %.2f milhões', c.vbol_m/1e6), '.', ',') WHEN c.vbol_m >= 1e3 THEN REPLACE(FORMAT('R$ %.2f mil', c.vbol_m/1e3), '.', ',') ELSE 'R$ 0' END, ' - ESTADO: ', CASE WHEN c.vbol_e >= 1e6 THEN REPLACE(FORMAT('R$ %.2f milhões', c.vbol_e/1e6), '.', ',') WHEN c.vbol_e >= 1e3 THEN REPLACE(FORMAT('R$ %.2f mil', c.vbol_e/1e3), '.', ',') ELSE 'R$ 0' END) AS cnca_val_articuladores,
  CONCAT(CASE WHEN c.vmat_m >= 1e6 THEN REPLACE(FORMAT('R$ %.2f milhões', c.vmat_m/1e6), '.', ',') WHEN c.vmat_m >= 1e3 THEN REPLACE(FORMAT('R$ %.2f mil', c.vmat_m/1e3), '.', ',') ELSE 'R$ 0' END, ' - ESTADO: ', CASE WHEN c.vmat_e >= 1e6 THEN REPLACE(FORMAT('R$ %.2f milhões', c.vmat_e/1e6), '.', ',') WHEN c.vmat_e >= 1e3 THEN REPLACE(FORMAT('R$ %.2f mil', c.vmat_e/1e3), '.', ',') ELSE 'R$ 0' END) AS cnca_val_materiais,
  CONCAT(CASE WHEN c.vform_m >= 1e6 THEN REPLACE(FORMAT('R$ %.2f milhões', c.vform_m/1e6), '.', ',') WHEN c.vform_m >= 1e3 THEN REPLACE(FORMAT('R$ %.2f mil', c.vform_m/1e3), '.', ',') ELSE 'R$ 0' END, ' - ESTADO: ', CASE WHEN c.vform_e >= 1e6 THEN REPLACE(FORMAT('R$ %.2f milhões', c.vform_e/1e6), '.', ',') WHEN c.vform_e >= 1e3 THEN REPLACE(FORMAT('R$ %.0f mil', c.vform_e/1e3), '.', ',') ELSE 'R$ 0' END) AS cnca_val_formacao,
  CONCAT(CASE WHEN (c.vcant_m + c.vbol_m + c.vmat_m + c.vform_m) >= 1e6 THEN REPLACE(FORMAT('R$ %.2f milhões', (c.vcant_m + c.vbol_m + c.vmat_m + c.vform_m)/1e6), '.', ',') WHEN (c.vcant_m + c.vbol_m + c.vmat_m + c.vform_m) >= 1e3 THEN REPLACE(FORMAT('R$ %.2f mil', (c.vcant_m + c.vbol_m + c.vmat_m + c.vform_m)/1e3), '.', ',') ELSE 'R$ 0' END, ' - ESTADO: ', CASE WHEN (c.vcant_e + c.vbol_e + c.vmat_e + c.vform_e) >= 1e6 THEN REPLACE(FORMAT('R$ %.2f milhões', (c.vcant_e + c.vbol_e + c.vmat_e + c.vform_e)/1e6), '.', ',') WHEN (c.vcant_e + c.vbol_e + c.vmat_e + c.vform_e) >= 1e3 THEN REPLACE(FORMAT('R$ %.2f mil', (c.vcant_e + c.vbol_e + c.vmat_e + c.vform_e)/1e3), '.', ',') ELSE 'R$ 0' END) AS cnca_total_investido,
  
  CONCAT(
    REPLACE(FORMAT("%'d", p.est_m), ',', '.'),
    ' (', REPLACE(FORMAT('%.2f', p.est_m * 100.0 / NULLIF(p.mat_m, 0)), '.', ','), '%)',
    ' - ESTADO: ',
    REPLACE(FORMAT("%'d", p.est_e), ',', '.'),
    ' (', REPLACE(FORMAT('%.2f', p.est_e * 100.0 / NULLIF(p.mat_e, 0)), '.', ','), '%)'
  ) AS pdm_estudantes,
  CONCAT(CASE WHEN p.val_m >= 1e9 THEN REPLACE(FORMAT('R$ %.2f bilhões', p.val_m/1e9), '.', ',') WHEN p.val_m >= 1e6 THEN REPLACE(FORMAT('R$ %.2f milhões', p.val_m/1e6), '.', ',') ELSE REPLACE(FORMAT('R$ %.2f', CAST(p.val_m AS FLOAT64)), '.', ',') END, ' - ESTADO: ', CASE WHEN p.val_e >= 1e9 THEN REPLACE(FORMAT('R$ %.2f bilhões', p.val_e/1e9), '.', ',') ELSE REPLACE(FORMAT('R$ %.2f milhões', p.val_e/1e6), '.', ',') END) AS pdm_valor,
  pdm.pdm_referencia,
  pdm.pdm_abrangencia,
  

  
  CONCAT(pac.ob_m, ' - ESTADO: ', pac.ob_e) AS pacto_obras,
  CONCAT(CASE WHEN pac.vp_m >= 1e9 THEN REPLACE(FORMAT('R$ %.2f bilhões', pac.vp_m/1e9), '.', ',') WHEN pac.vp_m >= 1e6 THEN REPLACE(FORMAT('R$ %.2f milhões', pac.vp_m/1e6), '.', ',') WHEN pac.vp_m >= 1e3 THEN REPLACE(FORMAT('R$ %.2f mil', pac.vp_m/1e3), '.', ',') ELSE 'R$ 0' END, ' - ESTADO: ', CASE WHEN pac.vp_e >= 1e9 THEN REPLACE(FORMAT('R$ %.2f bilhões', pac.vp_e/1e9), '.', ',') ELSE REPLACE(FORMAT('R$ %.2f milhões', pac.vp_e/1e6), '.', ',') END) AS pacto_previsto,
  CONCAT(CASE WHEN pac.vr_m >= 1e9 THEN REPLACE(FORMAT('R$ %.2f bilhões', pac.vr_m/1e9), '.', ',') WHEN pac.vr_m >= 1e6 THEN REPLACE(FORMAT('R$ %.2f milhões', pac.vr_m/1e6), '.', ',')  WHEN pac.vr_m >= 1e3 THEN REPLACE(FORMAT('R$ %.2f mil', pac.vr_m/1e3), '.', ',') ELSE 'R$ 0' END, ' - ESTADO: ', CASE WHEN pac.vr_e >= 1e9 THEN REPLACE(FORMAT('R$ %.2f bilhões', pac.vr_e/1e9), '.', ',') ELSE REPLACE(FORMAT('R$ %.2f milhões', pac.vr_e/1e6), '.', ',') END) AS pacto_repassado,
  
  CONCAT(sel.cr_m, ' - ESTADO: ', sel.cr_e) AS sel_creches,
  CONCAT(CASE WHEN sel.vcr_m >= 1e9 THEN REPLACE(FORMAT('R$ %.2f bilhões', sel.vcr_m/1e9), '.', ',') WHEN sel.vcr_m >= 1e6 THEN REPLACE(FORMAT('R$ %.2f milhões', sel.vcr_m/1e6), '.', ',') WHEN sel.vcr_m >= 1e3 THEN REPLACE(FORMAT('R$ %.2f mil', sel.vcr_m/1e3), '.', ',') ELSE 'R$ 0' END, ' - ESTADO: ', CASE WHEN sel.vcr_e >= 1e9 THEN REPLACE(FORMAT('R$ %.2f bilhões', sel.vcr_e/1e9), '.', ',') ELSE REPLACE(FORMAT('R$ %.2f milhões', sel.vcr_e/1e6), '.', ',') END) AS sel_creches_val,
  CONCAT(sel.eti_m, ' - ESTADO: ', sel.eti_e) AS sel_eti,
  CONCAT(CASE WHEN sel.veti_m >= 1e9 THEN REPLACE(FORMAT('R$ %.2f bilhões', sel.veti_m/1e9), '.', ',') WHEN sel.veti_m >= 1e6 THEN REPLACE(FORMAT('R$ %.2f milhões', sel.veti_m/1e6), '.', ',') WHEN sel.veti_m >= 1e3 THEN REPLACE(FORMAT('R$ %.2f mil', sel.veti_m/1e3), '.', ',') ELSE 'R$ 0' END, ' - ESTADO: ', CASE WHEN sel.veti_e >= 1e9 THEN REPLACE(FORMAT('R$ %.2f bilhões', sel.veti_e/1e9), '.', ',') ELSE REPLACE(FORMAT('R$ %.2f milhões', sel.veti_e/1e6), '.', ',') END) AS sel_eti_val,
  CONCAT(sel.on_m, ' - ESTADO: ', sel.on_e) AS sel_onibus,
  CONCAT(CASE WHEN sel.von_m >= 1e9 THEN REPLACE(FORMAT('R$ %.2f bilhões', sel.von_m/1e9), '.', ',') WHEN sel.von_m >= 1e6 THEN REPLACE(FORMAT('R$ %.2f milhões', sel.von_m/1e6), '.', ',')  WHEN sel.von_m >= 1e3 THEN REPLACE(FORMAT('R$ %.2f mil', sel.von_m/1e3), '.', ',') ELSE 'R$ 0' END, ' - ESTADO: ', CASE WHEN sel.von_e >= 1e9 THEN REPLACE(FORMAT('R$ %.2f bilhões', sel.von_e/1e9), '.', ',') ELSE REPLACE(FORMAT('R$ %.2f milhões', sel.von_e/1e6), '.', ',') END) AS sel_onibus_val,
  
  CONCAT(CASE WHEN se.cons_m >= 1e9 THEN REPLACE(FORMAT('R$ %.2f bilhões', se.cons_m/1e9), '.', ',') WHEN se.cons_m >= 1e6 THEN REPLACE(FORMAT('R$ %.2f milhões', se.cons_m/1e6), '.', ',') ELSE 'R$ 0' END, ' - ESTADO: ', CASE WHEN se.cons_e >= 1e9 THEN REPLACE(FORMAT('R$ %.2f bilhões', se.cons_e/1e9), '.', ',') ELSE REPLACE(FORMAT('R$ %.2f milhões', se.cons_e/1e6), '.', ',') END) AS sesu_consolidacao,
  CONCAT(CASE WHEN se.exp_m >= 1e9 THEN REPLACE(FORMAT('R$ %.2f bilhões', se.exp_m/1e9), '.', ',') WHEN se.exp_m >= 1e6 THEN REPLACE(FORMAT('R$ %.2f milhões', se.exp_m/1e6), '.', ',') ELSE 'R$ 0' END, ' - ESTADO: ', CASE WHEN se.exp_e >= 1e9 THEN REPLACE(FORMAT('R$ %.2f bilhões', se.exp_e/1e9), '.', ',') ELSE REPLACE(FORMAT('R$ %.2f milhões', se.exp_e/1e6), '.', ',') END) AS sesu_expansao,
  CONCAT(CASE WHEN (se.cons_m + se.exp_m) >= 1e9 THEN REPLACE(FORMAT('R$ %.2f bilhões', (se.cons_m + se.exp_m)/1e9), '.', ',') WHEN (se.cons_m + se.exp_m) >= 1e6 THEN REPLACE(FORMAT('R$ %.2f milhões', (se.cons_m + se.exp_m)/1e6), '.', ',') ELSE 'R$ 0' END, ' - ESTADO: ', CASE WHEN se.tot_e >= 1e9 THEN REPLACE(FORMAT('R$ %.2f bilhões', se.tot_e/1e9), '.', ',') ELSE REPLACE(FORMAT('R$ %.2f milhões', se.tot_e/1e6), '.', ',') END) AS sesu_total,
  
  CONCAT(CASE WHEN st.cons_m >= 1e9 THEN REPLACE(FORMAT('R$ %.2f bilhões', st.cons_m/1e9), '.', ',') WHEN st.cons_m >= 1e6 THEN REPLACE(FORMAT('R$ %.2f milhões', st.cons_m/1e6), '.', ',') ELSE 'R$ 0' END, ' - ESTADO: ', CASE WHEN st.cons_e >= 1e9 THEN REPLACE(FORMAT('R$ %.2f bilhões', st.cons_e/1e9), '.', ',') ELSE REPLACE(FORMAT('R$ %.2f milhões', st.cons_e/1e6), '.', ',') END) AS setec_consolidacao,
  CONCAT(CASE WHEN st.exp_m >= 1e9 THEN REPLACE(FORMAT('R$ %.2f bilhões', st.exp_m/1e9), '.', ',') WHEN st.exp_m >= 1e6 THEN REPLACE(FORMAT('R$ %.2f milhões', st.exp_m/1e6), '.', ',') ELSE 'R$ 0' END, ' - ESTADO: ', CASE WHEN st.exp_e >= 1e9 THEN REPLACE(FORMAT('R$ %.2f bilhões', st.exp_e/1e9), '.', ',') ELSE REPLACE(FORMAT('R$ %.2f milhões', st.exp_e/1e6), '.', ',') END) AS setec_expansao,
  CONCAT(CASE WHEN (st.cons_m + st.exp_m) >= 1e9 THEN REPLACE(FORMAT('R$ %.2f bilhões', (st.cons_m + st.exp_m)/1e9), '.', ',') WHEN (st.cons_m + st.exp_m) >= 1e6 THEN REPLACE(FORMAT('R$ %.2f milhões', (st.cons_m + st.exp_m)/1e6), '.', ',') ELSE 'R$ 0' END, ' - ESTADO: ', CASE WHEN st.tot_e >= 1e9 THEN REPLACE(FORMAT('R$ %.2f bilhões', st.tot_e/1e9), '.', ',') ELSE REPLACE(FORMAT('R$ %.2f milhões', st.tot_e/1e6), '.', ',') END) AS setec_total,
  
  CONCAT(CASE WHEN hu.val_m >= 1e9 THEN REPLACE(FORMAT('R$ %.2f bilhões', hu.val_m/1e9), '.', ',') WHEN hu.val_m >= 1e6 THEN REPLACE(FORMAT('R$ %.2f milhões', hu.val_m/1e6), '.', ',') ELSE 'R$ 0' END, ' - ESTADO: ', CASE WHEN hu.val_e >= 1e9 THEN REPLACE(FORMAT('R$ %.2f bilhões', hu.val_e/1e9), '.', ',') ELSE REPLACE(FORMAT('R$ %.2f milhões', hu.val_e/1e6), '.', ',') END) AS hu_valor,
  
  CONCAT(CASE WHEN f.v22_m >= 1e6 THEN REPLACE(FORMAT('R$ %.2f milhões', f.v22_m/1e6), '.', ',') ELSE REPLACE(FORMAT('R$ %.2f', CAST(f.v22_m AS FLOAT64)), '.', ',') END, ' - ESTADO: ', REPLACE(FORMAT('R$ %.2f bilhões', f.v22_e/1e9), '.', ',')) AS fundeb_2022,
  CONCAT(CASE WHEN f.v23_m >= 1e6 THEN REPLACE(FORMAT('R$ %.2f milhões', f.v23_m/1e6), '.', ',') ELSE REPLACE(FORMAT('R$ %.2f', CAST(f.v23_m AS FLOAT64)), '.', ',') END, ' - ESTADO: ', REPLACE(FORMAT('R$ %.2f bilhões', f.v23_e/1e9), '.', ',')) AS fundeb_2023,
  CONCAT(CASE WHEN f.v24_m >= 1e6 THEN REPLACE(FORMAT('R$ %.2f milhões', f.v24_m/1e6), '.', ',') ELSE REPLACE(FORMAT('R$ %.2f', CAST(f.v24_m AS FLOAT64)), '.', ',') END, ' - ESTADO: ', REPLACE(FORMAT('R$ %.2f bilhões', f.v24_e/1e9), '.', ',')) AS fundeb_2024,
  CONCAT(CASE WHEN f.v25_m >= 1e6 THEN REPLACE(FORMAT('R$ %.2f milhões', f.v25_m/1e6), '.', ',') ELSE REPLACE(FORMAT('R$ %.2f', CAST(f.v25_m AS FLOAT64)), '.', ',') END, ' - ESTADO: ', REPLACE(FORMAT('R$ %.2f bilhões', f.v25_e/1e9), '.', ',')) AS fundeb_2025,
  CONCAT(CASE WHEN f.v26_m >= 1e6 THEN REPLACE(FORMAT('R$ %.2f milhões', f.v26_m/1e6), '.', ',') ELSE REPLACE(FORMAT('R$ %.2f', CAST(f.v26_m AS FLOAT64)), '.', ',') END, ' - ESTADO: ', REPLACE(FORMAT('R$ %.2f bilhões', f.v26_e/1e9), '.', ',')) AS fundeb_2026,
  CONCAT(CASE WHEN f.vaaf_m >= 1e6 THEN REPLACE(FORMAT('R$ %.2f milhões', f.vaaf_m/1e6), '.', ',') WHEN f.vaaf_m > 0 THEN REPLACE(FORMAT('R$ %.2f mil', f.vaaf_m/1e3), '.', ',') ELSE '0' END, ' - ESTADO: ', CASE WHEN f.vaaf_e >= 1e9 THEN REPLACE(FORMAT('R$ %.2f bilhões', f.vaaf_e/1e9), '.', ',') ELSE REPLACE(FORMAT('R$ %.2f milhões', f.vaaf_e/1e6), '.', ',') END) AS fundeb_VAAF,
  CONCAT(CASE WHEN f.vaat_m >= 1e6 THEN REPLACE(FORMAT('R$ %.2f milhões', f.vaat_m/1e6), '.', ',') WHEN f.vaat_m > 0 THEN REPLACE(FORMAT('R$ %.2f mil', f.vaat_m/1e3), '.', ',') ELSE '0' END, ' - ESTADO: ', CASE WHEN f.vaat_e >= 1e9 THEN REPLACE(FORMAT('R$ %.2f bilhões', f.vaat_e/1e9), '.', ',') ELSE REPLACE(FORMAT('R$ %.2f milhões', f.vaat_e/1e6), '.', ',') END) AS fundeb_VAAT,
  CONCAT(CASE WHEN f.vaar_m >= 1e6 THEN REPLACE(FORMAT('R$ %.2f milhões', f.vaar_m/1e6), '.', ',') WHEN f.vaar_m > 0 THEN REPLACE(FORMAT('R$ %.2f mil', f.vaar_m/1e3), '.', ',') ELSE '0' END, ' - ESTADO: ', CASE WHEN f.vaar_e >= 1e9 THEN REPLACE(FORMAT('R$ %.2f bilhões', f.vaar_e/1e9), '.', ',') ELSE REPLACE(FORMAT('R$ %.2f milhões', f.vaar_e/1e6), '.', ',') END) AS fundeb_VAAR,
  
  CONCAT(REPLACE(FORMAT("%'d", CAST(pn.esc_m AS INT64)), ',', '.'), ' - ESTADO: ', REPLACE(FORMAT("%'d", CAST(pn.esc_e AS INT64)), ',', '.')) AS pnae_escolas,
  pn.valor_ano AS pnae_valor,
  
  CONCAT(REPLACE(FORMAT("%'d", CAST(pt.al_m AS INT64)), ',', '.'), ' - ESTADO: ', REPLACE(FORMAT("%'d", CAST(pt.al_e AS INT64)), ',', '.')) AS pnate_estudantes,
  pt.valor_ano AS pnate_valor,
  
  CONCAT(REPLACE(FORMAT("%'d", CAST(i.mat_m AS INT64)), ',', '.'), ' - ESTADO: ', REPLACE(FORMAT("%'d", CAST(i.mat_e AS INT64)), ',', '.')) AS if_matriculas,
  CONCAT(i.if_m, ' - ESTADO: ', i.if_e) AS if_numero,
  CONCAT(i.campi_m, ' - ESTADO: ', i.campi_e) AS if_campi,
  
  CASE WHEN u.campi_m = 0 THEN CONCAT('0 - ESTADO: ', u.campi_e) ELSE CONCAT(u.campi_m, ' - ESTADO: ', u.campi_e) END AS uf_campi,
  CASE WHEN u.inst_m = 0 THEN CONCAT('0 - ESTADO: ', u.inst_e) ELSE CONCAT(u.inst_m, ' - ESTADO: ', u.inst_e) END AS uf_instituicoes,
  CASE WHEN u.mat_m = 0 THEN CONCAT('0 - ESTADO: ', REPLACE(FORMAT("%'d", CAST(u.mat_e AS INT64)), ',', '.')) ELSE CONCAT(REPLACE(FORMAT("%'d", CAST(u.mat_m AS INT64)), ',', '.'), ' - ESTADO: ', REPLACE(FORMAT("%'d", CAST(u.mat_e AS INT64)), ',', '.')) END AS uf_matriculas,
  
  -- INDICADORES HISTÓRICOS MUNICÍPIO x ESTADO
  ind_eti.eti_serie_historica_alunos,
  ind_dis.distorcao_idade_serie,
  ind_ren.taxa_reprovacao,
  ind_ren.taxa_abandono_evasao,
  ind_ica.ica_alfabetizacao
  
FROM escola_conectada ec
CROSS JOIN eti
CROSS JOIN cnca c
CROSS JOIN pdm p
CROSS JOIN pacto pac
CROSS JOIN selecoes sel
CROSS JOIN sesu se
CROSS JOIN setec st
CROSS JOIN hu
CROSS JOIN fundeb f
CROSS JOIN pnae pn
CROSS JOIN pnate pt
CROSS JOIN inst i
CROSS JOIN uni u
CROSS JOIN ind_eti
CROSS JOIN ind_dis
CROSS JOIN ind_ren
CROSS JOIN pdm_referencia_abrangencia pdm
CROSS JOIN ind_ica
CROSS JOIN mun_ibge;