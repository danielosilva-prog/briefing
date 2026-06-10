#import "../components/style.typ": *

#let Introducao(..args) = {
  let dados = args.at(0, default: (:))
  [

    #set page(
      margin: (top: 0pt, right: 0pt, bottom: 1.25cm, left: 0pt),
      background: [
        #image("../assets/backgrounds/introducao.svg", width: 100%)
      ],
      fill: rgb(pneerqLaranja),
      footer: [],
    )
    #set text(
      font: "Rawline",
      size: sizeBody,
    )
    #set par(
      leading: 1em,
      spacing: 1.5em,
      justify: true,
    )

    #box(
      inset: (top: 1.5cm, right: 3.5cm, bottom: 1cm, left: 2.5cm),
    )[

      #hide[= Introdução]

      #v(-.5cm)

      #text(weight: "light", size: sizeTitlePage*1.15, fill: rgb(txBranco))[#text(weight: "extrabold")[Introdução]]

      #v(-.55cm)

      #set text(fill: white, size: sizeBodySmall)

      #set par(justify: false)

      #text(weight: weightTitle, size: sizeSubtitle)[
        Como o meu município está avançando na equidade racial#linebreak()na aprendizagem, de modo a estar habilitado à complementação VAAR/FUNDEB?
      ]

      #set par(justify: true)

      #par[
        Buscando apoiar na resposta a essa pergunta, o Ministério da Educação lança a 'Edição Especial Equidade Racial', utilizando a tecnologia do Aqui Tem MEC, com relatórios individualizados para cada município brasileiro. Neste material, trazemos os dados específicos de sua rede municipal no que tange à situação educacional dos estudantes negros, demonstramos como essa situação se relaciona ao recebimento da Complementação da União VAAR/FUNDEB e sugerimos algumas estratégias para que a rede municipal melhore seus indicadores de equidade racial.
      ]

      #par[
        2026 é o quarto ano de vigência desta Complementação, conforme Lei Federal nº 14.113/2020. O que se observa é que a condicionalidade III (redução das desigualdades socioeconômicas e raciais) continua sendo o maior desafio para Prefeituras e Governos Estaduais estarem plenamente habilitados ao recebimento dos recursos.
      ]

      #par[
        A condicionalidade III diz respeito a resultados de equidade, que são derivados do conjunto de ações institucionais, administrativo-financeiras e pedagógicas da gestão das redes de ensino. A compreensão do que é possível ser feito para o cumprimento da condicionalidade, portanto, exige a consideração de uma gama mais complexa de fatores, que influenciam o resultado das redes.
      ]

      #par[
        Uma Política de Estado é um instrumento fundamental para a consolidação de uma educação de equidade com foco na superação das desigualdades étnico-raciais na educação brasileira e que incida decisivamente nas escolas, nas aprendizagens e trajetórias escolares dos estudantes da educação básica.
      ]

      #par[
        Este documento tem como objetivo apresentar os principais dados de desigualdades e orientar estratégias práticas para apoiar as redes de ensino no avanço da equidade. A iniciativa se insere nas estratégias da Política Nacional de Equidade, Educação para as Relações Étnico-Raciais e Educação Escolar Quilombola (PNEERQ), instituída pela Portaria MEC nº 470/2024, e fortalece um de seus pilares centrais: o regime de colaboração. Cumpre, assim, a função de apoio técnico da União aos entes federativos, em especial aos Municípios, na promoção de uma educação mais justa e equitativa.
      ]
    ]

    #v(-.7cm)

    #move(dx: 2.5cm)[
      #box(
        inset: (top: 1cm, right: .5cm, bottom: .5cm, left: .5cm),
        fill: rgb(txBranco),
        width: 15cm,
        radius: (left:8pt, top-right:40pt, bottom-right: 8pt)
      )[

        #text(weight: "extrabold", size: sizeTitle, fill: pneerqVermelho)[
          Como funciona a Complementação VAAR/FUNDEB?
        ]

        #v(-.25cm)

        #box(width: 1.6cm, height: .2cm, fill: pneerqLaranja)[]

        #v(-.1cm)

        #set text(fill: txCinza, size: sizeBodySmall)

        #set par(justify: false)

        #text(
          weight: weightTitle,
          size: sizeBody,
        )[Para receber recursos dessa transferência constitucional federal, as redes de ensino:]

        #align(left + horizon)[
          #grid(
            columns: (auto, 1fr),
            gutter: .25cm,

            image("../assets/icons/checklist.svg", width: 1.2cm),
            [Devem cumprir anualmente as 5 condicionalidades de melhoria da gestão educacional, definidas por Lei (_veja na próxima página_);],

            image("../assets/icons/money.svg", width: 1.2cm),
            [Recebem o recurso de acordo com o desempenho em indicadores de atendimento (Censo Escolar) e de aprendizagem com equidade (Prova Brasil/Saeb).],
          )
        ]

        #v(-.25cm)


        // Gráfico
        #box(
          width: 100%,
          inset: (top: .3cm, right: 0.0cm, bottom: .15cm, left: 0cm),
        )[
          #align(center)[
            #text(
              size: sizeChartTitle,
              fill: txCinza,
              weight: weightTitleChart,
            )[Crescimento da complementação VAAR/FUNDEB para Estados e Municípios,#linebreak()2023 a 2026 – R\$ bilhões nominais – última Portaria Interministerial de cada ano]

            #if "chartCrescimentoVaarFundeb" in dados and dados.chartCrescimentoVaarFundeb != none {
              image("../" + dados.chartCrescimentoVaarFundeb, height: 3.25cm)
            }
          ]
        ]
        #v(-.25cm)

        #align(center)[#text(size: sizeCaption, fill: txCinza)[#strong[Fonte:] MEC/FNDE (2023-2026)]]
      ]
    ]

    // QR Codes
    #place(right + bottom, dx:-.5cm, dy: -0.35cm)[

      #set par(justify: false, leading: 6pt)

      #shadow(blur: 4pt, dx: 1pt, dy: 1pt,  fill: rgb(0, 0, 0, 25%), radius: 4pt)[
        #box(
          fill: white,
          inset: .25cm,
          radius: (top: 4pt),
          width: 2.5cm
        )[#image("../assets/qrcodes/py/conheca-mais-sobre-a-complementacao-vaar.svg", width: 100%)]
      ]
      #v(-.58cm)
      #shadow(blur: 4pt, dx: 1pt, dy: 1pt,  fill: rgb(0, 0, 0, 25%), radius: (top-left: 4pt, bottom-right: 4pt))[
        #box(fill: txPreto, inset: (top:6pt, x: 4pt, bottom:4pt), radius: (top-left: 4pt, bottom-right: 4pt), width:3.5cm)[
          #text("Conheça mais sobre a Complementação VAAR", fill: txBranco, weight: "bold", size: sizeBody * 0.7)
        ]
      ]

      #shadow(blur: 4pt, dx: 1pt, dy: 1pt,  fill: rgb(0, 0, 0, 25%), radius: 4pt)[
        #box(
          fill: white,
          inset: .25cm,
          radius: (top: 4pt),
          width: 2.5cm
        )[#image("../assets/qrcodes/py/conheca-a-pneerq.svg", width: 100%)]
      ]
      #v(-.58cm)
      #shadow(blur: 4pt, dx: 1pt, dy: 1pt,  fill: rgb(0, 0, 0, 25%), radius: (top-left: 4pt, bottom-right: 4pt))[
        #box(fill: txPreto, inset: (top:6pt, x: 4pt, bottom:4pt), radius: (top-left: 4pt, bottom-right: 4pt), width:2.9cm)[
          #text("Conheça a PNEERQ", fill: txBranco, weight: "bold", size: sizeBody * 0.7)
        ]
      ]
    ]
  ]
}
