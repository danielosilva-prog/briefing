# Mapeamento de Queries do ATM (origem R)

Nota:
- este arquivo e um inventario historico do mapeamento de queries a partir da implementacao em R;
- ele nao deve ser tratado como fonte de verdade do estado atual das queries Python do `ATM-EQ`.

Gerado em: 2026-03-06 08:22:24

Fonte: school-report-r/report/ATM/queries (ignorando atm.sql).

## Criterio de status no R

- Ativa no report.yaml: arquivo listado em sql_files sem comentario.
- Comentada no report.yaml: arquivo presente porem comentado com #- .
- Fora do report.yaml: arquivo existe em queries/ mas nao esta em sql_files.

## Inventario

| Query | Status (R) | Tabelas BigQuery (qtd) | Campos no SELECT final (qtd) |
|---|---|---:|---:|
| acesso_ensino_superior.sql | Ativa no report.yaml | 6 | 0 |
| acesso_ensino_superior_charts.sql | Ativa no report.yaml | 6 | 0 |
| atm_all_municipios.sql | Fora do report.yaml | 1 | 0 |
| caminho_da_escola.sql | Comentada no report.yaml | 1 | 0 |
| cnca.sql | Ativa no report.yaml | 5 | 10 |
| cpop.sql | Ativa no report.yaml | 2 | 7 |
| ei_manutencao.sql | Ativa no report.yaml | 2 | 0 |
| escolas_conectadas.sql | Ativa no report.yaml | 3 | 9 |
| financiamento_educacao_basica.sql | Ativa no report.yaml | 4 | 46 |
| fundeb.sql | Ativa no report.yaml | 6 | 0 |
| indicadores_educacionais.sql | Ativa no report.yaml | 5 | 0 |
| indicadores_gerais.sql | Ativa no report.yaml | 15 | 0 |
| mais_professores.sql | Ativa no report.yaml | 3 | 0 |
| mulheres_mil.sql | Ativa no report.yaml | 3 | 7 |
| grafico_mapa_municipio_info.sql | Ativa no report.yaml | 1 | 3 |
| novo_pac.sql | Ativa no report.yaml | 7 | 59 |
| novo_pac_charts.sql | Ativa no report.yaml | 5 | 0 |
| pacto_eja.sql | Ativa no report.yaml | 4 | 18 |
| panorama_mec_charts.sql | Ativa no report.yaml | 1 | 0 |
| panorama_mec_geral.sql | Ativa no report.yaml | 7 | 74 |
| panorama_mec_municipio.sql | Ativa no report.yaml | 9 | 74 |
| partiu_if.sql | Ativa no report.yaml | 2 | 12 |
| pdde_basico.sql | Comentada no report.yaml | 1 | 13 |
| pdde_equidade.sql | Ativa no report.yaml | 7 | 21 |
| pe_de_meia.sql | Ativa no report.yaml | 6 | 33 |
| peti.sql | Ativa no report.yaml | 3 | 17 |
| pnae.sql | Comentada no report.yaml | 1 | 10 |
| pnate.sql | Comentada no report.yaml | 2 | 12 |
| pneepei.sql | Ativa no report.yaml | 3 | 15 |
| pneerq.sql | Ativa no report.yaml | 5 | 7 |
| pnld.sql | Comentada no report.yaml | 2 | 13 |
| premio_mais_professores.sql | Ativa no report.yaml | 2 | 14 |
| premio_mec.sql | Ativa no report.yaml | 2 | 22 |
| proditec.sql | Ativa no report.yaml | 1 | 7 |
| proec.sql | Ativa no report.yaml | 2 | 6 |
| pronatec.sql | Ativa no report.yaml | 3 | 7 |
| rede_federal.sql | Ativa no report.yaml | 6 | 12 |
| rede_federal_charts.sql | Ativa no report.yaml | 4 | 0 |

## Detalhamento por query

### acesso_ensino_superior.sql

- status_r: Ativa no report.yaml
- tabelas_bq (6):
  - br-mec-segape.educacao_dados_mestres.municipio
  - br-mec-segape.educacao_sisu_dados_abertos.sisu_nota_de_corte
  - br-mec-segape.projeto_painel_ministro.painel_capes
  - br-mec-segape.projeto_painel_ministro.painel_fies_contrato
  - br-mec-segape.projeto_painel_ministro.painel_prouni
  - br-mec-segape.projeto_painel_ministro.painel_sisu
- campos_select_final (0):
  - Nao foi possivel inferir aliases no SELECT final.

### acesso_ensino_superior_charts.sql

- status_r: Ativa no report.yaml
- tabelas_bq (6):
  - br-mec-segape.educacao_dados_mestres.municipio
  - br-mec-segape.educacao_inep_dados_abertos.inep_censo_educacao_superior_curso
  - br-mec-segape.educacao_sisu_dados_abertos.sisu_nota_de_corte
  - br-mec-segape.projeto_painel_ministro.painel_capes
  - br-mec-segape.projeto_painel_ministro.painel_fies_contrato
  - br-mec-segape.projeto_painel_ministro.painel_prouni
- campos_select_final (0):
  - Nao foi possivel inferir aliases no SELECT final.

### atm_all_municipios.sql

- status_r: Fora do report.yaml
- tabelas_bq (1):
  - br-mec-segape-sandbox.projeto_segape_dmape_relat_automatico.atm_all_municipios
- campos_select_final (0):
  - Nao foi possivel inferir aliases no SELECT final.

### caminho_da_escola.sql

