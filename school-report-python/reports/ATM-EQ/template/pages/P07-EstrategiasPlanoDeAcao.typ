#import "../components/style.typ": *

#import "../components/header.typ": Header
#import "../components/footer.typ": Footer

#let EstrategiasPlanoDeAcao(..args) = {

  let dados = args.at(0)

  [

    #Header(
      titulo: [#text(weight: "extrabold")[Estratégias] de ação para a #linebreak()promoção da equidade racial],
      municipio: dados.municipio,
      uf: dados.uf,
      bgColor: rgb("265793"),
      textoDoSumario: "Estratégias"
    )

    #v(-.5cm)
    #hide[== Plano de ação]

    #grid(
      columns: (auto, 1fr),
      gutter: .5cm,
      box(
        fill: rgb("00000050"),
        radius: (top-left: 2cm),
        width: 2cm,
        height: 2cm,
        inset: (left: .82cm, top: 1.25cm)
      )[#text(fill: white, weight: "black", size: 64pt)[1]],
      box(
        inset: (top: .7cm)
      )[
        #set par(leading: 14pt)
        #text(size: 18pt, weight: "light", fill: black)[Plano de ação PNEERQ #linebreak() #text(weight: "extrabold")[Diagnóstico de Equidade]]
      ]
    )

    #v(-.25cm)

    #box(
      inset: (right: .22cm)
    )[
      #set text(fill: black, size: sizeBodySmall)

      #set par(spacing: 1.5em)

      #box(
        //fill: rgb("EAEAEA50"),
        inset: (top: .25cm, right: .25cm, bottom: 0cm, left: .25cm),
        radius: (top-left: 20pt, bottom-right: 20pt)
      )[

        #set par(leading: 1.15em, spacing: 18pt)

        #text(size: sizeBody)[
          Para que a organização da rede de ensino promova adequadamente a equidade, o #strong[planejamento deve ser orientado por dados de raça/cor e modalidades]:​
        ]

        #v(.05cm)

        #place(dx:.40cm, dy: 2.5cm)[
          #box(width: .5pt, height: 8cm, fill: rgb("666"))
        ]

        #align(left + horizon)[

          #place(dx:7.850cm, dy: 1.5cm)[
            #box(width: .5pt, height: 3.5cm, fill: rgb("666"))
          ]

          #place(dx:7.0cm, dy: 2.5cm)[
            #box(height: .5pt, width: .85cm, fill: rgb("666"))
          ]

          #grid(
            columns: (36%, 60%),
            gutter: 4%,

            align(left + horizon)[
              #grid(
              columns: (auto, 1fr),
              gutter: .25cm,
              row-gutter: 20pt,
              align(center + horizon)[
                #box(width: .8cm, height:.8cm, fill: pneerqLaranja, radius: 50%, inset: (top: .15cm))[
                  #text(size: 14pt,weight: "black", fill: white)[1]]
                ],
                text(size: 9pt)[
                  Aprimore continuamente seu monitoramento da situação de equidade racial na rede de ensino:
                ],
              )
            ],
            align(left + horizon)[
              #grid(
                columns: (auto, 1fr),
                gutter: .25cm,
                row-gutter: 14pt,
                align(center + horizon)[
                  #box(width: .7cm, height:.7cm, fill: pneerqLaranja, radius: 50%, inset: (top: .15cm))[
                    #text(size: 12pt,weight: "black", fill: white)[A]]
                  ],
                  text(size: 9pt)[
                    Identifique as diferenças de raça/cor, de pertencimento étnico e das modalidades de ensino nos seguintes indicadores: acesso à escola, permanência/rendimento, aprendizagem no SAEB, formação dos professores, infraestrutura escolar, conectividade, número de alunos por turma, acesso ao tempo integral e ao Atendimento Educacional Especializado.​
                  ],
                align(center + horizon)[
                  #box(width: .7cm, height:.7cm, fill: pneerqLaranja, radius: 50%, inset: (top: .15cm))[
                    #text(size: 12pt,weight: "black", fill: white)[B]]
                  ],
                  text(size: 9pt)[
                    Identifique as escolas com maioria dos estudantes pretos, pardos, quilombolas e indígenas.​
                  ],
                align(center + horizon)[
                  #box(width: .7cm, height:.7cm, fill: pneerqLaranja, radius: 50%, inset: (top: .15cm))[
                    #text(size: 12pt,weight: "black", fill: white)[C]]
                  ],
                  text(size: 9pt)[
                    Aprimore seu monitoramento de frequência escolar e sua avaliação diagnóstica/formativa/somativa para coletar os dados por raça/cor, incluindo a desagregação quilombola.
                  ],
                )
              ]
          )
        ]

        #v(-.9cm)

        ​#align(left + horizon)[
          #grid(
            columns: (auto, 1fr),
            gutter: .25cm,
            row-gutter: 14pt,
            align(center + horizon)[
              #box(width: .8cm, height:.8cm, fill: pneerqLaranja, radius: 50%, inset: (top: .15cm))[
                #text(size: 14pt,weight: "black", fill: white)[2]]
              ],
              text(size: 9pt)[
                Analise as respostas da sua rede ao #strong[#emph("Diagnóstico Equidade")].
              ],
            align(center + horizon)[
              #box(width: .8cm, height:.8cm, fill: pneerqLaranja, radius: 50%, inset: (top: .15cm))[
                #text(size: 14pt,weight: "black", fill: white)[3]]
              ],
              text(size: 9pt)[
                A partir dos achados da análise dos indicadores acima, organize #strong[um plano de ação de equidade racial da rede de ensino, com foco em melhorar as condições de ensino nas escolas com maioria de estudantes PPI e quilombolas]. Utilize as informações acima para identificar as potencialidades de melhoria.
              ],
            align(center + horizon)[
              #box(width: .8cm, height:.8cm, fill: pneerqLaranja, radius: 50%, inset: (top: .15cm))[
                #text(size: 14pt,weight: "black", fill: white)[4]]
              ],
              text(size: 9pt)[
                Neste plano de trabalho, considere também os territórios onde se faz necessário construir ou ampliar escolas regulares ou da modalidade quilombola, para garantir o atendimento escolar.
              ],
            align(center + horizon)[
              #box(width: .8cm, height:.8cm, fill: pneerqLaranja, radius: 50%, inset: (top: .15cm))[
                #text(size: 14pt,weight: "black", fill: white)[5]]
              ],
              text(size: 9pt)[
                Verifique nos instrumentos de planejamento de médio e longo prazo da Secretaria, como o Plano Municipal de Educação, as metas e estratégias ligadas à equidade racial e se estas estão ou podem ser contempladas no Planejamento de Ações para a Equidade.
              ],
          )
        ]
      ]
    ]

    #v(-.5cm)

    //
    #align(right + horizon)[
      #grid(
        columns: (16%, 70%),
        gutter: 8%,
        box()[
          #shadow(blur: 4pt, dx: 1pt, dy: 1pt,  fill: rgb(0, 0, 0, 25%), radius: (left: 4pt, top: 4pt, right: 4pt,bottom-right: 0pt))[
            #box(fill: txPreto, inset: (top:6pt, x: 4pt, bottom:4pt), radius: (left: 4pt, top: 4pt, right: 4pt,bottom-right: 0pt), width:3.7cm)[
              #text("Acesse o modelo de plano de ação de referência para equidade racial", fill: txBranco, weight: "bold", size: sizeBody * 0.7)
            ]
          ]
          #v(-.58cm)
          #shadow(blur: 4pt, dx: 1pt, dy: 1pt,  fill: rgb(0, 0, 0, 25%), radius: 4pt)[
            #box(
              fill: white,
              inset: .25cm,
              radius: (bottom: 4pt),
              width: 2.5cm
            )[#image("../assets/qrcodes/py/modelo-de-plano-de-acao-de-referencia-para-equidade-racial.svg", width: 100%)]
          ]
        ],
        box()[
          Acesse também os módulos de Diagnóstico e Planejamento do Novo PAR, ferramentas do Ministério da Educação, para planejar com equidade:​

          #v(-.25cm)

          #grid(
            columns: (auto, auto),
            gutter: .25cm,
            link("https://www.gov.br/mec/pt-br/novo-par/documentos/etapa-diagnstico.pdf")[

              #box(fill: rgb("265793"), radius:4pt, inset: (x:.5cm, top: .5cm, bottom: .4cm))[
                #text(fill: white, weight: "bold")[Diagnóstico do Novo PAR​]
              ]
              #v(-.75cm)
              #shadow(blur: 4pt, dx: 1pt, dy: 1pt,  fill: rgb(0, 0, 0, 25%), radius: 4pt)[
                #box(
                  fill: white,
                  inset: .125cm,
                  radius: 4pt,
                  width: 2cm
                )[#image("../assets/qrcodes/py/diagnostico-do-novo-par.svg", width: 100%)]
              ]
            ],

            link("https://novopar.mec.gov.br/")[
              #box(fill: rgb("0C8C59"), radius:4pt, inset: (x:.5cm, top: .5cm, bottom: .4cm))[
                #text(fill: white, weight: "bold")[Planejamento do Novo PAR​]
              ]
              #v(-.75cm)
              #shadow(blur: 4pt, dx: 1pt, dy: 1pt,  fill: rgb(0, 0, 0, 25%), radius: 4pt)[
                #box(
                  fill: white,
                  inset: .125cm,
                  radius: 4pt,
                  width: 2cm
                )[#image("../assets/qrcodes/py/novo-par.svg", width: 100%)]
              ]
            ],
          )
        ],
      )
    ]

    #v(-.25cm)

    // Como funciona o cálculo
    #box(inset:(right: 2.8cm))[
      #box(
        inset: (top: .5cm, right: .5cm, bottom: .75cm, left: .5cm),
        fill: rgb(pneerqLaranja),
        radius: (bottom: .5cm, right: .5cm),
        width: 100%,
      )[
        #align(center)[]
        #v(.25cm)
        #set text(fill: white, size: sizeBodySmall)
        #text(weight: weightTitle, size: sizeSubtitle)[Por que a autodeclaração racial é importante?]

        A autodeclaração racial é reconhecida como o “padrão-ouro” na coleta de dados raciais, por ser fundamental à construção da identidade e da pertença racial de todos os estudantes e por refletir a diversidade nos dados educacionais. Trata-se de informação essencial para o planejamento de políticas públicas e ações afirmativas, assegurando a distribuição justa de recursos, a correção de distorções históricas e a promoção da equidade no acesso, na permanência e na qualidade da educação básica.
      ]
    ]

    // QR Codes
    #place(right + bottom, dx:-.5cm, dy: -1cm)[

      #set par(justify: false, leading: 6pt)

      #shadow(blur: 4pt, dx: 1pt, dy: 1pt,  fill: rgb(0, 0, 0, 25%), radius: 4pt)[
        #box(
          fill: white,
          inset: .25cm,
          radius: (top: 4pt, left: 4pt),
          width: 2.5cm
        )[#image("../assets/qrcodes/py/materiais-de-declaracao-racial.svg", width: 100%)]
      ]
      #v(-.58cm)
      #shadow(blur: 4pt, dx: 1pt, dy: 1pt,  fill: rgb(0, 0, 0, 25%), radius: (top-left: 4pt, bottom-right: 4pt))[
        #box(fill: txPreto, inset: (top:6pt, x: 4pt, bottom:4pt), radius: (top-left: 4pt, bottom-right: 4pt), width:1.7cm)[
          #text("Saiba mais", fill: txBranco, weight: "bold", size: sizeBody * 0.7)
        ]
      ]
    ]
  ]
}