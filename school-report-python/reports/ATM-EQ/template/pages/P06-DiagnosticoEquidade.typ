#import "../components/style.typ": *

#import "../components/header.typ": Header

#let indiceErer(dadosIndice: (), corFundo: white, corTitulo: black, corIndicadores: txAzulClaro, corRotulos: txCinzaMedio) = {

  [
    #align(center)[
      #shadow(blur: 4pt, dx: 1pt, dy: 1pt,  fill: rgb(0, 0, 0, 25%))[
        #box(
          fill: corFundo,
          inset: (top:.45cm, x: .35cm, bottom: .35cm),
          width: 100%,
        )[
          #set par(leading: .8em)
          #text(size: 8pt, hyphenate: false, fill: corTitulo)[#dadosIndice.titulo]
          #v(-.05cm)
          #text(size: 7pt, fill: corRotulos)[Média]
          #v(-.5cm)
          #text(size: 16pt, fill: corIndicadores, weight: "black")[#format-no-zero(dadosIndice.media)]
          /*
          #v(-.35cm)
          #grid(
            columns: (1fr, 1fr, 1fr),
            align(center)[
              #box(
                width: 100%,
              )[
                #text(size: 6pt, fill: corRotulos)[Mínimo]
                #v(-.25cm)
                #text(size: 10pt, fill: corIndicadores, weight: "black")[#format-no-zero(dadosIndice.minimo)]
              ]
            ],
            align(center)[
              #box(
                width: 100%,
              )[
                #text(size: 6pt, fill: corRotulos)[Mediana]
                #v(-.25cm)
                #text(size: 10pt, fill: corIndicadores, weight: "black")[#format-no-zero(dadosIndice.mediana)]
              ]
            ],
            align(center)[
              #box(
                width: 100%,
              )[
                #text(size: 6pt, fill: corRotulos)[Máxima]
                #v(-.25cm)
                #text(size: 10pt, fill: corIndicadores, weight: "black")[#format-no-zero(dadosIndice.maximo)]
              ]
            ]
          )
          */
        ]
      ]
    ]
  ]
}

#let indiceComparativo(..args) = {

  let dadosIndice = args.at(0)

  [
    #align(center)[
      #shadow(blur: 4pt, dx: 1pt, dy: 1pt,  fill: rgb(0, 0, 0, 25%))[ 
        #box(
          fill: white,
          inset: (top:.35cm, x: .25cm, bottom: .25cm),
          width: 100%,
        )[
          #set par(leading: .8em)
          #text(size: 8pt, hyphenate: false)[#dadosIndice.titulo]
          #v(-.1cm)
          #let naoRespondeuDiagnostico = (
            dadosIndice.status == "Não respondeu esta parte do Diagnóstico"
          )
          #if naoRespondeuDiagnostico [
            #v(.25cm)
            #align(center)[
              #text(size: 8.5pt, fill: txCinzaClaro, weight: "bold")[Não respondeu esta#linebreak()parte do Diagnóstico]
            ]
            #v(.8cm)
          ] else [
            #v(.125cm)
            #align(center)[#text(size: 7pt, fill: rgb("999"))[Município]]
            #v(-.52cm)
            //#text(size: 16pt, fill: txAzulClaro, weight: "black")[#dadosIndice.municipio]
            #let valorMunicipio = if dadosIndice.municipio != none {
              format-no-zero(dadosIndice.municipio)
            } else {
              " "
            }
            #text(valorMunicipio, size: 16pt, fill: txAzulClaro, weight: "black")
            #v(-.32cm)
            #grid(
              columns: (1fr, 1fr),
              gutter: .35cm,
              align(center)[
                #box(
                  width: 100%,
                )[
                  #align(center)[#text(size: 6pt, fill: rgb("999"))[Média UF]]
                  #v(-.25cm)
                  #align(center)[#text(size: 10pt, fill: txAzulClaro, weight: "black")[#format-no-zero(dadosIndice.mediaUF)]]
                ]
              ],
              align(center)[
                #box(
                  width: 100%,
                )[
                  #align(center)[#text(size: 6pt, fill: rgb("999"))[Média Brasil]]
                  #v(-.25cm)
                  #align(center)[#text(size: 10pt, fill: txAzulClaro, weight: "black")[#format-no-zero(dadosIndice.mediaBrasil)]]
                ]
              ]
            )
          ]
        ]
      ]
    ]
  ]
}