- status_r: Comentada no report.yaml
- tabelas_bq (1):
  - br-mec-segape.projeto_painel_ministro.painel_cde
- campos_select_final (0):
  - Nao foi possivel inferir aliases no SELECT final.

### cnca.sql

- status_r: Ativa no report.yaml
- tabelas_bq (5):
  - br-mec-segape.educacao_dados_mestres.municipio
  - br-mec-segape.projeto_gaia.gaia_cnca
  - br-mec-segape.projeto_painel_ministro.painel_cnca
  - br-mec-segape.projeto_painel_ministro.painel_cnca_investimento
  - br-mec-segape.projeto_painel_ministro.painel_cnca_meta
- campos_select_final (10):
  - aderiuPAT, cantinhosDeLeitura, codIbge, escolasParticipantes, estudantesAvaliacoesContinuas, INT64, municipio, recursosInvestidos, recursosInvestidosArtMun, seloReconhecimento

### cpop.sql

- status_r: Ativa no report.yaml
- tabelas_bq (2):
  - br-mec-segape.educacao_dados_mestres.municipio
  - br-mec-segape.educacao_politica_secadi.secadi_cpop_situacao_municipio
- campos_select_final (7):
  - codIbge, INT64, investimentoCpop, municipioAderiuCpop, numeroCursinhosCpop, numeroMatriculasCpop, numeroProfissionaisBolsistasCpop

### ei_manutencao.sql

- status_r: Ativa no report.yaml
- tabelas_bq (2):
  - br-mec-segape.educacao_dados_mestres.municipio
  - br-mec-segape.educacao_politica_simec.simec_seb_oferta_educacao_infantil_provisorio
- campos_select_final (0):
  - Nao foi possivel inferir aliases no SELECT final.

### escolas_conectadas.sql

- status_r: Ativa no report.yaml
- tabelas_bq (3):
  - br-mec-segape.educacao_dados_mestres.municipio
  - br-mec-segape.projeto_painel_ministro.painel_escolas_conectadas
  - br-mec-segape-sandbox.projeto_segape_dmape_relat_automatico.enec_escolas_apoiadas
- campos_select_final (9):
  - escolasApoiadasMunicipio, escolasEnergiaAdequada, escolasInternetAdequada, escolasWifiAdequado, municipioAderiuEscolasConectadas, percentualEscolasEstadoConectadas, percentualEscolasMunicipioConectadas, STRING, valorRecebidoPDDE

### financiamento_educacao_basica.sql

- status_r: Ativa no report.yaml
- tabelas_bq (4):
  - br-mec-segape.educacao_dados_mestres.municipio
  - br-mec-segape.educacao_politica_fnde.fnde_repasse_programa_municipio
  - br-mec-segape.educacao_politica_fnde.fnde_saldo_programa_municipio
  - br-mec-segape.projeto_gaia.gaia_pnld
- campos_select_final (46):
  - ativoETIEst, ativoETIMun, ativoPDDEEquiEst, ativoPDDEEquiMun, ativoPDDEEst, ativoPDDEMun, ativoPDDEQualEst, ativoPDDEQualMun, ativoPNAEEst, ativoPNAEMun, ativoPNATEEst, ativoPNATEMun, ativoPNLDEst, ativoPNLDMun, inativoETIEst, inativoETIMun, inativoPDDEEquiEst, inativoPDDEEquiMun, inativoPDDEEst, inativoPDDEMun, inativoPDDEQualEst, inativoPDDEQualMun, inativoPNAEEst, inativoPNAEMun, inativoPNATEEst, inativoPNATEMun, inativoPNLDEst, inativoPNLDMun, INT64, matriculasAmpliadasPNLD, municipioAderiuFinanciamentoEducacaoBasica, repasseETIEst, repasseETIMun, repassePDDEEquiEst, repassePDDEEquiMun, repassePDDEEst, repassePDDEMun, repassePDDEQualEst, repassePDDEQualMun, repassePNAEEst, repassePNAEMun, repassePNATEEst, repassePNATEMun, repassePNLDEst, repassePNLDMun, saldoInvestido2025PNLD

### fundeb.sql

- status_r: Ativa no report.yaml
- tabelas_bq (6):
  - br-mec-segape.educacao_dados_mestres.municipio
  - br-mec-segape.educacao_politica_fnde.fnde_salario_educacao_estimativa
  - br-mec-segape.educacao_politica_fnde.fnde_salario_educacao_repasse
  - br-mec-segape.educacao_politica_fundeb.fundeb_condicionalidade
  - br-mec-segape.educacao_politica_fundeb.fundeb_indicador
  - br-mec-segape.indicador_politica_fundeb_base.fundeb_base_repasse_estimativa
- campos_select_final (0):
  - Nao foi possivel inferir aliases no SELECT final.

### indicadores_educacionais.sql

- status_r: Ativa no report.yaml
- tabelas_bq (5):
  - br-mec-segape.educacao_dados_mestres.municipio
  - br-mec-segape.educacao_inep_dados_abertos.censo_escolar_escola
  - br-mec-segape.educacao_inep_dados_abertos.indicadores_educacionais_municipio
  - br-mec-segape.educacao_inep_dados_abertos.inep_adequacao_formacao_docente_municipio
  - br-mec-segape.educacao_inep_dados_abertos.inep_nse_escola
- campos_select_final (0):
  - Nao foi possivel inferir aliases no SELECT final.

### indicadores_gerais.sql

