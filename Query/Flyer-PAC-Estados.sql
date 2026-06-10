-- =========================LUCIO========================================
-- BRIEFING MINISTERIAL – DADOS  FLYER
--
-- Composto por três partes:
--   1) Resumo Geral / Novo PAC  
--   2) Programas do MEC         
--   3) Tabela de Obras           
-- Retorno dos 27 estados, economiza ajuste manual no pipeline :)
-- =====================================================================


WITH base_selecoes AS (
  SELECT
    sigla_uf,
    edital,
    -- Creches 
    COALESCE(SUM(CASE WHEN modalidade = 'Creches'               THEN 1                ELSE 0 END), 0) AS creches_qtd,
    COALESCE(SUM(CASE WHEN modalidade = 'Creches'               THEN valor_repasse    ELSE 0 END), 0) AS creches_valor,
    -- ETI
    COALESCE(SUM(CASE WHEN modalidade = 'Escolas Tempo Integral' THEN 1               ELSE 0 END), 0) AS eti_qtd,
    COALESCE(SUM(CASE WHEN modalidade = 'Escolas Tempo Integral' THEN valor_repasse   ELSE 0 END), 0) AS eti_valor,
    -- Ônibus
    COALESCE(SUM(CASE WHEN modalidade = 'Ônibus'                THEN 1                ELSE 0 END), 0) AS onibus_qtd,
    COALESCE(SUM(CASE WHEN modalidade = 'Ônibus'                THEN valor_investimento ELSE 0 END), 0) AS onibus_valor
  FROM `br-mec-segape.projeto_painel_ministro.painel_novopac_selecoes_consolidado`
  WHERE modalidade IS NOT NULL
    AND id = '99'
    AND situacao NOT IN (
      'Prop. Cancelada','Desclassificado/ Perda De Prazo',
      'Desclassificado/Perda De Prazo','Convenio Anulado',
      'Convenio Rescindido','Habilitado'
    )
  GROUP BY 1, 2
),

selecoes_agg AS (
  SELECT
    sigla_uf,

    -- Creche Por edital
    COALESCE(SUM(CASE 
      WHEN edital = 'Edital 1' 
      THEN creches_valor 
      ELSE 0 
    END), 0) AS creches_edital_1_valor,

    COALESCE(SUM(CASE 
      WHEN edital = 'Edital 2' 
      THEN creches_valor 
      ELSE 0 
    END), 0) AS creches_edital_2_valor,
    -- Quantidade total de creches
    COALESCE(SUM(creches_qtd), 0) AS creches_qtd,

    -- ETI: só tem Edital 1
    COALESCE(SUM(CASE 
      WHEN edital = 'Edital 1' 
      THEN eti_valor 
      ELSE 0 
    END), 0) AS eti_edital_1_valor,

    COALESCE(SUM(eti_qtd), 0) AS eti_qtd,

    -- Ônibus Por edital
    COALESCE(SUM(CASE 
      WHEN edital = 'Edital 1' 
      THEN onibus_valor 
      ELSE 0 
    END), 0) AS onibus_edital_1_valor,

    COALESCE(SUM(CASE 
      WHEN edital = 'Edital 2' 
      THEN onibus_valor 
      ELSE 0 
    END), 0) AS onibus_edital_2_valor,

    -- Quantidade total de ônibus
    COALESCE(SUM(onibus_qtd), 0) AS onibus_qtd,

    -- Retornando para contemplar a tabela por enquanto
    0 AS indigena_valor,
    0.0 AS indigena_qtd

  FROM base_selecoes
  GROUP BY sigla_uf
),

sesu_agg AS (
  SELECT
    sigla_uf,
    COALESCE(SUM(CASE WHEN categoria = 'Expansão'     THEN valor_previsto ELSE 0 END), 0) AS val_expansao,
    COALESCE(SUM(CASE WHEN categoria = 'Consolidação' THEN valor_previsto ELSE 0 END), 0) AS val_consolidacao,
    COALESCE(SUM(valor_previsto), 0)                                                       AS val_total,
    COALESCE(SUM(CASE WHEN categoria = 'Consolidação' THEN 1 ELSE 0 END), 0)              AS qtd_obras_consolidacao,
    COUNT(DISTINCT CASE WHEN categoria = 'Consolidação' THEN  municipio_obra END) AS qtd_campi_consolidacao
  FROM `br-mec-segape.projeto_painel_ministro.painel_novopac_sesu`
  WHERE id = '99'
  GROUP BY 1
),

