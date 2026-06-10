-- =====================================================================
-- ATUALIZAÇÃO DO BRIEFING - pedidos do Ministro
-- ---------------------------------------------------------------------
-- (a) Ind. 2  ETI ......... dois blocos por faixa de governo (2019-2022 e 2023-2026)  [FEITO]
--             retrato = ano final de cada faixa (2022 e 2025); 2026 não publicado.
-- (b) Ind. 4  Pé-de-Meia .. + Taxa de Reprovação e Abandono/Evasão, janela 2023->2024  [FEITO]
--             valor em fração na base -> *100 no texto. (2022/2025 não existem aqui.)
-- (f) Ind. 11 PNAE ........ removida abrangência; valor por ano desde 2022          [FEITO]
-- (g) Ind. 12 PNATE ....... removida abrangência; valor por ano desde 2022          [FEITO]
-- (i) Ind. 14 Univ. Fed. .. campi por faixa de governo + visão Novo PAC            [FEITO]
--             NOTA: números saem da base (Total=339). A imagem do briefing (344)
--             foi tratada como FORMATO, não meta. Validar com quem pediu.
--             2016 inteiro -> faixa "2003 a 2016" (base só tem ano, sem mês).
-- (h) Ind. 13 Inst. Fed. .. PENDENTE - não há tabela de campi de IF com ano de
--             criação no schema. Fonte da imagem (1837->2002, Autorizados/A
--             Autorizar, visão Novo PAC) é externa. Descobrir origem do dado.
-- (c)/(d) SESU R$3,99bi e HU "Brasil Todo": conferir rodando a query (verificação).
-- =====================================================================
WITH mapeamento_uf AS (
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
),
escola_conectada_base AS (
  SELECT  
    sigla_uf,  
    COUNTIF(escolas_conectadas_nivel IN ('Escola com velocidade adequada e rede Wi-Fi insuficiente', 'Escola com velocidade e rede Wi-Fi adequados')) AS conectadas_uf,
    COUNT(*) AS total_escolas_uf
  FROM `br-mec-segape.educacao_politica_enec.enec_conectividade`
  GROUP BY 1 
),
escola_conectada AS (
  SELECT 
    sigla_uf,
    CONCAT(
      REPLACE(FORMAT("%'d", conectadas_uf), ',', '.'), ' (', 
      REPLACE(FORMAT("%.1f", ROUND(conectadas_uf / NULLIF(total_escolas_uf, 0) * 100, 1)), '.', ','), '% ) | Brasil: ',
      REPLACE(FORMAT("%'d", CAST(SUM(conectadas_uf) OVER() AS INT64)), ',', '.'), ' (',
      REPLACE(FORMAT("%.1f", ROUND(SUM(conectadas_uf) OVER() / NULLIF(SUM(total_escolas_uf) OVER(), 0) * 100, 1)), '.', ','), '%)'
    ) AS escolas_conectadas_nivel_4_5
  FROM escola_conectada_base
),
base_eti_union AS (
  SELECT uf, peti_07_qtd_matricula_declarada_ciclo AS matriculas, peti_09_valor_pago_ciclo AS valor
  FROM `br-mec-segape.projeto_gaia.gaia_peti`
  WHERE uf != 'BR' AND peti_04_ciclo IN ('2023/2024', '2023', '2024')
  UNION ALL
  SELECT uf, CAST(matriculas_fundeb AS INT64) AS matriculas, CAST(valor_total_fomento AS FLOAT64) AS valor
  FROM `br-mec-segape-sandbox.sandbox_segape_dmape.andre_teste_eti_valores_2025_csv`
  WHERE tipo_registro = 'repasse' AND nivel_territorial IN ('municipio', 'estadual')
),
base_eti_agg AS (
  SELECT uf AS sigla_uf, SUM(matriculas) AS uf_matriculas, SUM(valor) AS uf_valor
  FROM base_eti_union GROUP BY 1
),
escola_eti AS (
  SELECT
    sigla_uf,
    CONCAT(REPLACE(FORMAT("%'d", CAST(uf_matriculas AS INT64)), ',', '.'), ' | Brasil: ', REPLACE(FORMAT("%'d", CAST(SUM(uf_matriculas) OVER() AS INT64)), ',', '.')) AS escola_eti_qtd_matricula,
    CONCAT('R$ ', REPLACE(FORMAT('%.1f', ROUND(uf_valor / 1e6, 1)), '.', ','), ' milhões | Brasil: R$ 7,16 bilhões') AS escola_eti_valor_fomento
  FROM base_eti_agg
),
pdm_base AS (
  SELECT
   m.sigla_uf,
   COUNT(DISTINCT id_pessoa) AS qtd_estudantes,
   COALESCE(SUM(valor_enviado),0) AS valor_investido
  FROM `br-mec-segape.educacao_politica_pdm.incentivo_estudante_historico_completo` iehc
  LEFT JOIN (SELECT DISTINCT id_uf, sigla_uf FROM `br-mec-segape.educacao_dados_mestres.municipio`) m ON iehc.id = m.id_uf
  WHERE ultima_carga is true AND id_tipo_status_parcela IN ('105','115') AND id != '99' AND LENGTH(id) = 2
  GROUP BY 1
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
pdm_matricula_uf AS (
  SELECT
    m.sigla_uf,
    COUNT(DISTINCT mup.id_pessoa) AS qtd_matricula_pdm
  FROM `br-mec-segape.educacao_politica_pdm.matricula_unica_pdm` mup
  JOIN (SELECT DISTINCT id_uf, sigla_uf FROM `br-mec-segape.educacao_dados_mestres.municipio`) m
    ON mup.id_uf = m.id_uf
  GROUP BY 1
),
pdm_matricula_br AS (
  SELECT COUNT(DISTINCT id_pessoa) AS qtd_matricula_pdm_br
  FROM `br-mec-segape.educacao_politica_pdm.matricula_unica_pdm`
),
pdm_brasil AS (
  SELECT
   COUNT(DISTINCT id_pessoa) AS qtd_estudantes_br,
   (SELECT COALESCE(SUM(valor_enviado),0)
    FROM `br-mec-segape.educacao_politica_pdm.incentivo_estudante_historico_completo`
    WHERE ultima_carga is true AND id_tipo_status_parcela IN ('105','115') 
      AND LENGTH(id) = 2 AND id != '99') AS valor_investido_br
  FROM `br-mec-segape.educacao_politica_pdm.incentivo_estudante_historico_completo`
  WHERE ultima_carga is true AND id_tipo_status_parcela IN ('105','115')
),
pdm AS (
  SELECT
   pb.sigla_uf,
   CONCAT(
     REPLACE(FORMAT("%'d", pb.qtd_estudantes), ',', '.'),
     ' (',
     REPLACE(FORMAT('%.2f', pb.qtd_estudantes * 100.0 / NULLIF(pmu.qtd_matricula_pdm, 0)), '.', ','),
     '%) | Brasil: ',
     REPLACE(FORMAT("%'d", br.qtd_estudantes_br), ',', '.'),
     ' (',
     REPLACE(FORMAT('%.2f', br.qtd_estudantes_br * 100.0 / NULLIF(pmb.qtd_matricula_pdm_br, 0)), '.', ','),
     '%)'
   ) AS pdm_estudantes_beneficiados,
   CONCAT(
     CASE WHEN pb.valor_investido >= 1e9 THEN REPLACE(CONCAT('R$ ', FORMAT('%.2f', pb.valor_investido/1e9), ' bilhões'), '.', ',') ELSE REPLACE(CONCAT('R$ ', FORMAT('%.2f', pb.valor_investido/1e6), ' milhões'), '.', ',') END,
     ' | Brasil: R$ ', REPLACE(FORMAT('%.2f', br.valor_investido_br/1e9), '.', ','), ' bilhões'
   ) AS pdm_valor_investido,
     pra.pdm_abrangencia,
     pra.pdm_referencia
  FROM pdm_base pb 
  CROSS JOIN pdm_referencia_abrangencia pra
  CROSS JOIN pdm_brasil br
  LEFT JOIN pdm_matricula_uf pmu USING(sigla_uf)
  CROSS JOIN pdm_matricula_br pmb
),
novopac_pacto_base AS (
   SELECT sigla_uf, COUNT(*) AS obras_total, COALESCE(SUM(valor_previsto),0) AS valor_previsto, COALESCE(SUM(valor_repasse),0) AS valor_repasse
   FROM (SELECT id_obra, MAX(sigla_uf) AS sigla_uf, MAX(valor_previsto) AS valor_previsto, MAX(valor_repasse) AS valor_repasse FROM `br-mec-segape.projeto_painel_ministro.painel_novopac_pacto` WHERE indicador_aprovada = TRUE AND LENGTH(CAST(id AS STRING)) = 2 AND id != '99' GROUP BY id_obra) GROUP BY 1
),
novopac_pacto AS (
   SELECT sigla_uf, 
    CONCAT(obras_total, ' | Brasil: ', SUM(obras_total) OVER()) AS obras_total_aprovadas,
    CONCAT(REPLACE(FORMAT('R$ %.2f milhões', valor_previsto/1e6), '.', ','), ' | Brasil: R$ ', REPLACE(FORMAT('%.2f bilhões', SUM(valor_previsto) OVER()/1e9), '.', ',')) AS obras_valor_previsto,
    CONCAT(REPLACE(FORMAT('R$ %.2f milhões', valor_repasse/1e6), '.', ','), ' | Brasil: R$ ', REPLACE(FORMAT('%.2f bilhões', SUM(valor_repasse) OVER()/1e9), '.', ',')) AS obras_valor_repassado
   FROM novopac_pacto_base
),
base_selecoes_base AS (
  SELECT sigla_uf,
    COALESCE(SUM(CASE WHEN modalidade = 'Creches' THEN 1 ELSE 0 END), 0) AS creches_qtd,
    SUM(CASE WHEN modalidade = 'Creches' THEN valor_repasse ELSE 0 END) AS creches_valor,
    COALESCE(SUM(CASE WHEN modalidade = 'Escolas Tempo Integral' THEN 1 ELSE 0 END), 0) AS eti_qtd,
    SUM(CASE WHEN modalidade = 'Escolas Tempo Integral' THEN valor_repasse ELSE 0 END) AS eti_valor,
    COALESCE(SUM(CASE WHEN modalidade = 'Ônibus' THEN 1 ELSE 0 END), 0) AS onibus_qtd,
    SUM(CASE WHEN modalidade = 'Ônibus' THEN valor_investimento ELSE 0 END) AS onibus_valor
  FROM `br-mec-segape.projeto_painel_ministro.painel_novopac_selecoes_consolidado` -- equivalente ao consolidado
  WHERE modalidade IS NOT NULL AND id = '99'
  AND situacao NOT IN ('Prop. Cancelada', 'Desclassificado/ Perda De Prazo', 'Desclassificado/Perda De Prazo', 'Convenio Anulado', 'Convenio Rescindido','Habilitado') -- habilitado sao onibus do edital 2 que nao foram selecionados 
  GROUP BY 1
)
,
base_selecoes AS (
  SELECT sigla_uf,
    CONCAT(creches_qtd, ' | Brasil: ', SUM(creches_qtd) OVER()) AS novo_pac_creches,
    CONCAT(REPLACE(FORMAT('R$ %.2f milhões', creches_valor/1e6), '.', ','), ' | Brasil: R$ ', REPLACE(FORMAT('%.2f bilhões', SUM(creches_valor) OVER()/1e9), '.', ',')) AS novo_pac_creches_valor_previsto,
    CONCAT(eti_qtd, ' | Brasil: ', SUM(eti_qtd) OVER()) AS novo_pac_eti,
    CONCAT(REPLACE(FORMAT('R$ %.2f milhões', eti_valor/1e6), '.', ','), ' | Brasil: R$ ', REPLACE(FORMAT('%.2f bilhões', SUM(eti_valor) OVER()/1e9), '.', ',')) AS novo_pac_eti_valor_previsto,
    CONCAT(onibus_qtd, ' | Brasil: ', SUM(onibus_qtd) OVER()) AS novo_pac_onibus,
    CONCAT(REPLACE(FORMAT('R$ %.2f milhões', onibus_valor/1e6), '.', ','), ' | Brasil: R$ ', REPLACE(FORMAT('%.2f bilhões', SUM(onibus_valor) OVER()/1e9), '.', ',')) AS novo_pac_onibus_valor_previsto
  FROM base_selecoes_base
),
novopac_sesu_aux AS (
  SELECT sigla_uf, COUNT(DISTINCT instituicao) AS qtd 
  FROM `br-mec-segape.projeto_painel_ministro.painel_novopac_sesu` 
  WHERE categoria = 'Expansão' AND id = '99'
  GROUP BY 1
),
novopac_sesu_expansao_locais AS (
  SELECT sigla_uf, STRING_AGG(DISTINCT municipio_obra, ', ') AS nomes_campi 
  FROM `br-mec-segape.projeto_painel_ministro.painel_novopac_sesu` 
  WHERE categoria = 'Expansão' AND id = '99' AND municipio_obra IS NOT NULL 
  GROUP BY 1
),
base_sesu_agg AS (
  SELECT sigla_uf,
    COALESCE(SUM(CASE WHEN categoria = 'Consolidação' THEN valor_previsto ELSE 0 END), 0) AS val_consolidacao,
    COALESCE(SUM(CASE WHEN categoria = 'Expansão' THEN valor_previsto ELSE 0 END), 0) AS val_expansao,
    COALESCE(SUM(valor_previsto), 0) AS val_total
  FROM `br-mec-segape.projeto_painel_ministro.painel_novopac_sesu`
  WHERE id = '99'
  GROUP BY 1
),
novopac_sesu AS (
  SELECT s.sigla_uf, 
    CONCAT(REPLACE(FORMAT('R$ %.2f milhões', s.val_consolidacao/1e6), '.', ','), ' | Brasil: R$ ', REPLACE(FORMAT('%.2f bilhões', SUM(s.val_consolidacao) OVER()/1e9), '.', ',')) AS novo_pac_superior_consolidacao, 
    CONCAT(
      CASE WHEN nsa.qtd > 0 THEN CONCAT('R$ ', REPLACE(FORMAT('%.2f', s.val_expansao/1e6), '.', ','), ' milhões - ', nsa.qtd, CASE WHEN nsa.qtd = 1 THEN ' Campus (' ELSE ' Campi (' END, IFNULL(nsel.nomes_campi, ''), ')') ELSE CONCAT('R$ ', REPLACE(FORMAT('%.2f', s.val_expansao/1e6), '.', ','), ' milhões') END,
      ' | Brasil: R$ ', REPLACE(FORMAT('%.2f', SUM(s.val_expansao) OVER()/1e6), '.', ','), ' milhões'
    ) AS novo_pac_superior_expansao, 
    CONCAT(REPLACE(FORMAT('R$ %.2f milhões', s.val_total/1e6), '.', ','), ' | Brasil: R$ ', REPLACE(FORMAT('%.2f bilhões', SUM(s.val_total) OVER()/1e9), '.', ',')) AS novo_pac_superior_total_previsto 
  FROM base_sesu_agg s LEFT JOIN novopac_sesu_aux nsa USING(sigla_uf) LEFT JOIN novopac_sesu_expansao_locais nsel USING(sigla_uf)
),
detalhes_sesu_agg AS (
  SELECT sigla_uf, IFNULL(tipologia, 'Outras Estruturas') AS tipologia, COUNT(*) AS qtd, SUM(valor_previsto)/1e6 AS valor_milhoes 
  FROM `br-mec-segape.projeto_painel_ministro.painel_novopac_sesu` WHERE categoria = 'Consolidação' AND id = '99' GROUP BY 1, 2
),
detalhes_sesu AS (
  SELECT sigla_uf, 
    STRING_AGG(
      CONCAT(qtd, ' ', tipologia, ' = R$ ', 
        CASE 
          WHEN valor_milhoes < 1 THEN CONCAT(REPLACE(FORMAT('%.2f', valor_milhoes * 1000), '.', ','), ' mil')
          ELSE CONCAT(REPLACE(FORMAT('%.2f', valor_milhoes), '.', ','), ' milhões')
        END
      ), ' | '
    ) AS lista_obras_sesu_dinamica 
  FROM detalhes_sesu_agg GROUP BY 1
),
base_novopac_ept AS (SELECT sigla_uf, REGEXP_REPLACE(id_governa, r'99$', '') AS id_campus, tipologia, natureza_empreendimento, categoria_resumido, SUM(valor_previsto) AS valor_previsto FROM `br-mec-segape.projeto_painel_ministro.painel_novopac_setec` WHERE id = '99' GROUP BY 1, 2, 3, 4, 5),
base_setec_agg AS (SELECT sigla_uf, SUM(CASE WHEN categoria_resumido = 'Consolidação' THEN valor_previsto ELSE 0 END) AS val_consolidacao, SUM(CASE WHEN categoria_resumido = 'Expansão' THEN valor_previsto ELSE 0 END) AS val_expansao, SUM(valor_previsto) AS val_total FROM `br-mec-segape.projeto_painel_ministro.painel_novopac_setec` WHERE id = '99' GROUP BY 1),
novopac_ept2 AS (SELECT sigla_uf, COUNT(DISTINCT CASE WHEN LOWER(tipologia) = 'expansão' AND natureza_empreendimento = 'Obra' AND valor_previsto IS NOT NULL THEN id_campus END) AS novopac_ept_expansao_qtd FROM base_novopac_ept WHERE sigla_uf != '-' GROUP BY 1),
novopac_setec AS (
  SELECT s.sigla_uf, 
    CONCAT(REPLACE(FORMAT('R$ %.2f milhões', s.val_consolidacao/1e6), '.', ','), ' | Brasil: R$ ', REPLACE(FORMAT('%.2f bilhões', SUM(s.val_consolidacao) OVER()/1e9), '.', ',')) AS novo_pac_ept_consolidacao, 
    CONCAT(REPLACE(FORMAT('R$ %.2f milhões', s.val_total/1e6), '.', ','), ' | Brasil: R$ ', REPLACE(FORMAT('%.2f bilhões', SUM(s.val_total) OVER()/1e9), '.', ',')) AS novo_pac_ept_total_previsto, 
    REPLACE(FORMAT('R$ %.2f milhões', s.val_expansao/1e6), '.', ',') AS val_expansao_uf_str, 
    REPLACE(FORMAT('%.2f bilhões', SUM(s.val_expansao) OVER()/1e9), '.', ',') AS val_expansao_br_str 
  FROM base_setec_agg s
),
detalhes_setec_agg AS (
  SELECT sigla_uf, IFNULL(tipologia, 'Outros Equipamentos') AS tipologia, COUNT(*) AS qtd, SUM(valor_previsto)/1e6 AS valor_milhoes 
  FROM `br-mec-segape.projeto_painel_ministro.painel_novopac_setec` WHERE categoria_resumido = 'Consolidação' AND id = '99' GROUP BY 1, 2
),
detalhes_setec AS (
  SELECT sigla_uf, 
    STRING_AGG(
      CONCAT(qtd, ' ', tipologia, ' - R$ ', 
        CASE 
          WHEN valor_milhoes < 1 THEN CONCAT(REPLACE(FORMAT('%.2f', valor_milhoes * 1000), '.', ','), ' mil')
          ELSE CONCAT(REPLACE(FORMAT('%.2f', valor_milhoes), '.', ','), ' milhões')
        END
      ), ' | '
    ) AS lista_obras_setec_dinamica 
  FROM detalhes_setec_agg GROUP BY 1
),
locais_expansao_setec AS (
select sigla_uf, STRING_AGG( TRIM(
  REGEXP_REPLACE(
    REPLACE(REPLACE(REPLACE(REPLACE(nome_empreendimento, 'Construção do ', ''), 'Reforma e adequação do ',''), 'Aquisição do ', ''),  'Novo ', ''),
    r' - (Bloco|Guarita|Urbanização|Reforma|Ampliação|Construção|Laboratório|Auditório|Ambientes|Prédio|Restaurante|Salas|Estruturas|Estrutura|Parque|Adequação|Aquisição).*$',
    ''
  )
), ' | ') AS lista_expansao_setec_dinamica
FROM `br-mec-segape.projeto_painel_ministro.painel_novopac_setec`
WHERE id = '99' AND tipologia = 'Expansão' AND municipio_obra IS NOT NULL and natureza_empreendimento = 'Obra'
GROUP BY 1
),
base_novopac_hu AS (
  SELECT sigla_uf, SUM(valor_novo_pac) AS valor_previsto 
  FROM `br-mec-segape.projeto_painel_ministro.painel_novopac_ebserh` 
  WHERE id = '99' 
  GROUP BY 1
),
novopac_hu_brasil AS (
  SELECT COALESCE(SUM(valor_novo_pac), 0) AS valor_previsto_br 
  FROM `br-mec-segape.projeto_painel_ministro.painel_novopac_ebserh` 
  WHERE id = '99'
),
detalhes_hu_agg AS (
  SELECT sigla_uf, nome_empreendimento, SUM(valor_novo_pac)/1e6 AS valor_milhoes 
  FROM `br-mec-segape.projeto_painel_ministro.painel_novopac_ebserh` 
  WHERE id = '99' 
  GROUP BY 1, 2
),
detalhes_hu AS (
  SELECT sigla_uf, STRING_AGG(CONCAT(nome_empreendimento, ' - R$ ', REPLACE(FORMAT('%.2f', valor_milhoes), '.', ','), ' milhões'), ' | ') AS lista_obras_hu_dinamica 
  FROM detalhes_hu_agg 
  GROUP BY 1
),
novopac_hu AS (
  SELECT 
    m.sigla_uf, 
    CONCAT(
      CASE 
        WHEN COALESCE(h.valor_previsto, 0) >= 1e9 THEN REPLACE(CONCAT('R$ ', FORMAT('%.2f', h.valor_previsto/1e9), ' bilhões'), '.', ',') 
        WHEN COALESCE(h.valor_previsto, 0) >= 1e6 THEN REPLACE(CONCAT('R$ ', FORMAT('%.2f', h.valor_previsto/1e6), ' milhões'), '.', ',') 
        ELSE CONCAT('R$ ', FORMAT("%'d", CAST(COALESCE(h.valor_previsto, 0) AS INT64))) 
      END,
      ' | Brasil: R$ ', REPLACE(FORMAT('%.2f', br.valor_previsto_br/1e9), '.', ','), ' bilhões'
    ) AS novo_pac_hu_valor_previsto, 
    d.lista_obras_hu_dinamica 
  FROM mapeamento_uf m
  LEFT JOIN base_novopac_hu h ON m.sigla_uf = h.sigla_uf
  LEFT JOIN detalhes_hu d ON m.sigla_uf = d.sigla_uf
  CROSS JOIN novopac_hu_brasil br
),
fundeb_base AS (
  SELECT sigla_uf,
    SUM(CASE WHEN ano = 2022 THEN valor ELSE 0 END) AS v22,  
    SUM(CASE WHEN ano = 2023 THEN valor ELSE 0 END) AS v23, 
    SUM(CASE WHEN ano = 2024 THEN valor ELSE 0 END) AS v24, 
    SUM(CASE WHEN ano = 2025 THEN valor ELSE 0 END) AS v25, 
    -- Correção: Voltando a somar o TOTAL de 2026 (Fundos + Complementações), 
    -- pois a 1ª linha do PDF representa o Total Geral, e não apenas o fundo base.
    SUM(CASE WHEN ano = 2026 THEN valor ELSE 0 END) AS v26, 
    SUM(CASE WHEN tipo_transferencia = 'Complementação VAAF' AND ano = 2026 THEN valor ELSE 0 END) AS vaaf, 
    SUM(CASE WHEN tipo_transferencia = 'Complementação VAAT' AND ano = 2026 THEN valor ELSE 0 END) AS vaat, 
    SUM(CASE WHEN tipo_transferencia = 'Complementação VAAR' AND ano = 2026 THEN valor ELSE 0 END) AS vaar
  FROM `br-mec-segape.indicador_politica_fundeb_base.fundeb_base_repasse_estimativa` 
  WHERE status = 'Realizado' 
  GROUP BY 1
),
fundeb AS (
  SELECT b.sigla_uf,
    CONCAT(REPLACE(FORMAT('R$ %.2f bilhões', b.v22/1e9), '.', ','), ' | Brasil: R$ ', REPLACE(FORMAT('%.2f bilhões', SUM(b.v22) OVER()/1e9), '.', ',')) AS fundeb_2022,
    CONCAT(REPLACE(FORMAT('R$ %.2f bilhões', b.v23/1e9), '.', ','), ' | Brasil: R$ ', REPLACE(FORMAT('%.2f bilhões', SUM(b.v23) OVER()/1e9), '.', ',')) AS fundeb_2023,
    CONCAT(REPLACE(FORMAT('R$ %.2f bilhões', b.v24/1e9), '.', ','), ' | Brasil: R$ ', REPLACE(FORMAT('%.2f bilhões', SUM(b.v24) OVER()/1e9), '.', ',')) AS fundeb_2024,
    CONCAT(REPLACE(FORMAT('R$ %.2f bilhões', b.v25/1e9), '.', ','), ' | Brasil: R$ ', REPLACE(FORMAT('%.2f bilhões', SUM(b.v25) OVER()/1e9), '.', ',')) AS fundeb_2025,
    CONCAT(
      CASE WHEN b.v26 >= 2e9 THEN REPLACE(FORMAT('R$ %.2f bilhões', b.v26/1e9), '.', ',') WHEN b.v26 >= 1e9 THEN REPLACE(FORMAT('R$ %.2f bilhão', b.v26/1e9), '.', ',') ELSE REPLACE(FORMAT('R$ %.2f milhões', b.v26/1e6), '.', ',') END,
      ' | Brasil: R$ ', REPLACE(FORMAT('%.2f bilhões', SUM(b.v26) OVER()/1e9), '.', ',')
    ) AS fundeb_2026,
    CONCAT(CASE WHEN b.vaaf >= 2e9 THEN REPLACE(FORMAT('R$ %.2f bilhões', b.vaaf/1e9), '.', ',') WHEN b.vaaf >= 1e9 THEN REPLACE(FORMAT('R$ %.2f bilhão', b.vaaf/1e9), '.', ',') ELSE REPLACE(FORMAT('R$ %.2f milhões', b.vaaf/1e6), '.', ',') END, ' | Brasil: R$ ', REPLACE(FORMAT('%.2f bilhões', SUM(b.vaaf) OVER()/1e9), '.', ',')) AS fundeb_valor_repassado_VAAF,
    CONCAT(CASE WHEN b.vaat >= 2e9 THEN REPLACE(FORMAT('R$ %.2f bilhões', b.vaat/1e9), '.', ',') WHEN b.vaat >= 1e9 THEN REPLACE(FORMAT('R$ %.2f bilhão', b.vaat/1e9), '.', ',') ELSE REPLACE(FORMAT('R$ %.2f milhões', b.vaat/1e6), '.', ',') END, ' | Brasil: R$ ', REPLACE(FORMAT('%.2f bilhões', SUM(b.vaat) OVER()/1e9), '.', ',')) AS fundeb_valor_repassado_VAAT,
    CONCAT(
      CASE WHEN b.vaar >= 2e9 THEN REPLACE(FORMAT('R$ %.2f bilhões', b.vaar/1e9), '.', ',') WHEN b.vaar >= 1e9 THEN REPLACE(FORMAT('R$ %.2f bilhão', b.vaar/1e9), '.', ',') ELSE REPLACE(FORMAT('R$ %.2f milhões', b.vaar/1e6), '.', ',') END,
      ' | Brasil: R$ ',
      CASE WHEN SUM(b.vaar) OVER() >= 2e9 THEN REPLACE(FORMAT('%.2f bilhões', SUM(b.vaar) OVER()/1e9), '.', ',') WHEN SUM(b.vaar) OVER() >= 1e9 THEN REPLACE(FORMAT('%.2f bilhão', SUM(b.vaar) OVER()/1e9), '.', ',') ELSE REPLACE(FORMAT('%.2f milhões', SUM(b.vaar) OVER()/1e6), '.', ',') END
    ) AS fundeb_valor_repassado_VAAR
  FROM fundeb_base b
),
pnae_escolas_agg AS (
  SELECT m.sigla_uf, SUM(p.qtd_escola) AS total_escolas FROM `br-mec-segape.projeto_painel_ministro.painel_pnae` p JOIN mapeamento_uf m ON UPPER(p.estado) = m.nome WHERE p.municipio = 'Todos' AND p.estado != 'Todos' GROUP BY 1
),
-- (f) PNAE: valor por ano desde 2022 (abrangência removida). Escolas mantidas.
pnae_repasse_ano AS (
  SELECT uf AS sigla_uf, LEFT(dt_ref,4) AS ano, SUM(pnae_03_val_repasse) AS valor
  FROM `br-mec-segape.projeto_gaia.gaia_pnae` GROUP BY 1,2
),
pnae_repasse_br_ano AS (
  SELECT ano, SUM(valor) AS valor_br FROM pnae_repasse_ano GROUP BY 1
),
pnae_valor_ano AS (
  SELECT sigla_uf,
    CONCAT(
      STRING_AGG(CONCAT(ano, ': ',
        CASE WHEN valor >= 1e9 THEN REPLACE(FORMAT('R$ %.2f bilhões', valor/1e9), '.', ',')
             ELSE REPLACE(FORMAT('R$ %.2f milhões', valor/1e6), '.', ',') END
      ), ' | ' ORDER BY ano),
      ' || Brasil: ',
      (SELECT STRING_AGG(CONCAT(ano, ': ',
        CASE WHEN valor_br >= 1e9 THEN REPLACE(FORMAT('R$ %.2f bilhões', valor_br/1e9), '.', ',')
             ELSE REPLACE(FORMAT('R$ %.2f milhões', valor_br/1e6), '.', ',') END
      ), ' | ' ORDER BY ano) FROM pnae_repasse_br_ano)
    ) AS pnae_valor_investido_ano
  FROM pnae_repasse_ano GROUP BY 1
),
pnae AS (
  SELECT e.sigla_uf,
    CONCAT(REPLACE(FORMAT("%'d", CAST(e.total_escolas AS INT64)), ',', '.'), ' | Brasil: ', REPLACE(FORMAT("%'d", SUM(CAST(e.total_escolas AS INT64)) OVER()), ',', '.')) AS pnae_escolas_apoiadas,
    v.pnae_valor_investido_ano AS pnae_valor_investido
  FROM pnae_escolas_agg e LEFT JOIN pnae_valor_ano v USING(sigla_uf)
),
-- (g) PNATE: valor por ano desde 2022 (abrangência removida). Alunos mantidos.
-- Repasse vem de gaia_pnate (município + estado); alunos seguem do painel_pnate.
pnate_alunos_agg AS (
  SELECT m.sigla_uf, SUM(p.qtd_aluno) AS alunos
  FROM `br-mec-segape.projeto_painel_ministro.painel_pnate` p
  JOIN mapeamento_uf m ON UPPER(p.estado) = m.nome
  WHERE SAFE_CAST(p.id AS INT64) < 99 GROUP BY 1
),
pnate_repasse_ano AS (
  SELECT uf AS sigla_uf, LEFT(dt_ref,4) AS ano,
    SUM(COALESCE(pnate_03_val_repasse_municipio,0) + COALESCE(pnate_04_val_repasse_estado,0)) AS valor
  FROM `br-mec-segape.projeto_gaia.gaia_pnate` GROUP BY 1,2
),
pnate_repasse_br_ano AS (
  SELECT ano, SUM(valor) AS valor_br FROM pnate_repasse_ano GROUP BY 1
),
pnate_valor_ano AS (
  SELECT sigla_uf,
    CONCAT(
      STRING_AGG(CONCAT(ano, ': ',
        CASE WHEN valor >= 1e9 THEN REPLACE(FORMAT('R$ %.2f bilhões', valor/1e9), '.', ',')
             ELSE REPLACE(FORMAT('R$ %.2f milhões', valor/1e6), '.', ',') END
      ), ' | ' ORDER BY ano),
      ' || Brasil: ',
      (SELECT STRING_AGG(CONCAT(ano, ': ',
        CASE WHEN valor_br >= 1e9 THEN REPLACE(FORMAT('R$ %.2f bilhões', valor_br/1e9), '.', ',')
             ELSE REPLACE(FORMAT('R$ %.2f milhões', valor_br/1e6), '.', ',') END
      ), ' | ' ORDER BY ano) FROM pnate_repasse_br_ano)
    ) AS pnate_valor_investido_ano
  FROM pnate_repasse_ano GROUP BY 1
),
pnate AS (
  SELECT a.sigla_uf,
    CONCAT(REPLACE(FORMAT("%'d", CAST(a.alunos AS INT64)), ',', '.'), ' | Brasil: ', REPLACE(FORMAT("%'d", SUM(CAST(a.alunos AS INT64)) OVER()), ',', '.')) AS pnate_estudantes_beneficiados,
    v.pnate_valor_investido_ano AS pnate_valor_investido
  FROM pnate_alunos_agg a LEFT JOIN pnate_valor_ano v USING(sigla_uf)
),
institutos_base AS (
  SELECT 
    p.sigla_uf, 
    SUM(pnp.numero_matriculas) AS mat, 
    COUNT(DISTINCT p.id_instituicao) AS n_if, 
    COUNT(DISTINCT pnp.id_unidade) AS n_campi 
  FROM `br-mec-segape.educacao_politica_pnp_painel.pnp_painel_situacao_matricula` pnp 
  JOIN `br-mec-segape.educacao_politica_pnp_painel.pnp_painel_instituicao` p 
    ON p.chave_unidade = pnp.chave_unidade 
  JOIN `br-mec-segape.educacao_politica_pnp_painel.pnp_painel_organizacao_administrativa` e 
    ON e.chave_unidade = pnp.chave_unidade 
  WHERE pnp.ano = 2024 
    AND e.organizacao_administrativa = 'Institutos'
 
  GROUP BY 1
),
institutos AS (
  SELECT sigla_uf, CONCAT(REPLACE(FORMAT("%.1f mil", mat/1000), '.', ','), ' | Brasil: ', REPLACE(FORMAT("%'d", SUM(mat) OVER()), ',', '.')) AS if_matriculas, CONCAT(n_if, ' | Brasil: ', SUM(n_if) OVER()) AS if_numero, CONCAT(n_campi, ' | Brasil: ', SUM(n_campi) OVER()) AS if_campi FROM institutos_base
),
universidades_base AS (
  SELECT 
    sigla_uf, 
    COUNT(DISTINCT CONCAT(sigla_ies, '|', campus)) AS uf_campi 
  FROM `sandbox_segape_dmape.projeto_painel_ministro_painel_universidades_campus`
  WHERE sigla_uf IS NOT NULL 
  GROUP BY 1
),
universidades AS (
  SELECT sigla_uf, CONCAT(uf_campi, ' | Brasil: ', SUM(uf_campi) OVER()) AS uf_campi 
  FROM universidades_base
),
universidade_inst_base AS (
  SELECT 
    sigla_uf, 
    COUNT(DISTINCT sigla_ies) AS uf_instituicoes 
  FROM `sandbox_segape_dmape.projeto_painel_ministro_painel_universidades_campus` 
  WHERE sigla_uf IS NOT NULL 
    -- AND status_funcionamento != 'Em Transformação Para Campus'
  GROUP BY 1
),
universidade_br_base AS (
  SELECT 
    COUNT(DISTINCT sigla_ies) AS instituicoes_br 
  FROM `sandbox_segape_dmape.projeto_painel_ministro_painel_universidades_campus`
  WHERE sigla_uf IS NOT NULL 
    -- AND status_funcionamento != 'Em Transformação Para Campus'
),
universidade_mat_base AS (
  SELECT curso.sigla_uf AS sigla_uf, 
    SUM(curso.quantidade_matriculas) AS uf_matriculas_graduacao 
  FROM `br-mec-segape.educacao_inep_dados_abertos.inep_censo_educacao_superior_curso` curso 
  JOIN `br-mec-segape.educacao_inep_dados_abertos.inep_censo_educacao_superior_ies` ies 
    ON curso.id_ies = ies.id_ies AND ies.ano_censo = 2024 
  WHERE curso.ano_censo = 2024 
    AND curso.id_tipo_nivel_academico = 1 
    AND curso.id_tipo_categoria_administrativa = 1 
    AND curso.id_tipo_organizacao_academica = 1 
    AND curso.id_tipo_modalidade_ensino IN (1, 2) 
    AND curso.sigla_uf IS NOT NULL 
  GROUP BY 1
),
universidade_mat AS (
  SELECT 
    COALESCE(inst.sigla_uf, mat.sigla_uf) AS sigla_uf, 
    CONCAT(inst.uf_instituicoes, ' | Brasil: ', br.instituicoes_br) AS uf_instituicoes, 
    CONCAT(REPLACE(FORMAT("%'d", CAST(mat.uf_matriculas_graduacao AS INT64)), ',', '.'), ' | Brasil: ', REPLACE(FORMAT("%'d", CAST(SUM(mat.uf_matriculas_graduacao) OVER() AS INT64)), ',', '.')) AS uf_matriculas_graduacao 
  FROM universidade_inst_base inst
  FULL OUTER JOIN universidade_mat_base mat USING (sigla_uf)
  CROSS JOIN universidade_br_base br
),
-- (i) Univ. Federais: campi por faixa de governo + visão Novo PAC (nível Brasil)
-- Tabela é ~20x duplicada (6.740 linhas / 339 campi) -> dedup obrigatório por (ies, campus).
-- 'contagem_campus' NÃO é contador (é sigla+nome concatenado); usar COUNT(DISTINCT).
-- 90 campi sem ano_inauguracao = futuros (81 'Previsto - Expansão' + 9 'Em Transformação') -> caem em 2023+.
uni_campus_norm AS (
  SELECT sigla_ies, campus,
    MIN(SAFE_CAST(ano_inauguracao AS INT64)) AS ano_inaug,
    CASE MAX(CASE status_funcionamento
               WHEN 'Em Atividade'                 THEN 5
               WHEN 'Em Atividade - Expansão'      THEN 4
               WHEN 'Em Transformação Para Campus' THEN 3
               WHEN 'Previsto - Expansão'          THEN 2 ELSE 1 END)
      WHEN 5 THEN 'Em Atividade'                WHEN 4 THEN 'Em Atividade - Expansão'
      WHEN 3 THEN 'Em Transformação Para Campus' WHEN 2 THEN 'Previsto - Expansão'
      ELSE 'Sem status' END AS status_funcionamento
  FROM `sandbox_segape_dmape.projeto_painel_ministro_painel_universidades_campus`
  WHERE sigla_uf IS NOT NULL
  GROUP BY 1, 2
),
uni_campus_faixa AS (
  SELECT *,
    CASE
      WHEN ano_inaug IS NULL THEN 'A partir de 2023'
      WHEN ano_inaug <= 2002 THEN 'Até 2002'
      WHEN ano_inaug <= 2016 THEN '2003 a 2016'   -- 2016 inteiro aqui (base só tem ano)
      WHEN ano_inaug <= 2018 THEN '2017 a 2018'
      WHEN ano_inaug <= 2022 THEN '2019 a 2022'
      ELSE 'A partir de 2023' END AS faixa_governo,
    CASE WHEN status_funcionamento IN ('Em Atividade','Em Atividade - Expansão')
         THEN 'Funcionando' ELSE 'Não Funcionando' END AS situacao,
    status_funcionamento IN ('Em Atividade - Expansão','Previsto - Expansão','Em Transformação Para Campus') AS is_expansao
  FROM uni_campus_norm
),
universidades_faixa AS (
  SELECT
    CONCAT(
      'Até 2002: ', COUNTIF(faixa_governo='Até 2002'),
      ' | 2003 a 2016: ', COUNTIF(faixa_governo='2003 a 2016'),
      ' | 2017 a 2018: ', COUNTIF(faixa_governo='2017 a 2018'),
      ' | 2019 a 2022: ', COUNTIF(faixa_governo='2019 a 2022'),
      ' | A partir de 2023: ', COUNTIF(faixa_governo='A partir de 2023'),
        ' (Funcionando: ', COUNTIF(faixa_governo='A partir de 2023' AND situacao='Funcionando'),
        ', Não Funcionando: ', COUNTIF(faixa_governo='A partir de 2023' AND situacao='Não Funcionando'), ')',
      ' | Total Geral: ', COUNT(*)
    ) AS uf_campi_visao_geral,
    CONCAT(
      'A partir de 2023: ', COUNTIF(is_expansao),
      ' (Funcionando: ', COUNTIF(is_expansao AND situacao='Funcionando'),
      ', Não Funcionando: ', COUNTIF(is_expansao AND situacao='Não Funcionando'), ')'
    ) AS uf_campi_expansao_novopac
  FROM uni_campus_faixa
),
cnca_art_tot AS (SELECT sigla_uf, SUM(qtd_articuladores_total) AS qtd_art FROM `br-mec-segape.projeto_painel_ministro.painel_cnca` WHERE id != '99' AND (municipio != 'Todos' OR sigla_uf = 'DF') AND ano = 2026 GROUP BY 1),
cnca_art_reg_est AS (SELECT sigla_uf, SUM(qtd_articuladores_renalfa_regional) AS qtd_reg, SUM(qtd_articuladores_renalfa_estadual) AS qtd_est FROM `br-mec-segape.projeto_painel_ministro.painel_cnca` WHERE id != '99' AND ano = 2026 GROUP BY 1),
cnca_emp AS (SELECT sigla_uf, SUM(valor_empenhado_materiais) AS val_mat, SUM(valor_empenhado_formacoes) AS val_form FROM `br-mec-segape.projeto_painel_ministro.painel_cnca` WHERE id != '99' GROUP BY 1),
cnca_inv AS (SELECT sigla_uf, SUM(valor_repasse_bolsistas_total) AS rep_bolsistas, SUM(valor_pago_total) AS val_pago FROM `br-mec-segape.projeto_painel_ministro.painel_cnca` WHERE id != '99' AND municipio = 'Todos' GROUP BY 1),
cnca_base AS (
  SELECT pc.sigla_uf, SUM(qtd_cantinho_leitura_apoiado) AS qtd_cantinho, SUM(qtd_escolas_apoiadas_cantinho_leitura) AS qtd_esc_apoiadas, SUM(valor_pago_escolas_cantinho_leitura) AS val_cantinhos, MAX(CASE WHEN pc.sigla_uf = 'DF' THEN a.qtd_art ELSE a.qtd_art + r.qtd_reg + r.qtd_est END) AS qtd_art_total, MAX(i.rep_bolsistas) AS rep_articuladores, MAX(e.val_mat) AS val_materiais, MAX(e.val_form) AS val_formacao, MAX(i.val_pago) AS total_investido
  FROM `br-mec-segape.projeto_painel_ministro.painel_cnca` pc INNER JOIN cnca_art_tot a USING(sigla_uf) INNER JOIN cnca_emp e USING(sigla_uf) INNER JOIN cnca_art_reg_est r USING(sigla_uf) INNER JOIN cnca_inv i USING(sigla_uf) WHERE id != '99' AND (municipio != 'Todos' OR pc.sigla_uf = 'DF') GROUP BY 1
),
cnca_brasil AS (
  SELECT
    SUM(qtd_cantinho_leitura_apoiado)            AS cantinho_leitura_br,
    SUM(qtd_escolas_apoiadas_cantinho_leitura)   AS escolas_apoiadas_br,
    SUM(valor_pago_escolas_cantinho_leitura)    AS valor_cantinhos_br,
    SUM(valor_repasse_bolsistas_total)           AS repasse_renalfa_br,
    SUM(valor_empenhado_materiais)               AS materiais_br,
    SUM(valor_empenhado_formacoes)               AS formacao_br
  FROM `br-mec-segape.projeto_painel_ministro.painel_cnca`
  WHERE id = '99' AND municipio = 'Todos'
),
cnca AS (
  SELECT 
    cb.sigla_uf,
    CONCAT(
      REPLACE(FORMAT("%'d", CAST(cb.qtd_cantinho AS INT64)), ',', '.'),
      ' | Brasil: ',
      REPLACE(FORMAT("%'d", CAST(br.cantinho_leitura_br AS INT64)), ',', '.')
    ) AS cnca_cantinho_leitura,
    CONCAT(
      REPLACE(FORMAT("%'d", CAST(cb.qtd_esc_apoiadas AS INT64)), ',', '.'),
      ' | Brasil: ',
      REPLACE(FORMAT("%'d", CAST(br.escolas_apoiadas_br AS INT64)), ',', '.')
    ) AS cnca_escolas_apoiadas,
    CONCAT(
      REPLACE(CONCAT('R$ ', FORMAT('%.2f', cb.val_cantinhos/1e6), ' milhões'), '.', ','),
      ' | Brasil: ',
      REPLACE(CONCAT('R$ ', FORMAT('%.2f', br.valor_cantinhos_br/1e6), ' milhões'), '.', ',')
    ) AS cnca_valor_cantinhos,
    CONCAT(
      REPLACE(FORMAT("%'d", cb.qtd_art_total), ',', '.'),
      ' | Brasil: 7.386'
    ) AS cnca_qtd_articuladores_total,
    CONCAT(
      REPLACE(CONCAT('R$ ', FORMAT('%.2f', cb.rep_articuladores/1e6), ' milhões'), '.', ','),
      ' | Brasil: ',
      REPLACE(CONCAT('R$ ', FORMAT('%.2f', br.repasse_renalfa_br/1e6), ' milhões'), '.', ',')
    ) AS cnca_articuladores_renalpha_2026,
    CONCAT(
      REPLACE(CONCAT('R$ ', FORMAT('%.2f', cb.val_materiais/1e6), ' milhões'), '.', ','),
      ' | Brasil: ',
      REPLACE(CONCAT('R$ ', FORMAT('%.2f', br.materiais_br/1e6), ' milhões'), '.', ',')
    ) AS cnca_valor_materiais,
    CONCAT(
      CASE 
        WHEN cb.val_formacao < 1e6 THEN REPLACE(CONCAT('R$ ', FORMAT('%.2f', cb.val_formacao/1e3), ' mil'), '.', ',')
        ELSE REPLACE(CONCAT('R$ ', FORMAT('%.2f', cb.val_formacao/1e6), ' milhões'), '.', ',')
      END,
      ' | Brasil: ',
      CASE 
        WHEN br.formacao_br < 1e6 THEN REPLACE(CONCAT('R$ ', FORMAT('%.2f', br.formacao_br/1e3), ' mil'), '.', ',')
        ELSE REPLACE(CONCAT('R$ ', FORMAT('%.2f', br.formacao_br/1e6), ' milhões'), '.', ',')
      END
    ) AS cnca_valor_formacao,
    CONCAT(
      REPLACE(CONCAT('R$ ', FORMAT('%.2f', (cb.val_cantinhos + cb.rep_articuladores + cb.val_materiais + cb.val_formacao)/1e6), ' milhões'), '.', ','),
      ' | Brasil: R$ 1,56 bilhão'
    ) AS cnca_total_investido
  FROM cnca_base cb
  CROSS JOIN cnca_brasil br
),
-- (a) ETI: série anual 2019-2025 (2026 ainda não publicado na base)
-- (a) ETI: dois blocos por faixa de governo. Retrato = ano final de cada faixa
-- (2022 p/ 2019-2022; 2025 p/ 2023-2026, pois 2026 ainda não foi publicado).
eti_serie_base AS (
  SELECT 
    CASE WHEN id = '99' THEN 'BR' ELSE id END AS id_norm,
    ano,
    quantidade_matricula_integral AS qtd_integral,
    quantidade_matricula_integral * 100.0 / NULLIF(quantidade_matricula, 0) AS pct
  FROM `br-mec-segape.projeto_painel_ministro.painel_matricula_integral_percentual`
  WHERE ano IN (2019,2022, 2023, 2025) AND etapa = 'Todas as etapas'
),
eti_serie_uf AS (
  SELECT m.sigla_uf,
    
    MAX(CASE WHEN b.ano = 2019 THEN b.pct END) AS pct_2019,
    MAX(CASE WHEN b.ano = 2019 THEN b.qtd_integral END) AS qtd_2019,

    MAX(CASE WHEN b.ano = 2022 THEN b.pct END) AS pct_2022,
    MAX(CASE WHEN b.ano = 2022 THEN b.qtd_integral END) AS qtd_2022,

    MAX(CASE WHEN b.ano = 2023 THEN b.pct END) AS pct_2023,
    MAX(CASE WHEN b.ano = 2023 THEN b.qtd_integral END) AS qtd_2023,

    MAX(CASE WHEN b.ano = 2025 THEN b.pct END) AS pct_2026,
    MAX(CASE WHEN b.ano = 2025 THEN b.qtd_integral END) AS qtd_2026
  FROM eti_serie_base b
  JOIN (SELECT DISTINCT id_uf, sigla_uf FROM `br-mec-segape.educacao_dados_mestres.municipio`) m
    ON b.id_norm = m.id_uf
  GROUP BY 1
),
eti_serie_br AS (
  SELECT
    MAX(CASE WHEN ano = 2019 THEN pct END) AS pct_2019_br,
    MAX(CASE WHEN ano = 2019 THEN qtd_integral END) AS qtd_2019_br,

    MAX(CASE WHEN ano = 2022 THEN pct END) AS pct_2022_br,
    MAX(CASE WHEN ano = 2022 THEN qtd_integral END) AS qtd_2022_br,

    MAX(CASE WHEN ano = 2023 THEN pct END) AS pct_2023_br,
    MAX(CASE WHEN ano = 2023 THEN qtd_integral END) AS qtd_2023_br,

    MAX(CASE WHEN ano = 2025 THEN pct END) AS pct_2026_br,
    MAX(CASE WHEN ano = 2025 THEN qtd_integral END) AS qtd_2026_br
  FROM eti_serie_base WHERE id_norm = 'BR'
),
eti_serie AS (
  SELECT u.sigla_uf,
    CONCAT(
      '2019: ', 
        IFNULL(REPLACE(FORMAT('%.2f', u.pct_2019), '.', ','), '-'), '% (',
        IFNULL(REPLACE(FORMAT("%'d", CAST(u.qtd_2019 AS INT64)), ',', '.'), '-'), ' matrículas)',

      ' | 2022: ', 
        IFNULL(REPLACE(FORMAT('%.2f', u.pct_2022), '.', ','), '-'), '% (',
        IFNULL(REPLACE(FORMAT("%'d", CAST(u.qtd_2022 AS INT64)), ',', '.'), '-'), ' matrículas)',

      ' | 2023: ', 
        IFNULL(REPLACE(FORMAT('%.2f', u.pct_2023), '.', ','), '-'), '% (',
        IFNULL(REPLACE(FORMAT("%'d", CAST(u.qtd_2023 AS INT64)), ',', '.'), '-'), ' matrículas)',

      ' | 2026: ', 
        IFNULL(REPLACE(FORMAT('%.2f', u.pct_2026), '.', ','), '-'), '% (',
        IFNULL(REPLACE(FORMAT("%'d", CAST(u.qtd_2026 AS INT64)), ',', '.'), '-'), ' matrículas)(*)',

      ' || Brasil: 2019: ', 
        IFNULL(REPLACE(FORMAT('%.2f', br.pct_2019_br), '.', ','), '-'), '% (',
        IFNULL(REPLACE(FORMAT("%'d", CAST(br.qtd_2019_br AS INT64)), ',', '.'), '-'), ' matrículas)',

      ' | 2022: ', 
        IFNULL(REPLACE(FORMAT('%.2f', br.pct_2022_br), '.', ','), '-'), '% (',
        IFNULL(REPLACE(FORMAT("%'d", CAST(br.qtd_2022_br AS INT64)), ',', '.'), '-'), ' matrículas)',

      ' | 2023: ', 
        IFNULL(REPLACE(FORMAT('%.2f', br.pct_2023_br), '.', ','), '-'), '% (',
        IFNULL(REPLACE(FORMAT("%'d", CAST(br.qtd_2023_br AS INT64)), ',', '.'), '-'), ' matrículas)',

      ' | 2026: ', 
        IFNULL(REPLACE(FORMAT('%.2f', br.pct_2026_br), '.', ','), '-'), '% (',
        IFNULL(REPLACE(FORMAT("%'d", CAST(br.qtd_2026_br AS INT64)), ',', '.'), '-'), ' matrículas)'
        ,
      '(*) 2026 com dado mais recente de 2025; 2026 ainda não publicado.'
    ) AS eti_serie_historica_alunos
  FROM eti_serie_uf u CROSS JOIN eti_serie_br br
),
distorcao_base AS (
  SELECT 
    CASE WHEN id = '99' THEN 'BR' ELSE id END AS id_norm,
    ano,
    taxa_distorcao
  FROM `br-mec-segape.projeto_painel_ministro.painel_taxa_distorcao`
  WHERE ano IN (2022, 2025) AND etapa = 'Ensino Médio'
),
distorcao_uf AS (
  SELECT 
    m.sigla_uf,
    MAX(CASE WHEN b.ano = 2022 THEN b.taxa_distorcao END) AS taxa_2023,
    MAX(CASE WHEN b.ano = 2025 THEN b.taxa_distorcao END) AS taxa_2025
  FROM distorcao_base b
  JOIN (SELECT DISTINCT id_uf, sigla_uf FROM `br-mec-segape.educacao_dados_mestres.municipio`) m
    ON b.id_norm = m.id_uf
  GROUP BY 1
),
distorcao_br AS (
  SELECT 
    MAX(CASE WHEN ano = 2022 THEN taxa_distorcao END) AS taxa_2023_br,
    MAX(CASE WHEN ano = 2025 THEN taxa_distorcao END) AS taxa_2025_br
  FROM distorcao_base WHERE id_norm = 'BR'
),
distorcao_serie AS (
  SELECT 
    u.sigla_uf,
    CONCAT(
      'Ensino Médio: De ',
      REPLACE(FORMAT('%.1f', u.taxa_2023), '.', ','), '% em 2022 para ',
      REPLACE(FORMAT('%.1f', u.taxa_2025), '.', ','), '% em 2025',
      ' | Brasil: De ',
      REPLACE(FORMAT('%.1f', br.taxa_2023_br), '.', ','), '% em 2022 para ',
      REPLACE(FORMAT('%.1f', br.taxa_2025_br), '.', ','), '% em 2025'
    ) AS distorcao_idade_serie
  FROM distorcao_uf u CROSS JOIN distorcao_br br
),
-- (b) Pé-de-Meia: Taxa de Reprovação e Abandono/Evasão (espelha a distorção)
-- TODO: ajustar os 2 anos conforme disponibilidade real em painel_rendimento
--       (a query de 2025 voltou vazia -> provavelmente último ano < 2025).
-- TODO: se 'valor' vier como fração (0,052) em vez de p.p. (5,2), trocar
--       FORMAT('%.1f', x)  por  FORMAT('%.1f', x*100) nas 4 ocorrências abaixo.
-- (b) Pé-de-Meia: Reprovação e Abandono/Evasão (Ensino Médio).
-- Janela 2023->2024 (única disponível em painel_rendimento; distorção vai 2022-2025).
-- 'valor' vem em fração (0,057), por isso *100 no texto.
rendimento_base AS (
  SELECT CASE WHEN id = '99' THEN 'BR' ELSE id END AS id_norm, ano, tipo_taxa, valor
  FROM `br-mec-segape.projeto_painel_ministro.painel_rendimento`
  WHERE ano IN (2023, 2024)
    AND etapa = 'Ensino Médio'
    AND tipo_taxa IN ('Reprovação', 'Abandono')
),
rendimento_uf AS (
  SELECT m.sigla_uf,
    MAX(CASE WHEN b.ano=2023 AND b.tipo_taxa='Reprovação' THEN b.valor END) AS reprov_ini,
    MAX(CASE WHEN b.ano=2024 AND b.tipo_taxa='Reprovação' THEN b.valor END) AS reprov_fim,
    MAX(CASE WHEN b.ano=2023 AND b.tipo_taxa='Abandono'   THEN b.valor END) AS aband_ini,
    MAX(CASE WHEN b.ano=2024 AND b.tipo_taxa='Abandono'   THEN b.valor END) AS aband_fim
  FROM rendimento_base b
  JOIN (SELECT DISTINCT id_uf, sigla_uf FROM `br-mec-segape.educacao_dados_mestres.municipio`) m
    ON b.id_norm = m.id_uf
  GROUP BY 1
),
rendimento_br AS (
  SELECT
    MAX(CASE WHEN ano=2023 AND tipo_taxa='Reprovação' THEN valor END) AS reprov_ini_br,
    MAX(CASE WHEN ano=2024 AND tipo_taxa='Reprovação' THEN valor END) AS reprov_fim_br,
    MAX(CASE WHEN ano=2023 AND tipo_taxa='Abandono'   THEN valor END) AS aband_ini_br,
    MAX(CASE WHEN ano=2024 AND tipo_taxa='Abandono'   THEN valor END) AS aband_fim_br
  FROM rendimento_base WHERE id_norm = 'BR'
),
rendimento_serie AS (
  SELECT u.sigla_uf,
    CONCAT('Ensino Médio: De ', REPLACE(FORMAT('%.1f', u.reprov_ini*100), '.', ','), '% em 2023 para ',
           REPLACE(FORMAT('%.1f', u.reprov_fim*100), '.', ','), '% em 2024 | Brasil: De ',
           REPLACE(FORMAT('%.1f', br.reprov_ini_br*100), '.', ','), '% em 2023 para ',
           REPLACE(FORMAT('%.1f', br.reprov_fim_br*100), '.', ','), '% em 2024') AS taxa_reprovacao,
    CONCAT('Ensino Médio: De ', REPLACE(FORMAT('%.1f', u.aband_ini*100), '.', ','), '% em 2023 para ',
           REPLACE(FORMAT('%.1f', u.aband_fim*100), '.', ','), '% em 2024 | Brasil: De ',
           REPLACE(FORMAT('%.1f', br.aband_ini_br*100), '.', ','), '% em 2023 para ',
           REPLACE(FORMAT('%.1f', br.aband_fim_br*100), '.', ','), '% em 2024') AS taxa_abandono_evasao
  FROM rendimento_uf u CROSS JOIN rendimento_br br
),
ica_base AS (
  SELECT
    CASE WHEN id = '99' THEN 'BR' ELSE id END AS id_norm,
    ano,
    valor
  FROM `br-mec-segape.projeto_painel_ministro.painel_cnca_meta`
  WHERE ano IN (2023, 2025)
    AND definicao_valor = 'REALIZADO - ICA'
),
ica_uf AS (
  SELECT
    m.sigla_uf,
    MAX(CASE WHEN b.ano = 2023 THEN b.valor END) AS ica_2023,
    MAX(CASE WHEN b.ano = 2025 THEN b.valor END) AS ica_2025
  FROM ica_base b
  JOIN (SELECT DISTINCT id_uf, sigla_uf FROM `br-mec-segape.educacao_dados_mestres.municipio`) m
    ON b.id_norm = m.id_uf
  GROUP BY 1
),
ica_br AS (
  SELECT
    MAX(CASE WHEN ano = 2023 THEN valor END) AS ica_2023_br,
    MAX(CASE WHEN ano = 2025 THEN valor END) AS ica_2025_br
  FROM ica_base WHERE id_norm = 'BR'
),
ica_serie AS (
  SELECT
    u.sigla_uf,
    CONCAT(
      'De ', REPLACE(FORMAT('%.2f', u.ica_2023 * 100), '.', ','), '%* em 2023 para ',
      REPLACE(FORMAT('%g', u.ica_2025 * 100), '.', ','), '% em 2025',
      ' | Brasil: De ', REPLACE(FORMAT('%.2f', br.ica_2023_br * 100), '.', ','), '%* em 2023 para ',
      REPLACE(FORMAT('%g', br.ica_2025_br * 100), '.', ','), '% em 2025'
    ) AS ica_alfabetizacao
  FROM ica_uf u CROSS JOIN ica_br br
)
SELECT 
  ec.sigla_uf AS uf, 
  m.nome AS territorio, 
  CONCAT('BRIEFING – Visita Ministerial - ', m.nome) AS titulo, 
  ec.escolas_conectadas_nivel_4_5, 
  eti.escola_eti_qtd_matricula AS eti_matriculas_fomentadas, 
  eti.escola_eti_valor_fomento AS eti_valor_fomentado, 
  c.cnca_cantinho_leitura, c.cnca_escolas_apoiadas, c.cnca_valor_cantinhos, c.cnca_qtd_articuladores_total, c.cnca_articuladores_renalpha_2026, c.cnca_valor_materiais, c.cnca_valor_formacao, c.cnca_total_investido, 
  p.pdm_estudantes_beneficiados, p.pdm_valor_investido, p.pdm_abrangencia, p.pdm_referencia, 
  pacto.obras_total_aprovadas, pacto.obras_valor_previsto, pacto.obras_valor_repassado, 
  bs.novo_pac_creches, bs.novo_pac_creches_valor_previsto, bs.novo_pac_eti, bs.novo_pac_eti_valor_previsto, bs.novo_pac_onibus, bs.novo_pac_onibus_valor_previsto, 
  sesu.novo_pac_superior_consolidacao, sesu.novo_pac_superior_expansao, sesu.novo_pac_superior_total_previsto, dsesu.lista_obras_sesu_dinamica, 
  setec.novo_pac_ept_consolidacao, 
  CASE WHEN ept2.novopac_ept_expansao_qtd > 1 THEN CONCAT(setec.val_expansao_uf_str, ' - ', ept2.novopac_ept_expansao_qtd, ' campi | Brasil: R$ ', setec.val_expansao_br_str) ELSE CONCAT(setec.val_expansao_uf_str, ' - ', IFNULL(ept2.novopac_ept_expansao_qtd,0), ' campus | Brasil: R$ ', setec.val_expansao_br_str) END AS novo_pac_ept_expansao, 
  setec.novo_pac_ept_total_previsto, dsetec.lista_obras_setec_dinamica, les.lista_expansao_setec_dinamica, 
  hu.novo_pac_hu_valor_previsto, hu.lista_obras_hu_dinamica, 
  f.fundeb_2022,f.fundeb_2023, f.fundeb_2024, f.fundeb_2025, f.fundeb_2026, f.fundeb_valor_repassado_VAAF, f.fundeb_valor_repassado_VAAT, f.fundeb_valor_repassado_VAAR, 
  pn.pnae_escolas_apoiadas, pn.pnae_valor_investido, pt.pnate_estudantes_beneficiados, pt.pnate_valor_investido,
  inst.if_matriculas, inst.if_numero, inst.if_campi, u.uf_campi, umat.uf_instituicoes, umat.uf_matriculas_graduacao,
  ufx.uf_campi_visao_geral, ufx.uf_campi_expansao_novopac,
  ind_eti.eti_serie_historica_alunos,
  ind_dis.distorcao_idade_serie,
  ind_ren.taxa_reprovacao, ind_ren.taxa_abandono_evasao,
  ind_ica.ica_alfabetizacao
FROM escola_conectada ec
LEFT JOIN escola_eti eti USING (sigla_uf)
LEFT JOIN cnca c USING (sigla_uf)
LEFT JOIN pdm p USING (sigla_uf)
LEFT JOIN novopac_pacto pacto USING (sigla_uf)
LEFT JOIN base_selecoes bs USING (sigla_uf)
LEFT JOIN novopac_sesu sesu USING (sigla_uf)
LEFT JOIN detalhes_sesu dsesu USING (sigla_uf)
LEFT JOIN novopac_setec setec USING (sigla_uf)
LEFT JOIN novopac_ept2 ept2 USING (sigla_uf)
LEFT JOIN detalhes_setec dsetec USING (sigla_uf)
LEFT JOIN locais_expansao_setec les USING (sigla_uf)
LEFT JOIN novopac_hu hu USING (sigla_uf)
LEFT JOIN fundeb f USING (sigla_uf)
LEFT JOIN pnae pn USING (sigla_uf)
LEFT JOIN pnate pt USING (sigla_uf)
LEFT JOIN institutos inst USING (sigla_uf)
LEFT JOIN universidades u USING (sigla_uf)
LEFT JOIN universidade_mat umat USING (sigla_uf)
LEFT JOIN eti_serie ind_eti USING (sigla_uf)
LEFT JOIN distorcao_serie ind_dis USING (sigla_uf)
LEFT JOIN rendimento_serie ind_ren USING (sigla_uf)
LEFT JOIN ica_serie ind_ica USING (sigla_uf)
CROSS JOIN universidades_faixa ufx
LEFT JOIN mapeamento_uf m USING (sigla_uf)
ORDER BY ec.sigla_uf;