- status_r: Ativa no report.yaml
- tabelas_bq (15):
  - br-mec-segape.educacao_dados_mestres.municipio
  - br-mec-segape.educacao_datasus_dados_abertos.datasus_estimativa_populacao
  - br-mec-segape.educacao_datasus_dados_abertos.datasus_obito_infantil
  - br-mec-segape.educacao_datasus_dados_abertos.datasus_renda_meio_salario_minimo
  - br-mec-segape.educacao_ibge_dados_abertos.ibge_analfabetismo
  - br-mec-segape.educacao_ibge_dados_abertos.ibge_esgotamento
  - br-mec-segape.educacao_ibge_dados_abertos.ibge_estimativa_populacao
  - br-mec-segape.educacao_ibge_dados_abertos.ibge_pessoal_ocupado
  - br-mec-segape.educacao_ibge_dados_abertos.ibge_pib_municipio
  - br-mec-segape.educacao_inep_dados_abertos.censo_escolar_escola
  - br-mec-segape.educacao_inep_dados_abertos.inep_censo_educacao_superior_curso
  - br-mec-segape.educacao_inep_dados_abertos.inep_censo_educacao_superior_ies
  - br-mec-segape.educacao_inep_dados_abertos.sinopses_estatisticas_basica_sexo_raca_cor
  - br-mec-segape.educacao_ipea_dados_abertos.ipea_gini_municipio_brasil
  - br-mec-segape.educacao_ipea_dados_abertos.ipea_idh_municipio_brasil
- campos_select_final (0):
  - Nao foi possivel inferir aliases no SELECT final.

### mais_professores.sql

- status_r: Ativa no report.yaml
- tabelas_bq (3):
  - br-mec-segape.educacao_dados_mestres.municipio
  - br-mec-segape.educacao_politica_pdmlic.pdmlic_beneficiario
  - br-mec-segape.projeto_painel_ministro.painel_pnd_adesao
- campos_select_final (0):
  - Nao foi possivel inferir aliases no SELECT final.

### mulheres_mil.sql

- status_r: Ativa no report.yaml
- tabelas_bq (3):
  - br-mec-segape.educacao_dados_mestres.municipio
  - br-mec-segape.projeto_gaia.gaia_mulheres_mil_matricula
  - br-mec-segape.projeto_gaia.gaia_mulheres_mil_vaga
- campos_select_final (7):
  - codIbge, concluintesMulheresMil, cursosOfertadosMulheresMil, INT64, matriculasMulheresMil, municipioAderiuMulheresMil, vagasMulheresMil

### grafico_mapa_municipio_info.sql

- status_r: Ativa no report.yaml
- tabelas_bq (1):
  - br-mec-segape.educacao_dados_mestres.municipio
- campos_select_final (3):
  - codIbge, municipioNome, UF

### novo_pac.sql

- status_r: Ativa no report.yaml
- tabelas_bq (7):
  - br-mec-segape.educacao_dados_mestres.municipio
  - br-mec-segape.projeto_painel_ministro.painel_novopac_consolidado
  - br-mec-segape.projeto_painel_ministro.painel_novopac_ebserh
  - br-mec-segape.projeto_painel_ministro.painel_novopac_pacto
  - br-mec-segape.projeto_painel_ministro.painel_novopac_selecoes_consolidado
  - br-mec-segape.projeto_painel_ministro.painel_novopac_sesu
  - br-mec-segape.projeto_painel_ministro.painel_novopac_setec
- campos_select_final (59):
  - acoesPrevistasPrimeiraEdicaoNovoPac, crechesNovoPac, crechesPrevistasBrasilNovoPac, escolasTempoIntegralNovoPac, escolasTempoIntegralPrevistasBrasilNovoPac, INT64, investidosMunicipioBasicaNovoPac, investidosMunicipioEptNovoPac, investidosMunicipioHuNovoPac, investidosMunicipioSuperiorNovoPac, investimentoPrevistoPrimeiraEdicaoNovoPac, investimentoSegundaEdicaoNovoPac, municipioContempladoBasicaNovoPac, municipioContempladoEptNovoPac, municipioContempladoHuNovoPac, municipioContempladoNovoPac, municipioContempladoSuperiorNovoPac, obrasConcluidasBasicaNovoPac, obrasConcluidasEptNovoPac, obrasConcluidasSuperiorNovoPac, obrasExecucaoBasicaNovoPac, obrasExecucaoEptNovoPac, obrasExecucaoSuperiorNovoPac, obrasLicitacaoBasicaNovoPac, obrasLicitacaoEptNovoPac, obrasLicitacaoSuperiorNovoPac, obrasMunicipioBasicaNovoPac, obrasMunicipioEptNovoPac, obrasMunicipioHuNovoPac, obrasMunicipioSuperiorNovoPac, obrasRetomadaBasicaNovoPac, obrasRetomadaEptNovoPac, obrasRetomadaSuperiorNovoPac, onibusNovoPac, onibusPrevistosBrasilNovoPac, previstosMunicipioEptNovoPac, previstosMunicipioHuNovoPac, previstosMunicipioSuperiorNovoPac, propostasOnibusCreches, repassadosMunicipioBasicaNovoPac, repassadosMunicipioEptNovoPac, repassadosMunicipioHuNovoPac, repassadosMunicipioSuperiorNovoPac, totalAcoes, totalObrasAprovadasEptBrasilNovoPac, totalObrasAprovadasHuBrasilNovoPac, totalObrasAprovadasNovoPac, totalObrasAprovadasSuperiorBrasilNovoPac, valorInvestidoEptBrasilNovoPac, valorInvestidoHuBrasilNovoPac, valorInvestidoSuperiorBrasilNovoPac, valorPrevistoObrasNovoPac, valorPrevistoTotal, valorPrevistoTotalBrasilNovoPac, valorPrevistoTotalMun, valorRepassadoEptBrasilNovoPac, valorRepassadoHuBrasilNovoPac, valorRepassadoObrasNovoPac, valorRepassadoSuperiorBrasilNovoPac