sesu_expansao_qtd AS (
  SELECT sigla_uf, COUNT(DISTINCT instituicao) AS qtd_campus_expansao
  FROM `br-mec-segape.projeto_painel_ministro.painel_novopac_sesu`
  WHERE categoria = 'Expansão' AND id = '99'
  GROUP BY 1
),

setec_agg AS (
  SELECT
    sigla_uf,
    COALESCE(SUM(CASE WHEN categoria_resumido = 'Expansão'     THEN valor_previsto ELSE 0 END), 0) AS val_expansao,
    COALESCE(SUM(CASE WHEN categoria_resumido = 'Consolidação' THEN valor_previsto ELSE 0 END), 0) AS val_consolidacao,
    COALESCE(SUM(valor_previsto), 0)                                                                AS val_total,
    -- obras 
    COALESCE(SUM(CASE WHEN categoria_resumido = 'Consolidação'
      AND natureza_empreendimento = 'Obra' THEN 1 ELSE 0 END), 0)                                 AS qtd_obras_consolidacao,
    -- campi = combinação única de instituicao + municipio_obra
    COUNT(DISTINCT CASE WHEN categoria_resumido = 'Consolidação'
      AND natureza_empreendimento = 'Obra'
      THEN CONCAT(instituicao, '|', municipio_obra) END)                                           AS qtd_campi_consolidacao
  FROM `br-mec-segape.projeto_painel_ministro.painel_novopac_setec`
  WHERE id = '99'
  GROUP BY 1
),

setec_expansao_campi AS (
  SELECT
    sigla_uf,
    COUNT(DISTINCT REGEXP_REPLACE(id_governa, r'99$', '')) AS qtd_campi_expansao
  FROM `br-mec-segape.projeto_painel_ministro.painel_novopac_setec`
  WHERE id = '99'
    AND LOWER(tipologia) = 'expansão'
    AND natureza_empreendimento = 'Obra'
    AND valor_previsto IS NOT NULL
    AND sigla_uf != '-'
  GROUP BY 1
),

hu_agg AS (
  SELECT sigla_uf, COALESCE(SUM(valor_novo_pac), 0) AS val_hu
  FROM `br-mec-segape.projeto_painel_ministro.painel_novopac_ebserh`
  WHERE id = '99'
  GROUP BY 1
),

-- deixei aqui, mas não parece fazer parte do Flyer
brasil_selecoes AS (
  SELECT
    COALESCE(SUM(CASE WHEN modalidade = 'Creches'               THEN 1               ELSE 0 END), 0) AS creches_qtd_br,
    COALESCE(SUM(CASE WHEN modalidade = 'Creches'               THEN valor_repasse   ELSE 0 END), 0) AS creches_valor_br,
    COALESCE(SUM(CASE WHEN modalidade = 'Escolas Tempo Integral' THEN 1              ELSE 0 END), 0) AS eti_qtd_br,
    COALESCE(SUM(CASE WHEN modalidade = 'Escolas Tempo Integral' THEN valor_repasse  ELSE 0 END), 0) AS eti_valor_br,
    COALESCE(SUM(CASE WHEN modalidade = 'Ônibus'                THEN 1               ELSE 0 END), 0) AS onibus_qtd_br,
    COALESCE(SUM(CASE WHEN modalidade = 'Ônibus'                THEN valor_investimento ELSE 0 END), 0) AS onibus_valor_br
  FROM `br-mec-segape.projeto_painel_ministro.painel_novopac_selecoes_consolidado`
  WHERE modalidade IS NOT NULL
    AND id = '99'
    AND situacao NOT IN (
      'Prop. Cancelada','Desclassificado/ Perda De Prazo',
      'Desclassificado/Perda De Prazo','Convenio Anulado',
      'Convenio Rescindido','Habilitado'
    )
),

brasil_sesu AS (
  SELECT
    SUM(CASE WHEN categoria = 'Expansão'     THEN valor_previsto ELSE 0 END) AS val_expansao_br,
    SUM(CASE WHEN categoria = 'Consolidação' THEN valor_previsto ELSE 0 END) AS val_consolidacao_br,
    SUM(valor_previsto)                                                        AS val_total_br
  FROM `br-mec-segape.projeto_painel_ministro.painel_novopac_sesu`
  WHERE id = '99'
),

