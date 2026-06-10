#import "../components/style.typ": *

#import "../components/header.typ": Header
#import "../components/footer.typ": Footer

#let EstrategiasAspectosPedagogicos(..args) = {
  let dados = args.at(0)

  [

    #Header(
      titulo: [#text(weight: "extrabold")[Estratégias] de ação para a #linebreak()promoção da equidade racial],
      municipio: dados.municipio,
      uf: dados.uf,
      bgColor: rgb("265793"),
      textoDoSumario: "Estratégias: Aspectos pedagógicos",
      esconderDoSumario: true
    )

    #v(-.5cm)
    #hide[== Aspectos pedagógicos]

    #grid(
      columns: (auto, 1fr),
      gutter: .5cm,
      box(
        fill: rgb("00000050"),
        radius: (top-left: 2cm),
        width: 2cm,
        height: 2cm,
        inset: (left: .82cm, top: 1.25cm),
      )[#text(fill: white, weight: "black", size: 64pt)[3]],
      box(
        inset: (top: .7cm),
      )[
        #set par(leading: 14pt)
        #text(size: 18pt, weight: "light", fill: black)[Aspectos #linebreak() #text(weight: "extrabold")[Pedagógicos]]
      ],
    )

    #box(
      inset: (right: 0cm),
    )[
      #set text(fill: black, size: sizeBodySmall)

      #set par(spacing: 1.5em)

      #box(
        fill: rgb("EAEAEA50"),
        inset: (top: .75cm, right: .75cm, bottom: .7cm, left: .75cm),
        radius: (top-right: 20pt, bottom-left: 20pt),
      )[

        #set par(leading: 1em, spacing: 20pt)
        O trabalho pedagógico antirracista na rede de ensino é essencial para o enfrentamento das desigualdades raciais de acesso, permanência, aprendizagem e conclusão, inclusive na modalidade da Educação Escolar Quilombola. Nesse sentido, é possível:​

        #align(left + horizon)[
          #grid(
            columns: (auto, 1fr),
            gutter: .25cm,
            row-gutter: 18pt,
            align(center + horizon)[
              #box(width: .8cm, height: .8cm, fill: pneerqLaranja, radius: 50%, inset: (top: .15cm))[
                #text(size: 14pt, weight: "black", fill: white)[1]]
            ],
            text(size: 9pt)[
              ​Uso dos #strong[indicadores escolares desagregados por raça/cor] para elaboração, acompanhamento e monitoramento da #strong[proposta pedagógica da escola e planejamento docente].
            ],

            align(center + horizon)[
              #box(width: .8cm, height: .8cm, fill: pneerqLaranja, radius: 50%, inset: (top: .15cm))[
                #text(size: 14pt, weight: "black", fill: white)[2]]
            ],
            text(size: 9pt)[
              #strong[Gestão da Aprendizagem:] desenvolver estratégias específicas para promover o desenvolvimento das competências essenciais e estruturantes, personalizando o ensino e atendendo às necessidades individuais de cada um dos estudantes com maior defasagem, garantindo a oferta de Recuperação, Reforço e Recomposição de Aprendizagens, apoiando a construção dos conhecimentos escolares de acordo com a idade e ano de matrícula.​
            ],

            align(center + horizon)[
              #box(width: .8cm, height: .8cm, fill: pneerqLaranja, radius: 50%, inset: (top: .15cm))[
                #text(size: 14pt, weight: "black", fill: white)[3]]
            ],
            text(size: 9pt)[
              #strong[​Reorientação da organização escolar, o currículo e as práticas pedagógicas docentes:] a partir da definição de matriz de referência com as habilidades prioritárias para cada turma conforme as necessidades evidenciadas nas avaliações diagnósticas e formativas. Esta reorientação deve guiar o planejamento docente, a adaptação das práticas pedagógicas, a organização ou aquisição de materiais didáticos.​
            ],

            align(center + horizon)[
              #box(width: .8cm, height: .8cm, fill: pneerqLaranja, radius: 50%, inset: (top: .15cm))[
                #text(size: 14pt, weight: "black", fill: white)[4]]
            ],
            text(size: 9pt)[
              #strong[​Desenvolvimento de projetos pedagógicos transversais:] fundamentados na construção das identidades étnico-raciais e culturais dos estudantes, são elementos centrais para promover engajamento e pertencimento, assegurando que os conteúdos abordados reflitam positivamente os conhecimentos, as produções e contribuições.​
            ],

            align(center + horizon)[
              #box(width: .8cm, height: .8cm, fill: pneerqLaranja, radius: 50%, inset: (top: .15cm))[
                #text(size: 14pt, weight: "black", fill: white)[5]]
            ],
            text(size: 9pt)[
              #strong[​Apoio direcionado:] priorizar a permanência de professores (preferencialmente PPI) em número suficiente e com formação inicial adequada, o acompanhamento pedagógico e o suporte às escolas com maior número de estudantes pretos, pardos e indígenas (PPI).​
            ],

            align(center + horizon)[
              #box(width: .8cm, height: .8cm, fill: pneerqLaranja, radius: 50%, inset: (top: .15cm))[
                #text(size: 14pt, weight: "black", fill: white)[6]]
            ],
            box(inset: (top: .2cm))[
              #text(size: 9pt)[
                #strong[Busca Ativa Escolar:] implementar ações de busca ativa nos territórios com as maiores taxas de infrequência, abandono e evasão, visando a retomada da trajetória educacional.​
              ]
            ],

            align(center + horizon)[
              #box(width: .8cm, height: .8cm, fill: pneerqLaranja, radius: 50%, inset: (top: .16cm))[
                #text(size: 14pt, weight: "black", fill: white)[7]]
            ],
            box(inset: (top: .2cm))[
              #text(size: 9pt, weight: "bold")[
                Gestão Pedagógica Antirracista:
              ]
            ],
          )
        ]

        //#v(-.955cm)

        #box(inset: (left: 1cm))[

          #align(left + horizon)[
            #grid(
              columns: (auto, 1fr),
              gutter: .25cm,
              row-gutter: 18pt,
              align(center + top)[
                #v(-.15cm)
                #box(width: .6cm, height: .6cm, fill: pneerqLaranja, radius: 50%, inset: (top: .25cm))[
                  #text(size: 12pt, weight: "black", fill: white)[a]]
              ],
              text(size: 9pt)[
                #strong[Revisar e aprimorar os Projetos Político-Pedagógicos (PPPs) e materiais pedagógicos] objetivando a inserção da educação para as relações étnico-raciais de forma transversal e interdisciplinar de escolas regulares e, no caso de escolas quilombolas, inserir materiais específicos de EEQ.
              ],

              align(center + top)[
                #v(-.15cm)
                #box(width: .6cm, height: .6cm, fill: pneerqLaranja, radius: 50%, inset: (top: .28cm))[
                  #text(size: 12pt, weight: "black", fill: white)[b]]
              ],
              text(size: 9pt)[
                #strong[Propiciar aos profissionais da educação] formação continuada, grupos de estudo, pesquisas sobre equidade racial e diretrizes nacionais de EEQ e seus desdobramentos no processo de aprendizagem, na escolarização e no ambiente escolar, em parceria, onde for possível, com os NEABIs.
              ],

              align(center + top)[
                #v(-.15cm)
                #box(width: .6cm, height: .6cm, fill: pneerqLaranja, radius: 50%, inset: (top: .25cm))[
                  #text(size: 12pt, weight: "black", fill: white)[c]]
              ],
              text(size: 9pt)[
                #strong[Estabelecer e apoiar gestores na aplicação de parâmetros de enturmação] escolar antirracistas, expressando a diversidade étnico-racial brasilera, vedando a existência de classes e turmas étnica-racialmente homogêneas.
              ],
            )
          ]
        ]

        #align(left + horizon)[
          #grid(
            columns: (auto, 1fr),
            gutter: .25cm,
            row-gutter: 18pt,
            align(center + horizon)[
              #box(width: .8cm, height: .8cm, fill: pneerqLaranja, radius: 50%, inset: (top: .15cm))[
                #text(size: 14pt, weight: "black", fill: white)[8]]
            ],
            box(inset: (top: .2cm, right: 3cm))[
              #text(size: 9pt)[
                #strong[Pedagogias de hip hop:] implementar inovação curricular por meio da valorização e da integração de pedagogias e culturas de Hip Hop. O Programa Escola Nacional de Hip Hop, instituído pela Portaria MEC nº 297/2026, tem como objetivo apoiar as redes de ensino neste sentido; conheça o Programa no QR Code ao lado.
              ]
            ]
          )
        ]

        #place(right + bottom, dx: 0cm, dy: 1.5cm)[
          #shadow(blur: 4pt, dx: 1pt, dy: 1pt,  fill: rgb(0, 0, 0, 25%), radius: 4pt)[
            #box(
              fill: white,
              inset: .25cm,
              radius: (top: 4pt),
              width: 2.5cm
            )[#image("../assets/qrcodes/py/escola-do-hip-hop.svg", width: 100%)]
          ]
          #v(-.7cm)
          #shadow(blur: 4pt, dx: 1pt, dy: 1pt,  fill: rgb(0, 0, 0, 25%), radius: (top-left: 4pt, bottom-right: 4pt))[
            #box(fill: txPreto, inset: (top:6pt, x: 4pt, bottom:4pt), radius: (top-left: 4pt, bottom-right: 4pt), width:2.6cm)[
              #text("Escola do hip hop", fill: txBranco, weight: "bold", size: sizeBody * 0.7)
            ]
          ]
        ]
        
      ]
    ]
  ]
}