### novo_pac_charts.sql

- status_r: Ativa no report.yaml
- tabelas_bq (5):
  - br-mec-segape.projeto_painel_ministro.painel_novopac_consolidado
  - br-mec-segape.projeto_painel_ministro.painel_novopac_ebserh
  - br-mec-segape.projeto_painel_ministro.painel_novopac_selecoes_consolidado
  - br-mec-segape.projeto_painel_ministro.painel_novopac_sesu
  - br-mec-segape.projeto_painel_ministro.painel_novopac_setec
- campos_select_final (0):
  - Nao foi possivel inferir aliases no SELECT final.

### pacto_eja.sql

- status_r: Ativa no report.yaml
- tabelas_bq (4):
  - br-mec-segape.educacao_dados_mestres.municipio
  - br-mec-segape.educacao_inep_dados_abertos.censo_escolar_escola
  - br-mec-segape.educacao_politica_inep.inep_censo
  - br-mec-segape.projeto_painel_ministro.painel_pactoeja_pdm
- campos_select_final (18):
  - escolasEstaduaisEja, escolasMunicipaisEja, estudantesBeneficiadosPBA, estudantesBeneficiadosPDM, fonteEscolasEstaduaisEja, fonteEscolasMunicipaisEja, fonteEstudantesBeneficiadosPBA, fonteEstudantesBeneficiadosPDM, fonteInvestimentoPacto, fonteMatriculasEja, fonteObjetivoPactoPelaSuperacaoAnalfabetismo, fonteOQueEPactoPelaSuperacaoAnalfabetismo, fonteTotalEscolasTurmasEja, INT64, investimentoPacto, matriculasEja, municipioAderiuPactoPelaSuperacaoAnalfabetismo, totalEscolasTurmasEja

### panorama_mec_charts.sql

- status_r: Ativa no report.yaml
- tabelas_bq (1):
  - br-mec-segape.educacao_inep_dados_abertos.ideb_municipio
- campos_select_final (0):
  - Nao foi possivel inferir aliases no SELECT final.

### panorama_mec_geral.sql

- status_r: Ativa no report.yaml
- tabelas_bq (7):
  - br-mec-segape.educacao_dados_mestres.municipio
  - br-mec-segape.educacao_inep_dados_abertos.censo_escolar_escola
  - br-mec-segape.educacao_inep_dados_abertos.inep_indicador_educacional_taxa_transicao_municipio
  - br-mec-segape.educacao_inep_dados_abertos.inep_rendimento_escolar_municipio
  - br-mec-segape.educacao_inep_dados_abertos.inep_taxa_distorcao_brasil
  - br-mec-segape.educacao_inep_dados_abertos.inep_taxa_distorcao_municipio
  - br-mec-segape.educacao_inep_indicadores_educacionais.municipio
- campos_select_final (74):
  - abandono5AnoEFPanoramaRedeGeral, abandono9AnoEFPanoramaRedeGeral, abandonoEMRegularPanoramaRedeGeral, anoDistorcaoIdadeSeriePanoramaRedeGeral, anoIndicadoresRendimentoPanoramaRedeGeral, anosFinaisDistorcaoPanoramaRedeGeral, anosFinaisEvasaoPanoramaRedeGeral, anosFinaisMigracaoEJAPanoramaRedeGeral, anosFinaisPromocaoPanoramaRedeGeral, anosFinaisRepetenciaPanoramaRedeGeral, anosIniciaisDistorcaoPanoramaRedeGeral, anosIniciaisEvasaoPanoramaRedeGeral, anosIniciaisMigracaoEJAPanoramaRedeGeral, anosIniciaisPromocaoPanoramaRedeGeral, anosIniciaisRepetenciaPanoramaRedeGeral, anoTransicoesInicioPanoramaRedeGeral, aprovacao5AnoEFPanoramaRedeGeral, aprovacao9AnoEFPanoramaRedeGeral, aprovacaoEMRegularPanoramaRedeGeral, brasilAnosFinaisDistorcaoPanoramaRedeGeral, brasilAnosIniciaisDistorcaoPanoramaRedeGeral, brasilEnsinoMedioDistorcaoPanoramaRedeGeral, ensinoMedioDistorcaoPanoramaRedeGeral, ensinoMedioEvasaoPanoramaRedeGeral, ensinoMedioMigracaoEJAPanoramaRedeGeral, ensinoMedioPromocaoPanoramaRedeGeral, ensinoMedioRepetenciaPanoramaRedeGeral, estadoAnosFinaisDistorcaoPanoramaRedeGeral, estadoAnosIniciaisDistorcaoPanoramaRedeGeral, estadoEnsinoMedioDistorcaoPanoramaRedeGeral, infraAguaPotavelCampoPanoramaRedeGeral, infraAguaPotavelConvencionaisPanoramaRedeGeral, infraAguaPotavelIndigenaPanoramaRedeGeral, infraAguaPotavelQuilombolaPanoramaRedeGeral, infraCozinhaCampoPanoramaRedeGeral, infraCozinhaConvencionaisPanoramaRedeGeral, infraCozinhaIndigenaPanoramaRedeGeral, infraCozinhaQuilombolaPanoramaRedeGeral, infraEnergiaEletricaCampoPanoramaRedeGeral, infraEnergiaEletricaConvencionaisPanoramaRedeGeral, infraEnergiaEletricaIndigenaPanoramaRedeGeral, infraEnergiaEletricaQuilombolaPanoramaRedeGeral, infraEsgotoCampoPanoramaRedeGeral, infraEsgotoConvencionaisPanoramaRedeGeral, infraEsgotoIndigenaPanoramaRedeGeral, infraEsgotoQuilombolaPanoramaRedeGeral, infraLabCienciasCampoPanoramaRedeGeral, infraLabCienciasConvencionaisPanoramaRedeGeral, infraLabCienciasIndigenaPanoramaRedeGeral, infraLabCienciasQuilombolaPanoramaRedeGeral, infraLabInformaticaCampoPanoramaRedeGeral, infraLabInformaticaConvencionaisPanoramaRedeGeral, infraLabInformaticaIndigenaPanoramaRedeGeral, infraLabInformaticaQuilombolaPanoramaRedeGeral, infraPatioCampoPanoramaRedeGeral, infraPatioConvencionaisPanoramaRedeGeral, infraPatioIndigenaPanoramaRedeGeral, infraPatioQuilombolaPanoramaRedeGeral, infraQuadraEsportesCampoPanoramaRedeGeral, infraQuadraEsportesConvencionaisPanoramaRedeGeral, infraQuadraEsportesIndigenaPanoramaRedeGeral, infraQuadraEsportesQuilombolaPanoramaRedeGeral, mediaAlunosTurmaAnosFinaisBrasilPanoramaRedeGeral, mediaAlunosTurmaAnosFinaisEstadoPanoramaRedeGeral, mediaAlunosTurmaAnosFinaisMunicipioPanoramaRedeGeral, mediaAlunosTurmaAnosIniciaisBrasilPanoramaRedeGeral, mediaAlunosTurmaAnosIniciaisEstadoPanoramaRedeGeral, mediaAlunosTurmaAnosIniciaisMunicipioPanoramaRedeGeral, mediaAlunosTurmaEnsinoMedioBrasilPanoramaRedeGeral, mediaAlunosTurmaEnsinoMedioEstadoPanoramaRedeGeral, mediaAlunosTurmaEnsinoMedioMunicipioPanoramaRedeGeral, reprovacao5AnoEFPanoramaRedeGeral, reprovacao9AnoEFPanoramaRedeGeral, reprovacaoEMRegularPanoramaRedeGeral