brasil_sesu_exp_qtd AS (
  SELECT COUNT(DISTINCT instituicao) AS qtd_campus_expansao_br
  FROM `br-mec-segape.projeto_painel_ministro.painel_novopac_sesu`
  WHERE categoria = 'Expansão' AND id = '99'
),

brasil_setec AS (
  SELECT
    SUM(CASE WHEN categoria_resumido = 'Expansão'     THEN valor_previsto ELSE 0 END) AS val_expansao_br,
    SUM(CASE WHEN categoria_resumido = 'Consolidação' THEN valor_previsto ELSE 0 END) AS val_consolidacao_br,
    SUM(valor_previsto)                                                                 AS val_total_br
  FROM `br-mec-segape.projeto_painel_ministro.painel_novopac_setec`
  WHERE id = '99'
),

brasil_setec_campi AS (
  SELECT COUNT(DISTINCT REGEXP_REPLACE(id_governa, r'99$', '')) AS qtd_campi_expansao_br
  FROM `br-mec-segape.projeto_painel_ministro.painel_novopac_setec`
  WHERE id = '99'
    AND LOWER(tipologia) = 'expansão'
    AND natureza_empreendimento = 'Obra'
    AND valor_previsto IS NOT NULL
    AND sigla_uf != '-'
),

brasil_hu AS (
  SELECT 
  sigla_uf,
  COALESCE(SUM(valor_novo_pac), 0) AS val_hu,
  COUNT(DISTINCT instituicao) AS qtd_hu
  FROM `br-mec-segape.projeto_painel_ministro.painel_novopac_ebserh`
  WHERE id = '99'
  GROUP BY 1
),

novopac_ind AS (
  SELECT sigla_uf, COUNT(DISTINCT proposta) AS qtd_emp, SUM(valor_repasse) AS valor_repasse 
FROM `br-mec-segape.gold_novopac.gold_novopac_indigena` 
GROUP BY 1
),


NovoPacEstado As (
SELECT
  s.sigla_uf                                  AS uf,

  -- ── SELEÇÕES ──────────────────────────────────────────────────────
  s.creches_edital_1_valor                    AS creches_valor_uf_ed_1,
  s.creches_edital_2_valor                    AS creches_valor_uf_ed_2,
  s.creches_qtd                               AS creches_qtd_uf,
  
  s.eti_edital_1_valor                        AS eti_valor_uf_ed_1,
  s.eti_qtd                                   AS eti_qtd_uf,
  
  s.onibus_edital_1_valor                     AS onibus_valor_uf_ed_1,
  s.onibus_edital_2_valor                     AS onibus_valor_uf_ed_2,
  s.onibus_qtd                                AS onibus_qtd_uf,
 
  COALESCE(ind.qtd_emp , 0)                   AS indigena_qtd_uf,  
  COALESCE(ind.valor_repasse , 0)             AS indigena_valor_uf,

  -- Subtotal Educação Básica
  (s.creches_edital_1_valor + s.creches_edital_2_valor) + s.eti_edital_1_valor + (s.onibus_edital_1_valor+s.onibus_edital_2_valor)  AS subtotal_ed_basica_valor_uf,
  

  -- ── EDUCAÇÃO SUPERIOR ─────────────────────────────────────────────
  COALESCE(su.val_expansao, 0)                AS sesu_expansao_valor_uf,
  COALESCE(seq.qtd_campus_expansao, 0)        AS sesu_expansao_qtd_campus_uf,


  COALESCE(su.val_consolidacao, 0)            AS sesu_consolidacao_valor_uf,
  COALESCE(su.qtd_obras_consolidacao, 0)      AS sesu_consolidacao_qtd_obras_uf,
  COALESCE(su.qtd_campi_consolidacao, 0)      AS sesu_consolidacao_qtd_campi_uf,


  COALESCE(hu.val_hu, 0)                      AS hu_brasil_valor_uf,
  COALESCE(hu.qtd_hu, 0)                      AS hu_qtd_uf,  


  -- Subtotal Educação Superior
  COALESCE(su.val_total, 0) + COALESCE(hu.val_hu, 0)          AS subtotal_ed_superior_valor_uf,


  -- ── EPT ───────────────────────────────────────────────────────────
  COALESCE(st.val_expansao, 0)                AS ept_expansao_valor_uf,
  COALESCE(stc.qtd_campi_expansao, 0)         AS ept_expansao_qtd_campi_uf,


  COALESCE(st.val_consolidacao, 0)            AS ept_consolidacao_valor_uf,
  COALESCE(st.qtd_obras_consolidacao, 0)      AS ept_consolidacao_qtd_obras_uf,
  COALESCE(st.qtd_campi_consolidacao, 0)      AS ept_consolidacao_qtd_campi_uf,


  -- Subtotal EPT
  COALESCE(st.val_total, 0)                   AS subtotal_ept_valor_uf,


  -- ── TOTAL NOVO PAC NO ESTADO ──────────────────────────────────────
  (s.creches_edital_1_valor + s.creches_edital_2_valor) + s.eti_edital_1_valor + (s.onibus_edital_1_valor+s.onibus_edital_2_valor)
    + COALESCE(su.val_total, 0)
    + COALESCE(hu.val_hu, 0)
    + COALESCE(st.val_total, 0)   
    + COALESCE(ind.valor_repasse,0)            AS total_novopac_estado_valor

FROM selecoes_agg s
LEFT JOIN sesu_agg su              ON s.sigla_uf = su.sigla_uf
LEFT JOIN sesu_expansao_qtd seq    ON s.sigla_uf = seq.sigla_uf
LEFT JOIN setec_agg st             ON s.sigla_uf = st.sigla_uf
LEFT JOIN setec_expansao_campi stc ON s.sigla_uf = stc.sigla_uf
LEFT JOIN brasil_hu hu                ON s.sigla_uf = hu.sigla_uf
LEFT JOIN novopac_ind ind             on s.sigla_uf = ind.sigla_uf
),