#let DiagnosticoEquidade(..args) = {

  let dados = args.at(0)

  let indiceERER1 = (
    titulo: [Institucionalização#linebreak()ERER],
    media: dados.indiceERER1Media,
    minimo: dados.indiceERER1Minimo,
    mediana: dados.indiceERER1Mediana,
    maximo: dados.indiceERER1Maximo
  )

  let indiceERER2 = (
    titulo: [Formação#linebreak()ERER],
    media: dados.indiceERER2Media,
    minimo: dados.indiceERER2Minimo,
    mediana: dados.indiceERER2Mediana,
    maximo: dados.indiceERER2Maximo,
  )

  let indiceERER3 = (
    titulo: [Gestão Escolar#linebreak()ERER],
    media: dados.indiceERER3Media,
    minimo: dados.indiceERER3Minimo,
    mediana: dados.indiceERER3Mediana,
    maximo: dados.indiceERER3Maximo,
  )

  let indiceERER4 = (
    titulo: [Material Didático &#linebreak()Paradidático ERER],
    media: dados.indiceERER4Media,
    minimo: dados.indiceERER4Minimo,
    mediana: dados.indiceERER4Mediana,
    maximo: dados.indiceERER4Maximo,
  )

  let indiceERER5 = (
    titulo: [Financiamento#linebreak()ERER],
    media: dados.indiceERER5Media,
    minimo: dados.indiceERER5Minimo,
    mediana: dados.indiceERER5Mediana,
    maximo: dados.indiceERER5Maximo,
  )

  let indiceERER6 = (
    titulo: [Avaliação &#linebreak()Monitoramento ERER],
    media: dados.indiceERER6Media,
    minimo: dados.indiceERER6Minimo,
    mediana: dados.indiceERER6Mediana,
    maximo: dados.indiceERER6Maximo,
  )

  let indiceEEQ1 = (
    titulo: [Institucionalização#linebreak()EEQ],
    municipio: dados.indiceEEQ1Municipio,
    mediaUF: dados.indiceEEQ1MediaUF,
    mediaBrasil: dados.indiceEEQ1MediaBrasil,
    status: dados.statusRespostaEEQ,
  )

  let indiceEEQ2 = (
    titulo: [Formação#linebreak()EEQ],
    municipio: dados.indiceEEQ2Municipio,
    mediaUF: dados.indiceEEQ2MediaUF,
    mediaBrasil: dados.indiceEEQ2MediaBrasil,
    status: dados.statusRespostaEEQ,
  )

  let indiceEEQ3 = (
    titulo: [Gestão#linebreak()EEQ],
    municipio: dados.indiceEEQ3Municipio,
    mediaUF: dados.indiceEEQ3MediaUF,
    mediaBrasil: dados.indiceEEQ3MediaBrasil,
    status: dados.statusRespostaEEQ,
  )

  let indiceEEQ4 = (
    titulo: [Material Didático &#linebreak()Paradidático EEQ],
    municipio: dados.indiceEEQ4Municipio,
    mediaUF: dados.indiceEEQ4MediaUF,
    mediaBrasil: dados.indiceEEQ4MediaBrasil,
    status: dados.statusRespostaEEQ,
  )

  [

    #Header(
      titulo: [#text(weight: "extrabold")[Diagnóstico] para compreensão #linebreak()de desigualdades raciais],
      municipio: dados.municipio,
      uf: dados.uf,
      bgColor: rgb("0C8C59"),
      esconderDoSumario: true
    )

    #align(center)[
      #box(
        stroke: .75pt + txCinza,
        inset: (top: 12pt, x: 8pt, bottom: 7pt),
      )[
        #text(
          weight: weightSubtitle,
          size: sizeTitle,
          fill: rgb(txCinza),
        )[#upper[Dados do Diagnóstico de Equidade (PNEERQ - 2024)]]
      ]
    ]

    #v(.1cm)

    #box()[
      #text(fill:txCinza, size: sizeBodySmall)[
        O índice geral de ERER varia de 0 a 100 e é calculado a partir da média ponderada de seis dimensões: #strong[institucionalização],  #strong[formação],  #strong[gestão escolar] (ações e legislação),  #strong[material didático e paradidático],  #strong[financiamento] e  #strong[avaliação e monitoramento]. Valores mais elevados indicam maior nível de implementação das ações. Os valores de mínimo, mediana e máximo representam a distribuição dos resultados entre as redes com dados disponíveis, e a posição da rede indica seu desempenho relativo no contexto estadual e nacional. 
      ]
    ]

    #v(.5cm)

    #grid(
      columns: (48%, 48%),
      gutter: 4%,
      align(center)[
        #box(width: 100%, inset: (top: .5cm, x: .5cm, bottom: .35cm))[

          #v(-.25cm)

          #box(width: 100%, inset: (bottom: .5cm))[
            #text(weight: "medium", size: sizeBodySmall)[Média do índice geral de ERER #linebreak() da rede municipal]
            #v(-.5cm)
            #text(fill: txAzulClaro, weight: "black", size: sizeTotalizerBig)[#format-no-zero(dados.mediaIndiceGeralERERMunicipal)]
          ]

          #text(fill: txCinza, weight: "extrabold")[#upper[Posição do índice geral de ERER #linebreak() da rede municipal na UF]]

          #v(-.125cm)

          #text(weight: "medium", size: sizeBodySmall)[Índice geral]
          #v(-.25cm)

          #align(center + horizon)[
            #grid(
              columns: (auto, 1fr, auto),
              gutter: .5cm,
              align(center)[
                #text(fill: txCinza, weight: "black", size: 12pt)[#format-no-zero(dados.minimoIndiceGeralERERUF)]
              ],
              align(left)[
                #move(dy: -.09cm)[
                  #box(width: 100%, height: .75cm)[
                    #image("../assets/backgrounds/gradient.svg", width: 100%, height: 100%)
                  ]
                ]
                #place(top + left)[
                  #if dados.percentualIndiceGeralERERMunicipal != none {
                    let percentual = float(dados.percentualIndiceGeralERERMunicipal)
                    move(dy: -.20cm, dx: percentual * 1%)[
                      #box(fill: txCinza, width: 2pt, height: 1cm)
                    ]
                  }
                ]
              ],
              align(center)[
                #text(fill: txCinza, weight: "black", size: 12pt)[#format-no-zero(dados.maximoIndiceGeralERERUF)]
              ]
            )
            #v(-.25cm)
            #text(fill: txCinza, weight: "black", size: 12pt)[#format-no-zero(dados.mediaIndiceGeralERERMunicipal)]

            #v(.5cm)

            #text(fill: txCinza, weight: "extrabold")[#upper[Posição do índice geral de ERER #linebreak() da rede municipal no Brasil]]
            #v(-.125cm)
            #text(weight: "medium", size: sizeBodySmall)[Índice geral]
            #v(-.25cm)

            #grid(
              columns: (auto, 1fr, auto),
              gutter: .5cm,
              align(center)[
                #text(fill: txCinza, weight: "black", size: 12pt)[#format-no-zero(dados.minimoIndiceGeralERERBrasil)]
              ],
              align(left)[
                #move(dy: -.09cm)[
                  #box(width: 100%, height: .75cm)[
                    #image("../assets/backgrounds/gradient.svg", width: 100%, height: 100%)
                  ]
                ]
                #place(top + left)[
                  #if dados.percentualIndiceGeralERERBrasil != none {
                    let percentualBrasil = float(dados.percentualIndiceGeralERERBrasil)
                    move(dy: -.20cm, dx: percentualBrasil * 1%)[
                      #box(fill: txCinza, width: 2pt, height: 1cm)
                    ]
                  }
                ]
              ],
              align(center)[
                #text(fill: txCinza, weight: "black", size: 12pt)[#format-no-zero(dados.maximoIndiceGeralERERBrasil)]
              ]
            )
            #v(-.25cm)
            #text(fill: txCinza, weight: "black", size: 12pt)[#format-no-zero(dados.mediaIndiceGeralERERMunicipal)]

          ]
        ]
      ],
      align(center)[
        //#box(width: 100%, stroke: 1pt + borderCinza, inset: (top: .5cm, x: .5cm, bottom: .35cm))[
        #v(.1cm)
        #box(width: 100%)[
          #text(fill: txCinza, weight: "extrabold")[#upper[Índices resumidos ERER]]
          #v(-.25cm)
          #grid(
            columns: (1fr, 1fr),
            gutter: 0cm,
            indiceErer(dadosIndice: indiceERER1),
            indiceErer(dadosIndice: indiceERER2),
            indiceErer(dadosIndice: indiceERER3),
            indiceErer(dadosIndice: indiceERER4),
            indiceErer(dadosIndice: indiceERER5),
            indiceErer(dadosIndice: indiceERER6),
          )

          #v(-.15cm)
          
          #box(inset:(left:.25cm))[
            #align(center + horizon)[
              #link("https://www.gov.br/mec/pt-br/pneerq/diagnostico-de-equidade-na-educacao")[
                #grid(
                  columns: (auto, auto),
                  gutter: 0cm,
                  align(left)[
                    #set par(leading: .75em)
                    #box(fill: rgb("265793"), radius:4pt, inset: (x:.5cm, top: .5cm, bottom: .4cm))[
                      #align(left)[
                        #text(fill: white, weight: "bold")[Acesse todos os dados do#linebreak()Diagnóstico de Equidade]
                      ]
                    ]
                  ],
                  move(dx: -.25cm)[
                    #shadow(blur: 4pt, dx: 1pt, dy: 1pt,  fill: rgb(0, 0, 0, 25%), radius: 4pt)[
                      #box(
                        fill: white,
                        inset: .125cm,
                        radius: 4pt,
                        width: 1.8cm
                      )[#image("../assets/qrcodes/py/todos-os-dados-do-diagnostico-de-equidade.svg", width: 100%)]
                    ]
                  ],
                )
              ]
            ]
          ]
          
        ]
      ]
    )

    #v(.75cm)

    #set par(justify: false)

    #align(center + top)[
      #grid(
        columns: (1fr, 1fr, 1fr, 1fr),
        gutter: 2.5%,
        align(center)[
          #text(fill: txAzulClaro, weight: "black", size: 14pt)[#upper[#dados.formacoesERER]]
          #v(-.25cm)
          #text(weight: "medium", size: sizeBodySmall*.9)[Formações voltadas à ERER desde a sanção da Lei 10.639/2003]
        ],
        align(center)[
          #text(fill: txAzulClaro, weight: "black", size: 14pt)[#upper[#dados.revisaoCurriculo]]
          #v(-.25cm)
          #text(weight: "medium", size: sizeBodySmall*.9)[Revisão do currículo da rede para alinhamento com a Lei 10.639/2003]
        ],
        align(center)[
          #text(fill: txAzulClaro, weight: "black", size: 14pt)[#upper[#dados.aquisicaoMateriais]]
          #v(-.25cm)
          #text(weight: "medium", size: sizeBodySmall*.9)[Aquisição de materiais pedagógicos que promovam a diversidade étnico-racial]
        ],
        align(center)[
          #text(fill: txAzulClaro, weight: "black", size: 14pt)[#upper[#dados.adocaoCriterioPriorizacao]]
          #v(-.25cm)
          #text(weight: "medium", size: sizeBodySmall*.9)[Adoção de critério socioeconômico para priorização de vagas em creche]
        ],
      )
    ]

    #v(.75cm)

    #align(center)[
      //#box(width: 100%, stroke: 1pt + borderCinza, inset: (top: .5cm, x: .5cm, bottom: .35cm))[
      #box(width: 100%)[
        // , ou informação de “Não respondeu esta parte do diagnóstico”
        #text(fill: txCinza, weight: "extrabold")[#upper[Índices de equidade - Educação Escolar Quilombola]]
        #v(-.25cm)

        #grid(
          columns: (1fr, 1fr, 1fr, 1fr),
          gutter: 0cm,
          indiceComparativo(indiceEEQ1),
          indiceComparativo(indiceEEQ2),
          indiceComparativo(indiceEEQ3),
          indiceComparativo(indiceEEQ4),
        )
        #text(size: sizeCaption, fill: txCinza)[#strong[Fonte:] MEC/SECADI (2024)]
      ]
    ]

  ]
}