### panorama_mec_municipio.sql

- status_r: Ativa no report.yaml
- tabelas_bq (9):
  - br-mec-segape.educacao_dados_mestres.municipio
  - br-mec-segape.educacao_inep_dados_abertos.censo_escolar_escola
  - br-mec-segape.educacao_inep_dados_abertos.inep_indicador_educacional_taxa_transicao_municipio
  - br-mec-segape.educacao_inep_dados_abertos.inep_rendimento_escolar_municipio
  - br-mec-segape.educacao_inep_dados_abertos.inep_taxa_distorcao_brasil
  - br-mec-segape.educacao_inep_dados_abertos.inep_taxa_distorcao_municipio
  - br-mec-segape.educacao_inep_indicadores_educacionais.brasil
  - br-mec-segape.educacao_inep_indicadores_educacionais.municipio
  - br-mec-segape.educacao_inep_indicadores_educacionais.uf
- campos_select_final (74):
  - abandono5AnoEFPanorama, abandono9AnoEFPanorama, abandonoEMRegularPanorama, anoDistorcaoIdadeSeriePanorama, anoIndicadoresRendimentoPanorama, anosFinaisDistorcaoPanorama, anosFinaisEvasaoPanorama, anosFinaisMigracaoEJAPanorama, anosFinaisPromocaoPanorama, anosFinaisRepetenciaPanorama, anosIniciaisDistorcaoPanorama, anosIniciaisEvasaoPanorama, anosIniciaisMigracaoEJAPanorama, anosIniciaisPromocaoPanorama, anosIniciaisRepetenciaPanorama, anoTransicoesInicioPanorama, aprovacao5AnoEFPanorama, aprovacao9AnoEFPanorama, aprovacaoEMRegularPanorama, brasilAnosFinaisDistorcaoPanorama, brasilAnosIniciaisDistorcaoPanorama, brasilEnsinoMedioDistorcaoPanorama, ensinoMedioDistorcaoPanorama, ensinoMedioEvasaoPanorama, ensinoMedioMigracaoEJAPanorama, ensinoMedioPromocaoPanorama, ensinoMedioRepetenciaPanorama, estadoAnosFinaisDistorcaoPanorama, estadoAnosIniciaisDistorcaoPanorama, estadoEnsinoMedioDistorcaoPanorama, infraAguaPotavelCampoPanorama, infraAguaPotavelConvencionaisPanorama, infraAguaPotavelIndigenaPanorama, infraAguaPotavelQuilombolaPanorama, infraCozinhaCampoPanorama, infraCozinhaConvencionaisPanorama, infraCozinhaIndigenaPanorama, infraCozinhaQuilombolaPanorama, infraEnergiaEletricaCampoPanorama, infraEnergiaEletricaConvencionaisPanorama, infraEnergiaEletricaIndigenaPanorama, infraEnergiaEletricaQuilombolaPanorama, infraEsgotoCampoPanorama, infraEsgotoConvencionaisPanorama, infraEsgotoIndigenaPanorama, infraEsgotoQuilombolaPanorama, infraLabCienciasCampoPanorama, infraLabCienciasConvencionaisPanorama, infraLabCienciasIndigenaPanorama, infraLabCienciasQuilombolaPanorama, infraLabInformaticaCampoPanorama, infraLabInformaticaConvencionaisPanorama, infraLabInformaticaIndigenaPanorama, infraLabInformaticaQuilombolaPanorama, infraPatioCampoPanorama, infraPatioConvencionaisPanorama, infraPatioIndigenaPanorama, infraPatioQuilombolaPanorama, infraQuadraEsportesCampoPanorama, infraQuadraEsportesConvencionaisPanorama, infraQuadraEsportesIndigenaPanorama, infraQuadraEsportesQuilombolaPanorama, mediaAlunosTurmaAnosFinaisBrasilPanorama, mediaAlunosTurmaAnosFinaisEstadoPanorama, mediaAlunosTurmaAnosFinaisMunicipioPanorama, mediaAlunosTurmaAnosIniciaisBrasilPanorama, mediaAlunosTurmaAnosIniciaisEstadoPanorama, mediaAlunosTurmaAnosIniciaisMunicipioPanorama, mediaAlunosTurmaEnsinoMedioBrasilPanorama, mediaAlunosTurmaEnsinoMedioEstadoPanorama, mediaAlunosTurmaEnsinoMedioMunicipioPanorama, reprovacao5AnoEFPanorama, reprovacao9AnoEFPanorama, reprovacaoEMRegularPanorama