-- ═════════════════════════════════════════════════════════════════════
-- Parte 2 – Programas do MEC
-- ═════════════════════════════════════════════════════════════════════
pdm_uf AS (
  SELECT
    m.sigla_uf,
    COUNT(DISTINCT iehc.id_pessoa)      AS qtd_estudantes,
    COALESCE(SUM(iehc.valor_enviado), 0) AS valor_investido
  FROM `br-mec-segape.educacao_politica_pdm.incentivo_estudante_historico_completo` iehc
  LEFT JOIN (SELECT DISTINCT id_uf, sigla_uf FROM `br-mec-segape.educacao_dados_mestres.municipio`) m
    ON iehc.id = m.id_uf
  WHERE iehc.ultima_carga IS TRUE
    AND iehc.id_tipo_status_parcela IN ('105','115')
    AND iehc.id != '99'
    AND LENGTH(iehc.id) = 2
  GROUP BY 1
),

pdm_br AS (
  SELECT COUNT(DISTINCT id_pessoa) AS qtd_estudantes_br
  FROM `br-mec-segape.educacao_politica_pdm.incentivo_estudante_historico_completo`
  WHERE ultima_carga IS TRUE
    AND id_tipo_status_parcela IN ('105','115')
),

ec_uf AS (
  SELECT
    sigla_uf,
    COUNTIF(escolas_conectadas_nivel IN (
      'Escola com velocidade adequada e rede Wi-Fi insuficiente',
      'Escola com velocidade e rede Wi-Fi adequados'
    )) AS conectadas_nivel45
  FROM `br-mec-segape.educacao_politica_enec.enec_conectividade`
  GROUP BY 1
),

ec_br AS (
  SELECT COUNTIF(escolas_conectadas_nivel IN (
    'Escola com velocidade adequada e rede Wi-Fi insuficiente',
    'Escola com velocidade e rede Wi-Fi adequados'
  )) AS conectadas_nivel45_br
  FROM `br-mec-segape.educacao_politica_enec.enec_conectividade`
),

eti_union AS (
  -- ciclos PETI (2023 e 2023/2024)
  SELECT uf AS sigla_uf, peti_07_qtd_matricula_declarada_ciclo AS matriculas
  FROM `br-mec-segape.projeto_gaia.gaia_peti`
  WHERE uf != 'BR' AND peti_04_ciclo IN ('2023/2024','2023','2024')
  UNION ALL
  -- repasses ETI 2025: 1 linha por município por mês; matriculas_fundeb só no 1º mês
  SELECT uf AS sigla_uf, CAST(matriculas_fundeb AS INT64) AS matriculas
  FROM `br-mec-segape-sandbox.sandbox_segape_dmape.andre_teste_eti_valores_2025_csv`
  WHERE nivel_territorial = 'municipio'
    AND matriculas_fundeb IS NOT NULL
),

