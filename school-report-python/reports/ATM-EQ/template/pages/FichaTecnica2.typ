#import "../components/style.typ": *

#let FichaTecnica() = [

  #set page(
    margin: (top: .5cm, right: 0cm, bottom: 1.8cm, left: 0cm),
    footer: [
      #align(center + bottom)[
        #image("../assets/backgrounds/footer.svg", width: 100%)
      ]
    ],
  )

  #set text(
    font: "Rawline",
    size: 9pt,
    hyphenate: false
  )

  #let spacing = .25cm

  #set par(
    spacing: 1em,
    leading: .8em,
    justify: false
  )

  #v(spacing * 2)

  #align(center)[

    // Governo Federal
    #text(weight: weightSubtitle)[REPÚBLICA FEDERATIVA DO BRASIL]

    #v(spacing)

    Luiz Inácio Lula da Silva

    #text(weight: weightTitle)[Presidente da República Federativa do Brasil]
    #v(spacing)

    Leonardo Osvaldo Barchini Rosa

    #text(weight: weightTitle)[Ministro de Estado da Educação]
    #v(spacing)

    Evânio Antônio de Araújo Júnior

    #text(weight: weightTitle)[Secretário de Gestão da Informação, Inovação e Avaliação de Políticas Educacionais]

    #v(spacing)

    Zara Figueiredo

    #text(weight: weightTitle)[Secretária de Educação Continuada, Alfabetização de Jovens e Adultos, Diversidade e Inclusão]

    #v(spacing * 2)

    #box(inset: (x: 1cm))[

      #box(fill:bgTabela, inset: (top: .7cm, bottom: .5cm, x: .5cm), radius: 8pt)[

        // Ficha Técnica
        #text(weight: weightSubtitle)[FICHA TÉCNICA]

        #v(spacing * 2)

        #grid(
          columns: (1fr, 1fr),
          gutter: 5%,
          align(left)[

            //#text(weight: weightTitle)[COORDENAÇÃO E PRODUÇÃO DE CONTEÚDO TÉCNICO]

            Camila Porto Fasolo

            #text(weight: weightTitle)[Diretora de Monitoramento e Avaliação de Políticas Educacionais]
            #v(spacing)

            Lucas Evencio Soares Dutra

            #text(weight: weightTitle)[Coordenador-Geral de Informação Estratégica em Educação]

            #v(spacing)
            Caio Callegari

            #text(weight: weightTitle)[Coordenador-Geral de Equidade Educacional]
            #v(spacing)

            Clelia Mara dos Santos

            #text(weight: weightTitle)[Diretora de Políticas de Educação Étnico-Racial #linebreak()e Educação Escolar Quilombola]
            #v(spacing)

            Eduardo Araújo

            #text(weight: weightTitle)[Coordenador-Geral de Educação Escolar Quilombola]
            #v(spacing)

            Lara Vilela

            #text(weight: weightTitle)[Coordenadora-Geral de Educação para Relações Étnico-Raciais]
            #v(spacing)

            Francisco Moraes da Costa Marques

            #text(weight: weightTitle)[Coordenador-Geral de Avaliação, Monitoramento#linebreak()e Fortalecimento de Políticas de Diversidade]
            #v(spacing)

            

          ],
          align(left)[

            #text(weight: weightTitle)[GERENTE DE PROJETO]

            Luiz Rogério Lopes
            #v(spacing * 1.75)
            

            #text(weight: weightTitle)[#upper[Redação e Revisão]]

            Ana Cláudia Richardelli Moreira de Castro Soares

            Emília Lucy Nogueira Marinho

            #v(spacing * 1.75)

            #text(weight: weightTitle)[GESTÃO E ENGENHARIA DE DADOS]

            Anderson Gregorio Marques Soares

            Eduardo Chagas Lustoza

            #v(spacing * 1.75)

            #text(weight: weightTitle)[PROJETO GRÁFICO]

            André José Ribeiro Guimarães
            
            #v(spacing * 1.75)

            #text(weight: weightTitle)[#upper[Apoio Técnico]]

            Daniel Duque

            Emília Lucy Nogueira Marinho

            Lauana Simplício Pereira

            Lucas Fernandes Hoogerbrugge

            Michael França

            Thais Barcellos

            Thales Machado
          ]
        )
      ]
    ]

    #v(spacing * 3)

    Brasília (DF), Abril de 2026

    #v(spacing + 6pt)

    #image("../assets/logos/MarcaMec.svg", height: 1.2cm)

    #place(center + bottom)[
      #box(inset:(x:1cm))[

        #text(weight: weightSubtitle)[#upper[Saiba mais sobre dados e indicadores da Educação no Brasil.]]

        #v(-.25cm)

        #grid(
          columns: (1fr, 1fr),
          gutter: .8cm,
          box(radius: 8pt, clip: true)[
            #image("../assets/backgrounds/diagnostico-pneerq.svg", height: 4.5cm)
          ],
          box(radius: 8pt, clip: true)[
            #image("../assets/backgrounds/educadados.svg", height: 4.5cm)
          ]
        )
      ]
    ]
  ]
]