### partiu_if.sql

- status_r: Ativa no report.yaml
- tabelas_bq (2):
  - br-mec-segape.educacao_dados_mestres.municipio
  - br-mec-segape.educacao_politica_secadi.secadi_partiu_if
- campos_select_final (12):
  - codIbge, fontInstituicaoPartiuIF, fontMatriculasPartiuIF, fontTurmasPartiuIF, idIbge, INT64, nomeInstituicaoOfertantePartiuIF, numeroMatriculasPartiuIF, numeroTurmasPartiuIF, STRUCT, totalAlunos, totalTurmas

### pdde_basico.sql

- status_r: Comentada no report.yaml
- tabelas_bq (1):
  - br-mec-segape.projeto_painel_ministro.painel_pdde_basico
- campos_select_final (13):
  - codIbge, fonteNumeroEscolasParticipantesPDDEBasico, fonteObjetivoPDDEBasico, fonteOQueEPDDEBasico, fonteRecebidoEscolaMunicipioPDDEBasico, fonteRepasseEscolasBrasilPDDEBasico, fontValorRecebidoPDDE, INT64, municipioAderiuPDDEBasico, numeroEscolasParticipantesPDDEBasico, recebidoEscolaMunicipioPDDEBasico, repasseEscolasBrasilPDDEBasico, valorRecebidoPDDE

### pdde_equidade.sql

- status_r: Ativa no report.yaml
- tabelas_bq (7):
  - br-mec-segape.educacao_dados_mestres.municipio
  - br-mec-segape-sandbox.projeto_segape_dmape_relat_automatico.pdde_agua_campo_adesao_empenho
  - br-mec-segape-sandbox.projeto_segape_dmape_relat_automatico.pdde_ebs_adesao_empenho
  - br-mec-segape-sandbox.projeto_segape_dmape_relat_automatico.pdde_eja_adesao_empenho
  - br-mec-segape-sandbox.projeto_segape_dmape_relat_automatico.pdde_erer_adesao_empenho
  - br-mec-segape-sandbox.projeto_segape_dmape_relat_automatico.pdde_srm_adesao_empenho
  - br-mec-segape-sandbox.projeto_segape_dmape_relat_automatico.pdde_tee_adesao_empenho
- campos_select_final (21):
  - codIbge, escolasAguaCampo, escolasBilingue, escolasEja, escolasErer, escolasSrm, escolasTee, estudantesAguaCampo, estudantesBilingue, estudantesEja, estudantesErer, estudantesSrm, estudantesTee, INT64, municipioAderiuPDDEEquidade, repasseAguaCampo, repasseBilingue, repasseEja, repasseErer, repasseSrm, repasseTee

### pe_de_meia.sql

- status_r: Ativa no report.yaml
- tabelas_bq (6):
  - br-mec-segape.educacao_dados_mestres.municipio
  - br-mec-segape.educacao_mds_cadunico.pessoa
  - br-mec-segape.educacao_politica_enem.enem_participante_2025_provisorio
  - br-mec-segape.educacao_politica_pdm.incentivo_estudante_historico_completo
  - br-mec-segape.educacao_politica_pdm.matricula_unica_pdm
  - br-mec-segape.educacao_politica_pdm.matricula_unica_pdm_historico
- campos_select_final (33):
  - alunosBeneficidos, codIbge, mediaPorAlunoBrasil, mediaPorAlunoEstado, mediaPorAlunoMunicipio, municipioAderiuPeDeMeia, percentualAlunosBeneficiados, percentualParticipacaoConcluintesBrasil, percentualParticipacaoConcluintesEstado, percentualParticipacaoConcluintesMunicipio, perfilBeneficiariosPorcentagemAmarelo, perfilBeneficiariosPorcentagemBranco, perfilBeneficiariosPorcentagemFeminino, perfilBeneficiariosPorcentagemIndigena, perfilBeneficiariosPorcentagemMasculino, perfilBeneficiariosPorcentagemNegro, perfilBeneficiariosPorcentagemOutroNaoInformado, perfilBeneficiariosPorcentagemPardo, perfilBeneficiariosPorcentagemPessoaComDeficiencia, perfilBeneficiariosPorcentagemPreto, perfilBeneficiariosPorcentagemRacaCorNaoInformado, perfilBeneficiariosQuantidadeAmarelo, perfilBeneficiariosQuantidadeBranco, perfilBeneficiariosQuantidadeFeminino, perfilBeneficiariosQuantidadeIndigena, perfilBeneficiariosQuantidadeMasculino, perfilBeneficiariosQuantidadeNegro, perfilBeneficiariosQuantidadeOutroNaoInformado, perfilBeneficiariosQuantidadePardo, perfilBeneficiariosQuantidadePessoaComDeficiencia, perfilBeneficiariosQuantidadePreto, perfilBeneficiariosQuantidadeRacaCorNaoInformado, valorInvestidoMunicipio