eti_uf AS (
  SELECT sigla_uf, SUM(matriculas) AS matriculas
  FROM eti_union
  GROUP BY 1
),

eti_br AS (
  SELECT SUM(matriculas) AS matriculas_br FROM eti_union
),

pacto_uf AS (
  SELECT sigla_uf, COUNT(*) AS obras_aprovadas
  FROM (
    SELECT id_obra, MAX(sigla_uf) AS sigla_uf
    FROM `br-mec-segape.projeto_painel_ministro.painel_novopac_pacto`
    WHERE indicador_aprovada = TRUE
      AND LENGTH(CAST(id AS STRING)) = 2
      AND id != '99'
    GROUP BY id_obra
  )
  GROUP BY 1
),

pacto_br AS (
  SELECT COUNT(*) AS obras_aprovadas_br
  FROM (
    SELECT id_obra
    FROM `br-mec-segape.projeto_painel_ministro.painel_novopac_pacto`
    WHERE indicador_aprovada = TRUE
      AND LENGTH(CAST(id AS STRING)) = 2
      AND id != '99'
    GROUP BY id_obra
  )
),

cnca_uf AS (
  SELECT
    sigla_uf,
    SUM(qtd_cantinho_leitura_apoiado) AS qtd_cantinho
  FROM `br-mec-segape.projeto_painel_ministro.painel_cnca`
  WHERE id != '99'
    AND (municipio != 'Todos' OR sigla_uf = 'DF')
  GROUP BY 1
),

cnca_br AS (
  SELECT SUM(qtd_cantinho_leitura_apoiado) AS qtd_cantinho_br
  FROM `br-mec-segape.projeto_painel_ministro.painel_cnca`
  WHERE id = '99' AND municipio = 'Todos'
),

cnca_art_tot AS (
  SELECT sigla_uf, SUM(qtd_articuladores_total) AS qtd_art
  FROM `br-mec-segape.projeto_painel_ministro.painel_cnca`
  WHERE id != '99'
    AND (municipio != 'Todos' OR sigla_uf = 'DF')
    AND ano = 2026
  GROUP BY 1
),

cnca_art_reg_est AS (
  SELECT sigla_uf,
    SUM(qtd_articuladores_renalfa_regional)  AS qtd_reg,
    SUM(qtd_articuladores_renalfa_estadual)  AS qtd_est
  FROM `br-mec-segape.projeto_painel_ministro.painel_cnca`
  WHERE id != '99' AND ano = 2026
  GROUP BY 1
),

art_uf AS (
  -- DF: só qtd_art (sem regional/estadual duplicado); demais UFs: soma os três
  SELECT
    a.sigla_uf,
    MAX(CASE WHEN a.sigla_uf = 'DF'
      THEN a.qtd_art
      ELSE a.qtd_art + COALESCE(r.qtd_reg, 0) + COALESCE(r.qtd_est, 0)
    END) AS qtd_articuladores
  FROM cnca_art_tot a
  LEFT JOIN cnca_art_reg_est r USING(sigla_uf)
  GROUP BY 1
),

art_br AS (
  SELECT 7386 AS qtd_articuladores_br  -- valor fixo conforme query original
),

ProgramasEstado AS (
SELECT
  ec.sigla_uf                              AS uf,
  COALESCE(p.qtd_estudantes, 0)            AS pdm_estudantes_uf,
  COALESCE(ec.conectadas_nivel45, 0)       AS escolas_conectadas_nivel45_uf,
  COALESCE(eti.matriculas, 0)              AS eti_matriculas_uf,
  COALESCE(pac.obras_aprovadas, 0)         AS pacto_obras_aprovadas_uf,
  COALESCE(cn.qtd_cantinho, 0)             AS cnca_cantinhos_uf,
  COALESCE(ar.qtd_articuladores, 0)        AS cnca_articuladores_uf


FROM ec_uf ec
LEFT JOIN pdm_uf p     ON ec.sigla_uf = p.sigla_uf
LEFT JOIN eti_uf eti   ON ec.sigla_uf = eti.sigla_uf
LEFT JOIN pacto_uf pac ON ec.sigla_uf = pac.sigla_uf
LEFT JOIN cnca_uf cn   ON ec.sigla_uf = cn.sigla_uf
LEFT JOIN art_uf ar    ON ec.sigla_uf = ar.sigla_uf
),

