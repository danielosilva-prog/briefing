#import "./typst-template.typ": Article

#let empty-data = (
  metadata: (:),
  params: (:),
  queries: (:),
  charts: (:),
  template_params: (:),
)

#let input-file = if "data_file" in sys.inputs {
  sys.inputs.at("data_file")
} else {
  sys.inputs.at("data", default: none)
}

#let data = if input-file != none {
  json(input-file)
} else {
  empty-data
}

#let metadata = data.at("metadata", default: (:))
#let params = data.at("params", default: (:))
#let queries = data.at("queries", default: (:))
#let charts = data.at("charts", default: (:))
#let template-params = data.at("template_params", default: (:))

#let municipio-info = queries.at("municipio_info", default: ())
#let municipio-row = municipio-info.at(0, default: (:))

#let p2-pib-info = queries.at("p2_pib_per_capita", default: ())
#let p2-pib-row = p2-pib-info.at(0, default: (:))

#let p2-pop-info = queries.at("p2_numero_habitantes", default: ())
#let p2-pop-row = p2-pop-info.at(0, default: (:))

#let p2-pop-quilombola-info = queries.at("p2_populacao_quilombola", default: ())
#let p2-pop-quilombola-row = p2-pop-quilombola-info.at(0, default: (:))

#let p2-comunidades-quilombolas-info = queries.at("p2_comunidades_quilombolas_certificadas", default: ())
#let p2-comunidades-quilombolas-row = p2-comunidades-quilombolas-info.at(0, default: (:))

#let p3-condicionalidade-info = queries.at("p3_condicionalidade_iii_vaar", default: ())
#let p3-condicionalidade-row = p3-condicionalidade-info.at(0, default: (:))

#let p2-vaar-media-info = queries.at("p2_vaar_media_uf", default: ())
#let p2-vaar-media-row = p2-vaar-media-info.at(0, default: (:))

#let p2-vaar-previsto-info = queries.at("p2_vaar_previsto_municipio", default: ())
#let p2-vaar-previsto-row = p2-vaar-previsto-info.at(0, default: (:))

#let vaar-rows = queries.at("grafico_vaar_municipio_2023_2025", default: ())
#let vaar-row = vaar-rows.at(2, default: vaar-rows.at(0, default: (:)))

#let cond-info = queries.at("tabela_condicionalidades", default: ())
#let cond-row = cond-info.at(0, default: (:))
#let cond-brasil-info = queries.at("grafico_condicionalidades_brasil", default: ())
#let cond-uf-info = queries.at("grafico_condicionalidades_uf", default: ())

#let infra-table-info = queries.at("tabela_infraestrutura_basica", default: ())
#let infra-table-row = infra-table-info.at(0, default: (:))

#let p6-info = queries.at("p6_diagnostico_equidade", default: ())
#let p6-row = p6-info.at(0, default: (:))

#let percentual-condicionalidade = (rows, cond-key, cond-field, att-field, pct-field) => {
  let filtered = rows.filter(row =>
    row.at(cond-field, default: "") == cond-key and row.at(att-field, default: "") == "true"
  )
  let row = filtered.at(0, default: (:))
  row.at(pct-field, default: 0)
}