### peti.sql

- status_r: Ativa no report.yaml
- tabelas_bq (3):
  - br-mec-segape.educacao_dados_mestres.municipio
  - br-mec-segape.projeto_painel_ministro.painel_matricula_integral_percentual
  - br-mec-segape.projeto_painel_ministro.painel_peti
- campos_select_final (17):
  - codIbge, existenciaDePoliticaDeTempoIntegral, fonteExistenciaDePoliticaDeTempoIntegral, fonteObjetivoEscolaEmTempoIntegral, fonteOQueEEscolaEmTempoIntegral, fontePercentualDeAlunosEmEscolaEmTempoIntegral, fontePercentualDeEscolasEmTempoIntegral, fonteTotalDeAlunosMatriculadosEmEscolaEmTempoIntegral, municipioAderiuPETI, municipioComEscolaEmTempoIntegral, novasMatriculasEmEscolaEmTempoIntegral, percentualDeAlunosEmEscolaEmTempoIntegral, percentualDeAlunosEmEscolaEmTempoIntegralBrasil, percentualDeEscolasEmTempoIntegral, repassesDoMecParaEscolaEmTempoIntegral, STRING, totalDeAlunosMatriculadosEmEscolaEmTempoIntegral

### pnae.sql

- status_r: Comentada no report.yaml
- tabelas_bq (1):
  - br-mec-segape.projeto_painel_ministro.painel_pnae
- campos_select_final (10):
  - alimentouAlunos, alimentouAlunosBrasil, codIbge, fonteNumeroEscolasApoiadas, fonteRepasse, INT64, municipioAderiuPNAE, numeroEscolasApoiadas, recebidoDestinadosPNAE, repasseParaEscolas

### pnate.sql

- status_r: Comentada no report.yaml
- tabelas_bq (2):
  - br-mec-segape.projeto_gaia.gaia_pnate
  - br-mec-segape.projeto_painel_ministro.painel_pnate
- campos_select_final (12):
  - alunosAtendidos, codIbge, estudantesMunicipio, fonteAlunosAtendidos, fonteNumerosEscolasParticipantes, fonteObjetivoPNATE, fonteOQueEPNATE, INT64, municipioAderiuPNATE, numeroEscolasParticipantes, numeroEstudantesQuePodemTerAcesso, recursoUtilizadosMunicipio

### pneepei.sql

- status_r: Ativa no report.yaml
- tabelas_bq (3):
  - br-mec-segape.educacao_dados_mestres.municipio
  - br-mec-segape.projeto_painel_ministro.painel_pneepei_censo_escolar_escola
  - br-mec-segape.projeto_painel_ministro.painel_pneepei_secadi_formacao
- campos_select_final (15):
  - codIbge, escolasAEE, fonteFormacoes, fonteMatriculasClassesComuns, fonteObjetivoPNEEPEI, fonteOnibusAcessiveis, fonteOQueEPNEEPEI, fonteSalasRecursosMultifuncionais, INT64, matriculasClassesComuns, matriculasCursosRenafor, matriculasPAEE, municipioAderiuPNEEPEI, onibusAcessiveis, salasRecursosMultifuncionais

### pneerq.sql

- status_r: Ativa no report.yaml
- tabelas_bq (5):
  - br-mec-segape.educacao_dados_mestres.municipio
  - br-mec-segape.educacao_inep_dados_abertos.censo_escolar_escola
  - br-mec-segape.educacao_politica_secadi.secadi_pneerq_pdde_eeq
  - br-mec-segape.educacao_politica_secadi.secadi_pneerq_pdde_erer
  - br-mec-segape.educacao_politica_secadi.secadi_programa_consolidado
- campos_select_final (7):
  - codIbge, escolasBeneficiadasPDDEEquidade, INT64, municipioAderiuPNEERQ, seloPetronilha, valorRepasseTotalPDDEEEQ, valorRepasseTotalPDDEERER

### pnld.sql

- status_r: Comentada no report.yaml
- tabelas_bq (2):
  - br-mec-segape.educacao_programa.pnld_core
  - br-mec-segape.projeto_painel_ministro.painel_pnld
- campos_select_final (13):
  - alunosAtendidosPNLD, coberturaMunicipio, codIbge, estudantesAtendidos, fonteObjetivoPNLD, fonteOQuePNLD, fontesEstudantesAtendidos, fontesValorInvestido, INT64, investimentoPorAluno, livrosDistribuidos, municipioAderiuPNLD, valorInvestido

### premio_mais_professores.sql

- status_r: Ativa no report.yaml
- tabelas_bq (2):
  - br-mec-segape.educacao_dados_mestres.municipio
  - br-mec-segape.educacao_politica_inep.inep_premio_mais_professores