-- ═════════════════════════════════════════════════════════════════════
-- Parte 3 – Tabela de Obras (1 linha por obra)
-- Colunas: acao_tipo | sigla | municipio | nome_obra
-- ═════════════════════════════════════════════════════════════════════
obras_base  AS (

  -- SETEC – Expansão
  SELECT
    sigla_uf AS uf, 
    'SETEC - Expansão' AS acao_tipo,
    instituicao AS sigla,
    municipio_obra AS municipio,
    TRIM(REPLACE(REPLACE(REPLACE(REPLACE(
      MIN(nome_empreendimento),
      'Construção do ', ''),
      'Reforma e adequação do ', ''),
      'Aquisição do ', ''),
      'Novo ', '')
    ) AS nome_obra
  FROM `br-mec-segape.projeto_painel_ministro.painel_novopac_setec`
  WHERE id = '99'
    AND tipologia = 'Expansão'
    AND natureza_empreendimento = 'Obra'
    AND municipio_obra IS NOT NULL
  GROUP BY 
    sigla_uf,
    instituicao,
    municipio_obra,
    REGEXP_EXTRACT(
      nome_empreendimento, 
      r'^(.*?)(?:\s*-\s*(?:Bloco|Prédio|Guarita|Urbanização|Laboratório|Auditório|Restaurante|Salas|Estruturas|Estrutura|Parque|Adequação|Ambientes).*)?$'
    )

  UNION ALL

  -- SESU – Expansão
  SELECT
    sigla_uf AS uf,
    'SESU - Expansão' AS acao_tipo,
    TRIM(REGEXP_REPLACE(instituicao, r'\s*[-–].*$', '')) AS sigla,
    municipio_obra AS municipio,
    nome_empreendimento AS nome_obra
  FROM `br-mec-segape.projeto_painel_ministro.painel_novopac_sesu`
  WHERE id = '99'
    AND categoria = 'Expansão'
    AND municipio_obra IS NOT NULL

  UNION ALL

  -- HU Brasil
  SELECT
    sigla_uf AS uf,
    'HU Brasil' AS acao_tipo,
    COALESCE(
      REGEXP_EXTRACT(nome_empreendimento, r'\b([A-Z]{2,}-[A-Z]{2,})\b'),
      REGEXP_EXTRACT(nome_empreendimento, r'\b([A-Z]{3,})\b')
    ) AS sigla,
    municipio_obra AS municipio,
    nome_empreendimento AS nome_obra
  FROM `br-mec-segape.projeto_painel_ministro.painel_novopac_ebserh`
  WHERE id = '99'
),

listaObras AS (
  SELECT
    uf,

    COUNT(*) AS qtd_obras_expansao,

    STRING_AGG(
      FORMAT(
        '%s§%s§%s§%s',
        acao_tipo,
        COALESCE(sigla, ''),
        COALESCE(municipio, ''),
        COALESCE(nome_obra, '')
      ),
      '-x-'
      ORDER BY acao_tipo, sigla, municipio, nome_obra
    ) AS obras_expansao_lista

  FROM obras_base
  GROUP BY uf
),
mapeamento_uf AS (
  SELECT 'AC' AS sigla_uf, 'ACRE' AS nome UNION ALL
  SELECT 'AL', 'ALAGOAS' UNION ALL
  SELECT 'AP', 'AMAPÁ' UNION ALL
  SELECT 'AM', 'AMAZONAS' UNION ALL
  SELECT 'BA', 'BAHIA' UNION ALL
  SELECT 'CE', 'CEARÁ' UNION ALL
  SELECT 'DF', 'DISTRITO FEDERAL' UNION ALL
  SELECT 'ES', 'ESPÍRITO SANTO' UNION ALL
  SELECT 'GO', 'GOIÁS' UNION ALL
  SELECT 'MA', 'MARANHÃO' UNION ALL
  SELECT 'MT', 'MATO GROSSO' UNION ALL
  SELECT 'MS', 'MATO GROSSO DO SUL' UNION ALL
  SELECT 'MG', 'MINAS GERAIS' UNION ALL
  SELECT 'PA', 'PARÁ' UNION ALL
  SELECT 'PB', 'PARAÍBA' UNION ALL
  SELECT 'PR', 'PARANÁ' UNION ALL
  SELECT 'PE', 'PERNAMBUCO' UNION ALL
  SELECT 'PI', 'PIAUÍ' UNION ALL
  SELECT 'RJ', 'RIO DE JANEIRO' UNION ALL
  SELECT 'RN', 'RIO GRANDE DO NORTE' UNION ALL
  SELECT 'RS', 'RIO GRANDE DO SUL' UNION ALL
  SELECT 'RO', 'RONDÔNIA' UNION ALL
  SELECT 'RR', 'RORAIMA' UNION ALL
  SELECT 'SC', 'SANTA CATARINA' UNION ALL
  SELECT 'SP', 'SÃO PAULO' UNION ALL
  SELECT 'SE', 'SERGIPE' UNION ALL
  SELECT 'TO', 'TOCANTINS'
)