#let article-args = (
  ..template-params,
  title: template-params.at(
    "title",
    default: metadata.at("title", default: "AQUI TEM MEC - Devolutivas de Equidade Racial"),
  ),
  municipio: template-params.at(
    "municipio",
    default: municipio-row.at(
      "municipioNome",
      default: municipio-row.at("municipio_nome", default: municipio-row.at("municipio", default: "Albadiania")),
    ),
  ),
  uf: template-params.at(
    "uf",
    default: municipio-row.at("UF", default: municipio-row.at("uf", default: "GO")),
  ),

  // Complementacao VAAR (campos explicitos no padrao do projeto)
  p2PibPerCapita: template-params.at(
    "p2PibPerCapita",
    default: p2-pib-row.at(
      "p2PibPerCapita",
      default: municipio-row.at("pibPerCapita", default: municipio-row.at("pib_per_capita", default: "R$ 35.001,00")),
    ),
  ),
  p2PibPerCapitaAno: template-params.at(
    "p2PibPerCapitaAno",
    default: p2-pib-row.at(
      "p2PibPerCapitaAno",
      default: municipio-row.at("pibPerCapitaAno", default: municipio-row.at("pib_per_capita_ano", default: "2021")),
    ),
  ),
  p2NumeroHabitantes: template-params.at(
    "p2NumeroHabitantes",
    default: p2-pop-row.at(
      "p2NumeroHabitantes",
      default: municipio-row.at("numeroHabitantes", default: municipio-row.at("numero_habitantes", default: "17.232")),
    ),
  ),
  p2NumeroHabitantesAno: template-params.at(
    "p2NumeroHabitantesAno",
    default: p2-pop-row.at(
      "p2NumeroHabitantesAno",
      default: municipio-row.at(
        "numeroHabitantesAno",
        default: municipio-row.at("numero_habitantes_ano", default: "2022"),
      ),
    ),
  ),
  populacaoQuilombola: template-params.at(
    "populacaoQuilombola",
    default: p2-pop-quilombola-row.at(
      "populacaoQuilombola",
      default: municipio-row.at("populacaoQuilombola", default: municipio-row.at("populacao_quilombola", default: "-")),
    ),
  ),
  populacaoQuilombolaAno: template-params.at(
    "populacaoQuilombolaAno",
    default: p2-pop-quilombola-row.at(
      "populacaoQuilombolaAno",
      default: municipio-row.at(
        "populacaoQuilombolaAno",
        default: municipio-row.at("populacao_quilombola_ano", default: "-"),
      ),
    ),
  ),
  comunidadesQuilombolas: template-params.at(
    "comunidadesQuilombolas",
    default: p2-comunidades-quilombolas-row.at(
      "comunidadesQuilombolas",
      default: municipio-row.at(
        "comunidadesQuilombolas",
        default: municipio-row.at("comunidades_quilombolas", default: "-"),
      ),
    ),
  ),
  comunidadesQuilombolasAno: template-params.at(
    "comunidadesQuilombolasAno",
    default: p2-comunidades-quilombolas-row.at(
      "comunidadesQuilombolasAno",
      default: municipio-row.at(
        "comunidadesQuilombolasAno",
        default: municipio-row.at("comunidades_quilombolas_ano", default: "-"),
      ),
    ),
  ),
  p3AnoReferencia: template-params.at(
    "p3AnoReferencia",
    default: p3-condicionalidade-row.at("p3AnoReferencia", default: "-"),
  ),
  p3PercentualRacial2019: template-params.at(
    "p3PercentualRacial2019",
    default: p3-condicionalidade-row.at("p3PercentualRacial2019", default: "-%"),
  ),
  p3PercentualRacial2023: template-params.at(
    "p3PercentualRacial2023",
    default: p3-condicionalidade-row.at("p3PercentualRacial2023", default: "-%"),
  ),
  p3DiferencaPercentualRacial: template-params.at(
    "p3DiferencaPercentualRacial",
    default: p3-condicionalidade-row.at("p3DiferencaPercentualRacial", default: "-%"),
  ),
  reduziuDesigualdadeRacial: template-params.at(
    "reduziuDesigualdadeRacial",
    default: p3-condicionalidade-row.at(
      "reduziuDesigualdadeRacial",
      default: "Ausência de dados suficientes",
    ),
  ),
  margemDeErroDesigualdadeRacial: template-params.at(
    "margemDeErroDesigualdadeRacial",
    default: p3-condicionalidade-row.at("margemDeErroDesigualdadeRacial", default: ""),
  ),
  p3PercentualSocioeconomica2019: template-params.at(
    "p3PercentualSocioeconomica2019",
    default: p3-condicionalidade-row.at("p3PercentualSocioeconomica2019", default: "-%"),
  ),
  p3PercentualSocioeconomica2023: template-params.at(
    "p3PercentualSocioeconomica2023",
    default: p3-condicionalidade-row.at("p3PercentualSocioeconomica2023", default: "-%"),
  ),
  p3DiferencaPercentualSocioeconomica: template-params.at(
    "p3DiferencaPercentualSocioeconomica",
    default: p3-condicionalidade-row.at("p3DiferencaPercentualSocioeconomica", default: "-%"),
  ),
  reduziuDesigualdadeSocioeconomica: template-params.at(
    "reduziuDesigualdadeSocioeconomica",
    default: p3-condicionalidade-row.at(
      "reduziuDesigualdadeSocioeconomica",
      default: "Ausência de dados suficientes",
    ),
  ),
  margemDeErroDesigualdadeSocioeconomica: template-params.at(
    "margemDeErroDesigualdadeSocioeconomica",
    default: p3-condicionalidade-row.at("margemDeErroDesigualdadeSocioeconomica", default: ""),
  ),
  habilitadoCondicionalidade: template-params.at(
    "habilitadoCondicionalidade",
    default: p3-condicionalidade-row.at("habilitadoCondicionalidade", default: "Não"),
  ),
  habilitadoCondicionalidadeMotivo: template-params.at(
    "habilitadoCondicionalidadeMotivo",
    default: p3-condicionalidade-row.at("habilitadoCondicionalidadeMotivo", default: ""),
  ),
  p2AnoReferencia: template-params.at(
    "p2AnoReferencia",
    default: p2-vaar-previsto-row.at(
      "p2AnoReferencia",
      default: str(vaar-row.at("anoReferencia", default: vaar-row.at("ano_referencia", default: 2025))),
    ),
  ),
  p2PortariaReferencia: template-params.at(
    "p2PortariaReferencia",
    default: p2-vaar-previsto-row.at(
      "p2PortariaReferencia",
      default: municipio-row.at(
        "p2PortariaReferencia",
        default: municipio-row.at("p2_portaria_referencia", default: "-"),
      ),
    ),
  ),
  p2ValorComplementacaoVAARAnoReferencia: template-params.at(
    "p2ValorComplementacaoVAARAnoReferencia",
    default: p2-vaar-previsto-row.at(
      "p2ValorComplementacaoVAARAnoReferencia",
      default: str(
        vaar-row.at(
          "valorPrevistoComplementacaoVAARMunicipio",
          default: vaar-row.at(
            "valorRepassadoComplementacaoVAARMunicipio",
            default: vaar-row.at("valor_repassado_complementacao_vaar_municipio", default: 0),
          ),
        ),
      ),
    ),
  ),
  p2ValorComplementacaoVAARMediaUF: template-params.at(
    "p2ValorComplementacaoVAARMediaUF",
    default: p2-vaar-media-row.at(
      "p2ValorComplementacaoVAARMediaUF",
      default: municipio-row.at(
      "valorMedioRecebidoVaarUf",
      default: municipio-row.at(
        "valor_medio_recebido_vaar_uf",
        default: municipio-row.at("p2ValorComplementacaoVAARMediaUF", default: "R$ 58.156.033,12"),
      ),
    ),
    ),
  ),
  p2ValorComplementacaoVAARMediaUFAno: template-params.at(
    "p2ValorComplementacaoVAARMediaUFAno",
    default: p2-vaar-media-row.at("p2ValorComplementacaoVAARMediaUFAno", default: "-"),
  ),
  
  // Condicionalidades (tabela condicionalidades)
  condSelecaoDiretor: template-params.at(
    "condSelecaoDiretor",
    default: cond-row.at("selecaoPorCriteriosTecnicosCargoDiretorEscolar", default: "pendente"),
  ),
  condParticipacaoSaeb: template-params.at(
    "condParticipacaoSaeb",
    default: cond-row.at("participacaoNoSaeb", default: "pendente"),
  ),
  condReducaoDesigualdades: template-params.at(
    "condReducaoDesigualdades",
    default: cond-row.at("reducaoDesigualdades", default: "pendente"),
  ),
  condRegulamentacaoIcms: template-params.at(
    "condRegulamentacaoIcms",
    default: cond-row.at("regulamentacaoICMSEducacionalEstado", default: "pendente"),
  ),
  condReferenciaisBncc: template-params.at(
    "condReferenciaisBncc",
    default: cond-row.at("referenciaisCurricularesAlinhadosBNCC", default: "pendente"),
  ),
  condAvancoAtendimento: template-params.at(
    "condAvancoAtendimento",
    default: cond-row.at("avancarIndicadorAtendimento", default: "pendente"),
  ),
  condAvancoAprendizagem: template-params.at(
    "condAvancoAprendizagem",
    default: cond-row.at("avancarIndicadorAprendizagem", default: "pendente"),
  ),
  condAnoReferencia: template-params.at(
    "condAnoReferencia",
    default: cond-row.at("anoReferencia", default: "-"),
  ),
  percentualCumprimentoCondicionalidade1Brasil: template-params.at(
    "percentualCumprimentoCondicionalidade1Brasil",
    default: percentual-condicionalidade(
      cond-brasil-info,
      "1",
      "condicionalidadeBrasil",
      "atendimentoBrasil",
      "percentualBrasil",
    ),
  ),
  percentualCumprimentoCondicionalidade2Brasil: template-params.at(
    "percentualCumprimentoCondicionalidade2Brasil",
    default: percentual-condicionalidade(
      cond-brasil-info,
      "2",
      "condicionalidadeBrasil",
      "atendimentoBrasil",
      "percentualBrasil",
    ),
  ),
  percentualCumprimentoCondicionalidade3Brasil: template-params.at(
    "percentualCumprimentoCondicionalidade3Brasil",
    default: percentual-condicionalidade(
      cond-brasil-info,
      "3",
      "condicionalidadeBrasil",
      "atendimentoBrasil",
      "percentualBrasil",
    ),
  ),
  percentualCumprimentoCondicionalidade4Brasil: template-params.at(
    "percentualCumprimentoCondicionalidade4Brasil",
    default: percentual-condicionalidade(
      cond-brasil-info,
      "4",
      "condicionalidadeBrasil",
      "atendimentoBrasil",
      "percentualBrasil",
    ),
  ),
  percentualCumprimentoCondicionalidade5Brasil: template-params.at(
    "percentualCumprimentoCondicionalidade5Brasil",
    default: percentual-condicionalidade(
      cond-brasil-info,
      "5",
      "condicionalidadeBrasil",
      "atendimentoBrasil",
      "percentualBrasil",
    ),
  ),
  percentualCumprimentoCondicionalidade1UF: template-params.at(
    "percentualCumprimentoCondicionalidade1UF",
    default: percentual-condicionalidade(
      cond-uf-info,
      "1",
      "condicionalidadeUf",
      "atendimentoUf",
      "percentualUf",
    ),
  ),
  percentualCumprimentoCondicionalidade2UF: template-params.at(
    "percentualCumprimentoCondicionalidade2UF",
    default: percentual-condicionalidade(
      cond-uf-info,
      "2",
      "condicionalidadeUf",
      "atendimentoUf",
      "percentualUf",
    ),
  ),
  percentualCumprimentoCondicionalidade3UF: template-params.at(
    "percentualCumprimentoCondicionalidade3UF",
    default: percentual-condicionalidade(
      cond-uf-info,
      "3",
      "condicionalidadeUf",
      "atendimentoUf",
      "percentualUf",
    ),
  ),
  percentualCumprimentoCondicionalidade4UF: template-params.at(
    "percentualCumprimentoCondicionalidade4UF",
    default: percentual-condicionalidade(
      cond-uf-info,
      "4",
      "condicionalidadeUf",
      "atendimentoUf",
      "percentualUf",
    ),
  ),
  percentualCumprimentoCondicionalidade5UF: template-params.at(
    "percentualCumprimentoCondicionalidade5UF",
    default: percentual-condicionalidade(
      cond-uf-info,
      "5",
      "condicionalidadeUf",
      "atendimentoUf",
      "percentualUf",
    ),
  ),
  tabelaInfraestruturaBasica: template-params.at(
    "tabelaInfraestruturaBasica",
    default: infra-table-info,
  ),
  infraAnoReferencia: template-params.at(
    "infraAnoReferencia",
    default: infra-table-row.at("anoReferencia", default: "-"),
  ),

  // P06 - Diagnostico de Equidade
  mediaIndiceGeralERERMunicipal: template-params.at(
    "mediaIndiceGeralERERMunicipal",
    default: p6-row.at("mediaIndiceGeralERERMunicipal", default: "-"),
  ),
  minimoIndiceGeralERERMunicipal: template-params.at(
    "minimoIndiceGeralERERMunicipal",
    default: p6-row.at("minimoIndiceGeralERERMunicipal", default: "-"),
  ),
  maximoIndiceGeralERERMunicipal: template-params.at(
    "maximoIndiceGeralERERMunicipal",
    default: p6-row.at("maximoIndiceGeralERERMunicipal", default: "-"),
  ),
  medianaIndiceGeralERERMunicipal: template-params.at(
    "medianaIndiceGeralERERMunicipal",
    default: p6-row.at("medianaIndiceGeralERERMunicipal", default: "-"),
  ),
  mediaIndiceGeralERERUF: template-params.at(
    "mediaIndiceGeralERERUF",
    default: p6-row.at("mediaIndiceGeralERERUF", default: "-"),
  ),
  minimoIndiceGeralERERUF: template-params.at(
    "minimoIndiceGeralERERUF",
    default: p6-row.at("minimoIndiceGeralERERUF", default: "-"),
  ),
  maximoIndiceGeralERERUF: template-params.at(
    "maximoIndiceGeralERERUF",
    default: p6-row.at("maximoIndiceGeralERERUF", default: "-"),
  ),
  percentualIndiceGeralERERUF: template-params.at(
    "percentualIndiceGeralERERUF",
    default: p6-row.at("percentualIndiceGeralERERUF", default: none),
  ),
  percentualIndiceGeralERERMunicipal: template-params.at(
    "percentualIndiceGeralERERMunicipal",
    default: p6-row.at("percentualIndiceGeralERERMunicipal", default: none),
  ),
  mediaIndiceGeralERERBrasil: template-params.at(
    "mediaIndiceGeralERERBrasil",
    default: p6-row.at("mediaIndiceGeralERERBrasil", default: "-"),
  ),
  minimoIndiceGeralERERBrasil: template-params.at(
    "minimoIndiceGeralERERBrasil",
    default: p6-row.at("minimoIndiceGeralERERBrasil", default: "-"),
  ),
  maximoIndiceGeralERERBrasil: template-params.at(
    "maximoIndiceGeralERERBrasil",
    default: p6-row.at("maximoIndiceGeralERERBrasil", default: "-"),
  ),
  percentualIndiceGeralERERBrasil: template-params.at(
    "percentualIndiceGeralERERBrasil",
    default: p6-row.at("percentualIndiceGeralERERBrasil", default: none),
  ),
  indiceERER1Media: template-params.at(
    "indiceERER1Media",
    default: p6-row.at("indiceERER1Media", default: "-"),
  ),
  indiceERER1Minimo: template-params.at(
    "indiceERER1Minimo",
    default: p6-row.at("indiceERER1Minimo", default: "-"),
  ),
  indiceERER1Mediana: template-params.at(
    "indiceERER1Mediana",
    default: p6-row.at("indiceERER1Mediana", default: "-"),
  ),
  indiceERER1Maximo: template-params.at(
    "indiceERER1Maximo",
    default: p6-row.at("indiceERER1Maximo", default: "-"),
  ),
  indiceERER2Media: template-params.at(
    "indiceERER2Media",
    default: p6-row.at("indiceERER2Media", default: "-"),
  ),
  indiceERER2Minimo: template-params.at(
    "indiceERER2Minimo",
    default: p6-row.at("indiceERER2Minimo", default: "-"),
  ),
  indiceERER2Mediana: template-params.at(
    "indiceERER2Mediana",
    default: p6-row.at("indiceERER2Mediana", default: "-"),
  ),
  indiceERER2Maximo: template-params.at(
    "indiceERER2Maximo",
    default: p6-row.at("indiceERER2Maximo", default: "-"),
  ),
  indiceERER3Media: template-params.at(
    "indiceERER3Media",
    default: p6-row.at("indiceERER3Media", default: "-"),
  ),
  indiceERER3Minimo: template-params.at(
    "indiceERER3Minimo",
    default: p6-row.at("indiceERER3Minimo", default: "-"),
  ),
  indiceERER3Mediana: template-params.at(
    "indiceERER3Mediana",
    default: p6-row.at("indiceERER3Mediana", default: "-"),
  ),
  indiceERER3Maximo: template-params.at(
    "indiceERER3Maximo",
    default: p6-row.at("indiceERER3Maximo", default: "-"),
  ),
  indiceERER4Media: template-params.at(
    "indiceERER4Media",
    default: p6-row.at("indiceERER4Media", default: "-"),
  ),
  indiceERER4Minimo: template-params.at(
    "indiceERER4Minimo",
    default: p6-row.at("indiceERER4Minimo", default: "-"),
  ),
  indiceERER4Mediana: template-params.at(
    "indiceERER4Mediana",
    default: p6-row.at("indiceERER4Mediana", default: "-"),
  ),
  indiceERER4Maximo: template-params.at(
    "indiceERER4Maximo",
    default: p6-row.at("indiceERER4Maximo", default: "-"),
  ),
  indiceERER5Media: template-params.at(
    "indiceERER5Media",
    default: p6-row.at("indiceERER5Media", default: "-"),
  ),
  indiceERER5Minimo: template-params.at(
    "indiceERER5Minimo",
    default: p6-row.at("indiceERER5Minimo", default: "-"),
  ),
  indiceERER5Mediana: template-params.at(
    "indiceERER5Mediana",
    default: p6-row.at("indiceERER5Mediana", default: "-"),
  ),
  indiceERER5Maximo: template-params.at(
    "indiceERER5Maximo",
    default: p6-row.at("indiceERER5Maximo", default: "-"),
  ),
  indiceERER6Media: template-params.at(
    "indiceERER6Media",
    default: p6-row.at("indiceERER6Media", default: "-"),
  ),
  indiceERER6Minimo: template-params.at(
    "indiceERER6Minimo",
    default: p6-row.at("indiceERER6Minimo", default: "-"),
  ),
  indiceERER6Mediana: template-params.at(
    "indiceERER6Mediana",
    default: p6-row.at("indiceERER6Mediana", default: "-"),
  ),
  indiceERER6Maximo: template-params.at(
    "indiceERER6Maximo",
    default: p6-row.at("indiceERER6Maximo", default: "-"),
  ),
  indiceEEQ1Media: template-params.at(
    "indiceEEQ1Media",
    default: p6-row.at("indiceEEQ1Media", default: "-"),
  ),
  indiceEEQ1Minimo: template-params.at(
    "indiceEEQ1Minimo",
    default: p6-row.at("indiceEEQ1Minimo", default: "-"),
  ),
  indiceEEQ1Mediana: template-params.at(
    "indiceEEQ1Mediana",
    default: p6-row.at("indiceEEQ1Mediana", default: "-"),
  ),
  indiceEEQ1Maximo: template-params.at(
    "indiceEEQ1Maximo",
    default: p6-row.at("indiceEEQ1Maximo", default: "-"),
  ),
  indiceEEQ2Media: template-params.at(
    "indiceEEQ2Media",
    default: p6-row.at("indiceEEQ2Media", default: "-"),
  ),
  indiceEEQ2Minimo: template-params.at(
    "indiceEEQ2Minimo",
    default: p6-row.at("indiceEEQ2Minimo", default: "-"),
  ),
  indiceEEQ2Mediana: template-params.at(
    "indiceEEQ2Mediana",
    default: p6-row.at("indiceEEQ2Mediana", default: "-"),
  ),
  indiceEEQ2Maximo: template-params.at(
    "indiceEEQ2Maximo",
    default: p6-row.at("indiceEEQ2Maximo", default: "-"),
  ),
  indiceEEQ3Media: template-params.at(
    "indiceEEQ3Media",
    default: p6-row.at("indiceEEQ3Media", default: "-"),
  ),
  indiceEEQ3Minimo: template-params.at(
    "indiceEEQ3Minimo",
    default: p6-row.at("indiceEEQ3Minimo", default: "-"),
  ),
  indiceEEQ3Mediana: template-params.at(
    "indiceEEQ3Mediana",
    default: p6-row.at("indiceEEQ3Mediana", default: "-"),
  ),
  indiceEEQ3Maximo: template-params.at(
    "indiceEEQ3Maximo",
    default: p6-row.at("indiceEEQ3Maximo", default: "-"),
  ),
  indiceEEQ4Media: template-params.at(
    "indiceEEQ4Media",
    default: p6-row.at("indiceEEQ4Media", default: "-"),
  ),
  indiceEEQ4Minimo: template-params.at(
    "indiceEEQ4Minimo",
    default: p6-row.at("indiceEEQ4Minimo", default: "-"),
  ),
  indiceEEQ4Mediana: template-params.at(
    "indiceEEQ4Mediana",
    default: p6-row.at("indiceEEQ4Mediana", default: "-"),
  ),
  indiceEEQ4Maximo: template-params.at(
    "indiceEEQ4Maximo",
    default: p6-row.at("indiceEEQ4Maximo", default: "-"),
  ),
  indiceEEQ1Municipio: template-params.at(
    "indiceEEQ1Municipio",
    default: p6-row.at("indiceEEQ1Municipio", default: "-"),
  ),
  indiceEEQ1MediaUF: template-params.at(
    "indiceEEQ1MediaUF",
    default: p6-row.at("indiceEEQ1MediaUF", default: "-"),
  ),
  indiceEEQ1MediaBrasil: template-params.at(
    "indiceEEQ1MediaBrasil",
    default: p6-row.at("indiceEEQ1MediaBrasil", default: "-"),
  ),
  indiceEEQ2Municipio: template-params.at(
    "indiceEEQ2Municipio",
    default: p6-row.at("indiceEEQ2Municipio", default: "-"),
  ),
  indiceEEQ2MediaUF: template-params.at(
    "indiceEEQ2MediaUF",
    default: p6-row.at("indiceEEQ2MediaUF", default: "-"),
  ),
  indiceEEQ2MediaBrasil: template-params.at(
    "indiceEEQ2MediaBrasil",
    default: p6-row.at("indiceEEQ2MediaBrasil", default: "-"),
  ),
  indiceEEQ3Municipio: template-params.at(
    "indiceEEQ3Municipio",
    default: p6-row.at("indiceEEQ3Municipio", default: "-"),
  ),
  indiceEEQ3MediaUF: template-params.at(
    "indiceEEQ3MediaUF",
    default: p6-row.at("indiceEEQ3MediaUF", default: "-"),
  ),
  indiceEEQ3MediaBrasil: template-params.at(
    "indiceEEQ3MediaBrasil",
    default: p6-row.at("indiceEEQ3MediaBrasil", default: "-"),
  ),
  indiceEEQ4Municipio: template-params.at(
    "indiceEEQ4Municipio",
    default: p6-row.at("indiceEEQ4Municipio", default: "-"),
  ),
  indiceEEQ4MediaUF: template-params.at(
    "indiceEEQ4MediaUF",
    default: p6-row.at("indiceEEQ4MediaUF", default: "-"),
  ),
  indiceEEQ4MediaBrasil: template-params.at(
    "indiceEEQ4MediaBrasil",
    default: p6-row.at("indiceEEQ4MediaBrasil", default: "-"),
  ),
  statusRespostaEEQ: template-params.at(
    "statusRespostaEEQ",
    default: p6-row.at("statusRespostaEEQ", default: "Não respondeu esta parte do Diagnóstico"),
  ),
  mediaIndiceInstitucionalizacaoERERMunicipal: template-params.at(
    "mediaIndiceInstitucionalizacaoERERMunicipal",
    default: p6-row.at("mediaIndiceInstitucionalizacaoERERMunicipal", default: "-"),
  ),
  minimoIndiceInstitucionalizacaoERERMunicipal: template-params.at(
    "minimoIndiceInstitucionalizacaoERERMunicipal",
    default: p6-row.at("minimoIndiceInstitucionalizacaoERERMunicipal", default: "-"),
  ),
  medianaIndiceInstitucionalizacaoERERMunicipal: template-params.at(
    "medianaIndiceInstitucionalizacaoERERMunicipal",
    default: p6-row.at("medianaIndiceInstitucionalizacaoERERMunicipal", default: "-"),
  ),
  maximoIndiceInstitucionalizacaoERERMunicipal: template-params.at(
    "maximoIndiceInstitucionalizacaoERERMunicipal",
    default: p6-row.at("maximoIndiceInstitucionalizacaoERERMunicipal", default: "-"),
  ),
  mediaIndiceGestaoEscolarERERMunicipal: template-params.at(
    "mediaIndiceGestaoEscolarERERMunicipal",
    default: p6-row.at("mediaIndiceGestaoEscolarERERMunicipal", default: "-"),
  ),
  minimoIndiceGestaoEscolarERERMunicipal: template-params.at(
    "minimoIndiceGestaoEscolarERERMunicipal",
    default: p6-row.at("minimoIndiceGestaoEscolarERERMunicipal", default: "-"),
  ),
  medianaIndiceGestaoEscolarERERMunicipal: template-params.at(
    "medianaIndiceGestaoEscolarERERMunicipal",
    default: p6-row.at("medianaIndiceGestaoEscolarERERMunicipal", default: "-"),
  ),
  maximoIndiceGestaoEscolarERERMunicipal: template-params.at(
    "maximoIndiceGestaoEscolarERERMunicipal",
    default: p6-row.at("maximoIndiceGestaoEscolarERERMunicipal", default: "-"),
  ),
  mediaIndiceFormacaoERERMunicipal: template-params.at(
    "mediaIndiceFormacaoERERMunicipal",
    default: p6-row.at("mediaIndiceFormacaoERERMunicipal", default: "-"),
  ),
  minimoIndiceFormacaoERERMunicipal: template-params.at(
    "minimoIndiceFormacaoERERMunicipal",
    default: p6-row.at("minimoIndiceFormacaoERERMunicipal", default: "-"),
  ),
  medianaIndiceFormacaoERERMunicipal: template-params.at(
    "medianaIndiceFormacaoERERMunicipal",
    default: p6-row.at("medianaIndiceFormacaoERERMunicipal", default: "-"),
  ),
  maximoIndiceFormacaoERERMunicipal: template-params.at(
    "maximoIndiceFormacaoERERMunicipal",
    default: p6-row.at("maximoIndiceFormacaoERERMunicipal", default: "-"),
  ),
  mediaIndiceMaterialDidaticoParadidaticoERERMunicipal: template-params.at(
    "mediaIndiceMaterialDidaticoParadidaticoERERMunicipal",
    default: p6-row.at("mediaIndiceMaterialDidaticoParadidaticoERERMunicipal", default: "-"),
  ),
  minimoIndiceMaterialDidaticoParadidaticoERERMunicipal: template-params.at(
    "minimoIndiceMaterialDidaticoParadidaticoERERMunicipal",
    default: p6-row.at("minimoIndiceMaterialDidaticoParadidaticoERERMunicipal", default: "-"),
  ),
  medianaIndiceMaterialDidaticoParadidaticoERERMunicipal: template-params.at(
    "medianaIndiceMaterialDidaticoParadidaticoERERMunicipal",
    default: p6-row.at("medianaIndiceMaterialDidaticoParadidaticoERERMunicipal", default: "-"),
  ),
  maximoIndiceMaterialDidaticoParadidaticoERERMunicipal: template-params.at(
    "maximoIndiceMaterialDidaticoParadidaticoERERMunicipal",
    default: p6-row.at("maximoIndiceMaterialDidaticoParadidaticoERERMunicipal", default: "-"),
  ),
  mediaIndiceFinanciamentoERERMunicipal: template-params.at(
    "mediaIndiceFinanciamentoERERMunicipal",
    default: p6-row.at("mediaIndiceFinanciamentoERERMunicipal", default: "-"),
  ),
  minimoIndiceFinanciamentoERERMunicipal: template-params.at(
    "minimoIndiceFinanciamentoERERMunicipal",
    default: p6-row.at("minimoIndiceFinanciamentoERERMunicipal", default: "-"),
  ),
  medianaIndiceFinanciamentoERERMunicipal: template-params.at(
    "medianaIndiceFinanciamentoERERMunicipal",
    default: p6-row.at("medianaIndiceFinanciamentoERERMunicipal", default: "-"),
  ),
  maximoIndiceFinanciamentoERERMunicipal: template-params.at(
    "maximoIndiceFinanciamentoERERMunicipal",
    default: p6-row.at("maximoIndiceFinanciamentoERERMunicipal", default: "-"),
  ),
  mediaIndiceAvaliacaoMonitoramentoERERMunicipal: template-params.at(
    "mediaIndiceAvaliacaoMonitoramentoERERMunicipal",
    default: p6-row.at("mediaIndiceAvaliacaoMonitoramentoERERMunicipal", default: "-"),
  ),
  minimoIndiceAvaliacaoMonitoramentoERERMunicipal: template-params.at(
    "minimoIndiceAvaliacaoMonitoramentoERERMunicipal",
    default: p6-row.at("minimoIndiceAvaliacaoMonitoramentoERERMunicipal", default: "-"),
  ),
  medianaIndiceAvaliacaoMonitoramentoERERMunicipal: template-params.at(
    "medianaIndiceAvaliacaoMonitoramentoERERMunicipal",
    default: p6-row.at("medianaIndiceAvaliacaoMonitoramentoERERMunicipal", default: "-"),
  ),
  maximoIndiceAvaliacaoMonitoramentoERERMunicipal: template-params.at(
    "maximoIndiceAvaliacaoMonitoramentoERERMunicipal",
    default: p6-row.at("maximoIndiceAvaliacaoMonitoramentoERERMunicipal", default: "-"),
  ),
  formacoesERER: template-params.at(
    "formacoesERER",
    default: p6-row.at("formacoesERER", default: "Não respondeu"),
  ),
  revisaoCurriculo: template-params.at(
    "revisaoCurriculo",
    default: p6-row.at("revisaoCurriculo", default: "Não respondeu"),
  ),
  aquisicaoMateriais: template-params.at(
    "aquisicaoMateriais",
    default: p6-row.at("aquisicaoMateriais", default: "Não respondeu"),
  ),
  adocaoCriterioPriorizacao: template-params.at(
    "adocaoCriterioPriorizacao",
    default: p6-row.at("adocaoCriterioPriorizacao", default: "Não respondeu"),
  ),
  // Charts (preparado para uso direto no typst-template, se necessario)
  chartCondicionalidadesUf: template-params.at(
    "chartCondicionalidadesUf",
    default: charts.at("graficoCondicionalidadesUfPercentual", default: none),
  ),
  chartCrescimentoVaarFundeb: template-params.at(
    "chartCrescimentoVaarFundeb",
    default: charts.at("graficoCrescimentoVaarFundeb", default: none),
  ),
  chartCondicionalidadesBrasil: template-params.at(
    "chartCondicionalidadesBrasil",
    default: charts.at("graficoCondicionalidadesBrasilPercentual", default: none),
  ),
  chartVaarMunicipio: template-params.at(
    "chartVaarMunicipio",
    default: charts.at(
      "graficoValoresPrevistosVaarMunicipio",
      default: charts.at("graficoValoresRecebidosVaarMunicipio", default: none),
    ),
  ),
  chartMapaMunicipio: template-params.at(
    "chartMapaMunicipio",
    default: charts.at("graficoMapaMunicipio", default: none),
  ),
  chartAtendimentoCrechePreEscola: template-params.at(
    "chartAtendimentoCrechePreEscola",
    default: charts.at(
      "graficoAtendimentoCrechePreEscola",
      default: charts.at("chartAtendimentoCrechePreEscola", default: none),
    ),
  ),
  chartDistribuicaoMatriculas: template-params.at(
    "chartDistribuicaoMatriculas",
    default: charts.at("graficoDistribuicaoMatriculas", default: charts.at("chartDistribuicaoMatriculas", default: none)),
  ),
  chartDeclaracaoRacial: template-params.at(
    "chartDeclaracaoRacial",
    default: charts.at("graficoDeclaracaoRacial", default: charts.at("chartDeclaracaoRacial", default: none)),
  ),
  chartAlunosAprendizagemAdequada: template-params.at(
    "chartAlunosAprendizagemAdequada",
    default: charts.at(
      "graficoCondicionalidadeIIIDesigualdadeRacial",
      default: charts.at("chartAlunosAprendizagemAdequada", default: none),
    ),
  ),
  chartAlunosBaixoNSE: template-params.at(
    "chartAlunosBaixoNSE",
    default: charts.at(
      "graficoCondicionalidadeIIIDesigualdadeSocioeconomica",
      default: charts.at("chartAlunosBaixoNSE", default: none),
    ),
  ),
  chartNivelFormacaoProfessores: template-params.at(
    "chartNivelFormacaoProfessores",
    default: charts.at(
      "graficoNivelFormacaoProfessores",
      default: charts.at("chartNivelFormacaoProfessores", default: none),
    ),
  ),
  chartInfraestruturaBasicaEmptyState: template-params.at(
    "chartInfraestruturaBasicaEmptyState",
    default: charts.at("graficoInfraestruturaBasicaEmptyState", default: none),
  ),
  chartTaxaRendimento: template-params.at(
    "chartTaxaRendimento",
    default: charts.at("graficoTaxaRendimento", default: charts.at("chartTaxaRendimento", default: none)),
  ),
)

#Article(..article-args)[]