- campos_select_final (14):
  - escolasAnosFinais, escolasAnosIniciais, escolasEnsinoMedio, escolasNseAnosFinais, escolasNseAnosIniciais, escolasNseEnsinoMedio, INT64, municipioAderiuPremioMaisProfessores, quantidadeDocentesAnosFinais, quantidadeDocentesAnosIniciais, quantidadeDocentesEnsinoMedio, quantidadeDocentesNseAnosFinais, quantidadeDocentesNseAnosIniciais, quantidadeDocentesNseEnsinoMedio

### premio_mec.sql

- status_r: Ativa no report.yaml
- tabelas_bq (2):
  - br-mec-segape.educacao_dados_mestres.municipio
  - br-mec-segape.educacao_politica_inep.inep_premio_mec_municipio
- campos_select_final (22):
  - codIbge, escolasAlfabetizacao, escolasAnosFinaisMEC, escolasAnosIniciaisMEC, municipioAderiuPremioMEC, premiadoAlfabetizacao, premiadoAnosFinais, premiadoAnosIniciais, premiadoEducInfantil, premiadoTempoIntegralEFFinais, premiadoTempoIntegralEFIniciais, premiadoTempoIntegralPre, premioAlfabetizacaoMunicipio, premioAlfabetizacaoPorEscola, premioAnosFinaisMunicipio, premioAnosFinaisPorEscola, premioAnosIniciaisMunicipio, premioAnosIniciaisPorEscola, premioEducInfantil, premioTempoIntegralEFFinais, premioTempoIntegralEFIniciais, premioTempoIntegralPre

### proditec.sql

- status_r: Ativa no report.yaml
- tabelas_bq (1):
  - br-mec-segape.educacao_dados_mestres.municipio
- campos_select_final (7):
  - codIbge, municipioAderiuProditec, proditecAprovados, proditecInstituicoesParceiras, proditecNaoAprovados, proditecParticipantes, proditecValorTotalInvestido

### proec.sql

- status_r: Ativa no report.yaml
- tabelas_bq (2):
  - , que contÃ©m informaÃ§Ãµes sobre 
--     as escolas apoiadas pelo Proec, valores repassados e o nÃºmero de estudantes, familiares/comunidade 
--     e profissionais impactados.
--     A consulta filtra os dados pelo cÃ³digo IBGE do municÃ­pio fornecido como parÃ¢metro e agrupa os 
--     resultados por municÃ­pio, ano e unidade federativa.
--     O resultado inclui o nÃºmero de escolas apoiadas, valores repassados e o nÃºmero de estudantes, 
--     familiares/comunidade e profissionais impactados no municÃ­pio para o Ãºltimo ano de referÃªncia disponÃ­vel.
-- ParÃ¢metros:
--     cod_ibge: CÃ³digo IBGE do municÃ­pio (ex: 3106200)
-- @indicator proecMunicipioEscolasImpactoValores
WITH
  municipio_info AS (
    SELECT
      id_municipio as cod_ibge,
      nome as municipio_nome,
      sigla_uf as uf_sigla
    FROM 
  - br-mec-segape.educacao_politica_proec.proec_escola_apoiada_planejado
- campos_select_final (6):
  - municipioAderiuProec, proecEscolasBeneficiadas, proecEstudantes, proecFamiliaresComunidade, proecProfissionaisEducacao, proecValorRepassado

### pronatec.sql

- status_r: Ativa no report.yaml
- tabelas_bq (3):
  - br-mec-segape.educacao_dados_mestres.municipio
  - br-mec-segape.projeto_painel_ministro.painel_pronatec_completo
  - br-mec-segape.projeto_painel_ministro.painel_pronatec_matricula
- campos_select_final (7):
  - codIbge, concluintesPronatec, cursosOfertadosPronatec, investimentoPronatec, matriculasPronatec, municipioAderiuPronatec, vagasPronatec

### rede_federal.sql

- status_r: Ativa no report.yaml
- tabelas_bq (6):
  - br-mec-segape.educacao_dados_mestres.municipio
  - br-mec-segape.educacao_ibge_dados_abertos.ibge_censo_2022_populacao_residente_sexo_idade
  - br-mec-segape.educacao_politica_pnp_painel.pnp_painel_instituicao
  - br-mec-segape.educacao_politica_pnp_painel.pnp_painel_servidor
  - br-mec-segape.educacao_politica_pnp_painel.pnp_painel_situacao_matricula
  - br-mec-segape.projeto_gaia.gaia_pnp_matricula
- campos_select_final (12):
  - compostaPorMunicipiosRegiao, docentesFederal, matriculasFederal, matriculasMunicipio, matriculasRegiao, novasUnidadesEmImplantacaoFederal, populacaoRegiao, unidadesDeEnsinoFederal, unidadesExistentesMunicipio, unidadesExistentesRegiao, unidadesNovasMunicipio, unidadesNovasRegiao

### rede_federal_charts.sql

- status_r: Ativa no report.yaml
- tabelas_bq (4):
  - br-mec-segape.educacao_dados_mestres.municipio
  - br-mec-segape.educacao_politica_pnp_painel.pnp_painel_curso
  - br-mec-segape.educacao_politica_pnp_painel.pnp_painel_instituicao
  - br-mec-segape.educacao_politica_pnp_painel.pnp_painel_situacao_matricula
- campos_select_final (0):
  - Nao foi possivel inferir aliases no SELECT final.

## Observacoes

- O mapeamento foi feito por parsing estatico de SQL (regex), sem execucao no BigQuery.
- Em queries com subqueries/CTEs complexas, a lista de campos_select_final pode ficar incompleta.
- Para migracao ao school-report-python, use este inventario como ponto de partida e valide cada output com --data-only.