SELECT 
     np.uf,
     map.nome,
     CONCAT('R$ ',REPLACE(REPLACE(REPLACE(FORMAT("%'.2f", ROUND(np.creches_valor_uf_ed_1, 2)),  ',', '#'),'.', ','),'#', '.')) AS creches_edital_1,
     CONCAT('R$ ',REPLACE(REPLACE(REPLACE(FORMAT("%'.2f", ROUND(np.creches_valor_uf_ed_2, 2)),  ',', '#'),'.', ','),'#', '.')) AS creches_edital_2,
     np.creches_qtd_uf            AS qtd_creches,
     CONCAT('R$ ',REPLACE(REPLACE(REPLACE(FORMAT("%'.2f", ROUND(np.eti_valor_uf_ed_1, 2)),  ',', '#'),'.', ','),'#', '.')) AS eti_edital_1,
     np.eti_qtd_uf                AS qtd_eti,
     CONCAT('R$ ',REPLACE(REPLACE(REPLACE(FORMAT("%'.2f", ROUND(np.onibus_valor_uf_ed_1, 2)),  ',', '#'),'.', ','),'#', '.')) AS onibus_edital_1,
     CONCAT('R$ ',REPLACE(REPLACE(REPLACE(FORMAT("%'.2f", ROUND(np.onibus_valor_uf_ed_2, 2)),  ',', '#'),'.', ','),'#', '.')) AS onibus_edital_2,
     np.onibus_qtd_uf             AS qtd_onibus,
     CONCAT('R$ ',REPLACE(REPLACE(REPLACE(FORMAT("%'.2f", ROUND(np.indigena_valor_uf, 2)),  ',', '#'),'.', ','),'#', '.')) AS  indigena_valor, 
     np.indigena_qtd_uf           AS qtd_indigena,
     CONCAT('R$ ',REPLACE(REPLACE(REPLACE(FORMAT("%'.2f", ROUND(np.subtotal_ed_basica_valor_uf, 2)),  ',', '#'),'.', ','),'#', '.')) AS subtotal_edbasica_valor,
     CONCAT('R$ ',REPLACE(REPLACE(REPLACE(FORMAT("%'.2f", ROUND(np.sesu_expansao_valor_uf, 2)),  ',', '#'),'.', ','),'#', '.')) AS sesu_expansao_valor,
     CONCAT(COALESCE(np.sesu_expansao_qtd_campus_uf,0), ' campus') AS sesu_qtd_campus,
     CONCAT('R$ ',REPLACE(REPLACE(REPLACE(FORMAT("%'.2f", ROUND(np.sesu_consolidacao_valor_uf, 2)),  ',', '#'),'.', ','),'#', '.')) AS sesu_consolidacao_valor,
     CONCAT(COALESCE(np.sesu_consolidacao_qtd_obras_uf,0), ' obras em ', COALESCE(np.sesu_consolidacao_qtd_campi_uf,0), ' campi')    AS sesu_consolidacao_qtd,
     CONCAT('R$ ',REPLACE(REPLACE(REPLACE(FORMAT("%'.2f", ROUND(np.hu_brasil_valor_uf, 2)),  ',', '#'),'.', ','),'#', '.')) AS hu_valor,
     CONCAT(COALESCE(np.hu_qtd_uf,0), ' obra(s)') AS hu_qtd_obras,
     CONCAT('R$ ',REPLACE(REPLACE(REPLACE(FORMAT("%'.2f", ROUND(np.subtotal_ed_superior_valor_uf, 2)),  ',', '#'),'.', ','),'#', '.')) AS subtotal_edsuperior_valor,
     CONCAT('R$ ',REPLACE(REPLACE(REPLACE(FORMAT("%'.2f", ROUND(np.ept_expansao_valor_uf, 2)),  ',', '#'),'.', ','),'#', '.')) AS ept_expansao_valor,
     CONCAT(COALESCE(np.ept_expansao_qtd_campi_uf,0), ' campus') AS ept_qtd_campus,
     CONCAT('R$ ',REPLACE(REPLACE(REPLACE(FORMAT("%'.2f", ROUND(np.ept_consolidacao_valor_uf, 2)),  ',', '#'),'.', ','),'#', '.')) AS ept_consolidacao_valor,
     CONCAT(COALESCE(np.ept_consolidacao_qtd_obras_uf,0), ' obras em ', COALESCE(np.ept_consolidacao_qtd_campi_uf,0), ' campi')    AS sesu_consolidacao_qtd,
     CONCAT('R$ ',REPLACE(REPLACE(REPLACE(FORMAT("%'.2f", ROUND(np.subtotal_ept_valor_uf, 2)),  ',', '#'),'.', ','),'#', '.')) AS subtotal_ept_valor,
     CONCAT('R$ ',REPLACE(REPLACE(REPLACE(FORMAT("%'.2f", ROUND(np.total_novopac_estado_valor, 2)),  ',', '#'),'.', ','),'#', '.')) AS total_novopac_valor,
  
     
      CASE 
        WHEN COALESCE(pe.pdm_estudantes_uf, 0) >= 1e9 THEN REPLACE(CONCAT(FORMAT('%.2f', pe.pdm_estudantes_uf/1e9), ' bilhões'), '.', ',') 
        WHEN COALESCE(pe.pdm_estudantes_uf, 0) >= 1e6 THEN REPLACE(CONCAT(FORMAT('%.2f', pe.pdm_estudantes_uf/1e6), ' milhões'), '.', ',') 
        ELSE CONCAT(FORMAT("%.2f", pe.pdm_estudantes_uf/1e3), ' mil') 
      END AS pdm_estudantes, 
      CASE 
        WHEN COALESCE(pe.escolas_conectadas_nivel45_uf, 0) >= 1e9 THEN REPLACE(CONCAT(FORMAT('%.2f', pe.escolas_conectadas_nivel45_uf/1e9), ' bilhões'), '.', ',') 
        WHEN COALESCE(pe.escolas_conectadas_nivel45_uf, 0) >= 1e6 THEN REPLACE(CONCAT(FORMAT('%.2f', pe.escolas_conectadas_nivel45_uf/1e6), ' milhões'), '.', ',') 
        ELSE CONCAT(FORMAT("%.2f", pe.escolas_conectadas_nivel45_uf/1e3), ' mil') 
      END AS escolas_conectadas_45, 
      CASE 
        WHEN COALESCE(pe.eti_matriculas_uf, 0) >= 1e9 THEN REPLACE(CONCAT(FORMAT('%.2f', pe.eti_matriculas_uf/1e9), ' bilhões'), '.', ',') 
        WHEN COALESCE(pe.eti_matriculas_uf, 0) >= 1e6 THEN REPLACE(CONCAT(FORMAT('%.2f', pe.eti_matriculas_uf/1e6), ' milhões'), '.', ',') 
        ELSE CONCAT(FORMAT("%.2f", pe.eti_matriculas_uf/1e3), ' mil') 
      END AS eti_matriculas,
      COALESCE(pe.pacto_obras_aprovadas_uf,0) AS pacto_obras_qtd,
      CASE 
        WHEN COALESCE(pe.cnca_cantinhos_uf, 0) >= 1e9 THEN REPLACE(CONCAT(FORMAT('%.2f', pe.cnca_cantinhos_uf/1e9), ' bilhões'), '.', ',') 
        WHEN COALESCE(pe.cnca_cantinhos_uf, 0) >= 1e6 THEN REPLACE(CONCAT(FORMAT('%.2f', pe.cnca_cantinhos_uf/1e6), ' milhões'), '.', ',') 
        ELSE CONCAT(FORMAT("%.2f", pe.cnca_cantinhos_uf/1e3), ' mil') 
      END AS cnca_cantinhos,
      COALESCE(pe.cnca_articuladores_uf,0) AS cnca_articuladores,
      lo.obras_expansao_lista

FROM NovoPacEstado np
LEFT JOIN ProgramasEstado pe ON np.uf = pe.uf
LEFT JOIN listaObras lo ON np.uf = lo.uf
LEFt JOIN mapeamento_uf map ON map.sigla_uf = np.uf


    


