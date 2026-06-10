#import "../components/style.typ": *

#import "../components/header.typ": Header
#import "../components/footer.typ": Footer

#let EstrategiasAspectosRelacionais(..args) = {

  let dados = args.at(0)

  [

    #Header(
      titulo: [#text(weight: "extrabold")[Estratégias] de ação para a #linebreak()promoção da equidade racial],
      municipio: dados.municipio,
      uf: dados.uf,
      bgColor: rgb("265793"),
      textoDoSumario: "Estratégias: Aspectos relacionais e de articulação institucional",
      esconderDoSumario: true
    )
    
    #v(-.5cm)
    #hide[== Aspectos relacionais e de articulação institucional]

    #grid(
      columns: (auto, 1fr),
      gutter: .5cm,
      box(
        fill: rgb("00000050"),
        radius: (top-left: 2cm),
        width: 2cm,
        height: 2cm,
        inset: (left: .75cm, top: 1.25cm)
      )[#text(fill: white, weight: "black", size: 64pt)[2]],
      box(
        inset: (top: .7cm)
      )[
        #set par(leading: 14pt)
        #text(size: 18pt, weight: "light", fill: black)[Aspectos #text(weight: "extrabold")[relacionais] e #linebreak() de #text(weight: "extrabold")[articulação institucional]]
      ]
    )

    #box(
      inset: (right: 3.5cm)
    )[
      #set text(fill: black, size: sizeBodySmall)

      #set par(spacing: 1.5em)

      #box(
        fill: bgTabela,
        inset: (top: .75cm, right: .75cm, bottom: .5cm, left: .75cm),
        radius: (top-left: 20pt, bottom-right: 20pt)
      )[
        #set par(leading: .75em)

        #move(dx: -1cm, dy: -.35cm)[
          #box(fill: rgb("265793"), inset: (top:.35cm, x:.25cm, bottom:.25cm), width: 108%, radius: (right:4pt, bottom-left:4pt))[
            #text(fill: white, weight: weightTitle, size: sizeBody)[Implementação de protocolos de Identificação, Prevenção e Resposta ao Racismo]
          ]
        ]

        #v(-.35cm)

        #set par(leading: 1em)
        O protocolo é instrumento objetivo e estruturado de procedimentos que servem para orientar toda a comunidade escolar (gestores, professores, profissionais, estudantes, pais, mães, famílias e responsáveis) nos casos de racismo intraescolar e na promoção de ações educativas de prevenção ao racismo.
      ]

      #v(-.6cm)

      #box(
        fill: rgb("EAEAEA50"),
        inset: (top: .75cm, right: .75cm, bottom: .75cm, left: .75cm),
        radius: (top-right: 20pt, bottom-left: 20pt)
      )[
        #set par(leading: .75em)

        #move(dx: -1cm, dy: -.35cm)[
          #box(fill: rgb("265793"), inset: (top:.35cm, x:.25cm, bottom:.25cm), width: 49%, radius: (right:4pt, bottom-left:4pt))[
            #text(fill: white, weight: weightTitle, size: sizeBody)[Agentes de governança da PNEERQ]
          ]
        ]

        #v(-.35cm)

        #set par(leading: 1em)
        Os Agentes de Governança Regionais apoiam as secretarias estaduais e municipais na articulação das diretrizes da PNEERQ e no acompanhamento das metas estabelecidas. Já os Agentes de Formação Local atuarão na formação de professores das redes que não cumpriram com a Condicionalidade III, e atuam em conjunto com as redes de ensino selecionadas para a ação focalizada, identificando desafios específicos e propondo soluções alinhadas às necessidades locais.

        Ao todo, são 1.533 Agentes de Governança com a finalidade de apoiar a implementação e monitoramento da PNEERQ nas redes de ensino em todo o país.
      ]

      #v(-.6cm)

      #box(
        fill: bgTabela,
        inset: (top: .75cm, right: .75cm, bottom: .65cm, left: .75cm),
        radius: (top-left: 20pt, bottom-right: 20pt)
      )[
        #set par(leading: .75em)

        #move(dx: -1cm, dy: -.35cm)[
          #box(fill: rgb("265793"), inset: (top:.35cm, x:.25cm, bottom:.25cm), width: 48.5%, radius: (right:4pt, bottom-left:4pt))[
            #text(fill: white, weight: weightTitle, size: sizeBody)[Avaliação participativa das escolas]
          ]
        ]

        #v(-.35cm)

        #set par(leading: 1em)
        O MEC é parceiro no desenvolvimento dos Indicadores da Qualidade na Educação: Relações Raciais na Escola – Antirracismo em Movimento. Revisada em 2023, a publicação é voltada às escolas que desejam fazer uma autoavaliação sobre o enfrentamento do racismo nas instituições educativas. Trata-se de um instrumento por meio da qual a comunidade escolar avalia de forma participativa a situação de diferentes aspectos de sua escola, identifica prioridades, estabelece planos de ações, implementa e monitora seus resultados. Este instrumento deve ser utilizado em conjunto com o Diagnóstico Equidade, disponível no site da PNEERQ e descrito nas páginas anteriores, para uma avaliação abrangente e estruturada.
      ]

      #v(-.6cm)

      #box(
        fill: rgb("EAEAEA50"),
        inset: (top: .75cm, right: .75cm, bottom: .65cm, left: .75cm),
        radius: (top-right: 20pt, bottom-left: 20pt)
      )[
        #set par(leading: .75em)

        #move(dx: -1cm, dy: -.35cm)[
          #box(fill: rgb("265793"), inset: (top:.35cm, x:.25cm, bottom:.25cm), width: 28%, radius: (right:4pt, bottom-left:4pt))[
            #text(fill: white, weight: weightTitle, size: sizeBody)[Participação social]
          ]
        ]

        #v(-.35cm)

        #set par(leading: 1em)
        A existência de canais de monitoramento e controle social das políticas públicas, programas e ações para construção de um município antirracista com escolas antirracistas é vital para a equidade racial na escola e fora dela.

        O seu município, caso ainda não tenha, pode fomentar a institucionalização de Câmara de Participação e Controle Social da PNEERQ, das ações locais antirracistas e da inclusão das representações negras e quilombolas em conselhos, comissões e grupos de trabalho da educação.
      ]

      #v(-.6cm)

      #box(
        fill: bgTabela,
        inset: (top: .75cm, right: .75cm, bottom: .5cm, left: .75cm),
        radius: (top-left: 20pt, bottom-right: 20pt),
        width: 100%
      )[
        #set par(leading: .75em)

        #move(dx: -1cm, dy: -.35cm)[
          #box(fill: rgb("265793"), inset: (top:.35cm, x:.25cm, bottom:.25cm), width: 32%, radius: (right:4pt, bottom-left:4pt))[
            #text(fill: white, weight: weightTitle, size: sizeBody)[Estrutura institucional]
          ]
        ]

        #v(-.35cm)

        #set par(leading: 1em)
        É importante estruturar uma equipe responsável pela gestão das políticas de equidade racial, incluindo as políticas de educação escolar quilombola quando há oferta da modalidade de ensino. Essa ação dá perenidade às ações desenvolvidas pela rede.
      ]
    ]

    // QR Codes
    #place(right + top, dx:-.5cm, dy: 5.65cm)[

      #set par(justify: false, leading: 6pt)

      #shadow(blur: 4pt, dx: 1pt, dy: 1pt,  fill: rgb(0, 0, 0, 25%), radius: 4pt)[
        #box(
          fill: white,
          inset: .25cm,
          radius: (top: 4pt),
          width: 2.5cm
        )[#image("../assets/qrcodes/py/protocolos-de-resposta-ao-racismo.svg", width: 100%)]
      ]

      #v(-.58cm)

      #shadow(blur: 4pt, dx: 1pt, dy: 1pt,  fill: rgb(0, 0, 0, 25%), radius: (top-left: 4pt, bottom-right: 4pt))[
        #box(fill: txPreto, inset: (top:6pt, x: 4pt, bottom:4pt), radius: (top-left: 4pt, bottom-right: 4pt), width:2.4cm)[
          #text("Acesse a página de protocolos", fill: txBranco, weight: "bold", size: sizeBody * 0.7)
        ]
      ]

      #v(0cm)

      #shadow(blur: 4pt, dx: 1pt, dy: 1pt,  fill: rgb(0, 0, 0, 25%), radius: 4pt)[
        #box(
          fill: white,
          inset: .25cm,
          radius: (top: 4pt),
          width: 2.5cm
        )[#image("../assets/qrcodes/py/agentes-de-governanca-pneerq.svg", width: 100%)]
      ]
      #v(-.58cm)
      #shadow(blur: 4pt, dx: 1pt, dy: 1pt,  fill: rgb(0, 0, 0, 25%), radius: (top-left: 4pt, bottom-right: 4pt))[
        #box(fill: txPreto, inset: (top:6pt, x: 4pt, bottom:4pt), radius: (top-left: 4pt, bottom-right: 4pt), width:3cm)[
          #text("Conheça os agentes que podem apoiar sua rede", fill: txBranco, weight: "bold", size: sizeBody * 0.7)
        ]
      ]

      #v(-.25cm)

      #shadow(blur: 4pt, dx: 1pt, dy: 1pt,  fill: rgb(0, 0, 0, 25%), radius: 4pt)[
        #box(
          fill: white,
          inset: .25cm,
          radius: (top: 4pt),
          width: 2.5cm
        )[#image("../assets/qrcodes/py/atribuicoes-dos-agentes-de-governanca.svg", width: 100%)]
      ]
      #v(-.58cm)
      #shadow(blur: 4pt, dx: 1pt, dy: 1pt,  fill: rgb(0, 0, 0, 25%), radius: (top-left: 4pt, bottom-right: 4pt))[
        #box(fill: txPreto, inset: (top:6pt, x: 4pt, bottom:4pt), radius: (top-left: 4pt, bottom-right: 4pt), width:1.9cm)[
          #text("Atribuições dos agentes", fill: txBranco, weight: "bold", size: sizeBody * 0.7)
        ]
      ]

      #v(1.90cm)

      #shadow(blur: 4pt, dx: 1pt, dy: 1pt,  fill: rgb(0, 0, 0, 25%), radius: 4pt)[
        #box(
          fill: white,
          inset: .25cm,
          radius: (top: 4pt),
          width: 2.5cm
        )[#image("../assets/qrcodes/py/material-do-indiques-rre.svg", width: 100%)]
      ]
      #v(-.58cm)
      #shadow(blur: 4pt, dx: 1pt, dy: 1pt,  fill: rgb(0, 0, 0, 25%), radius: (top-left: 4pt, bottom-right: 4pt))[
        #box(fill: txPreto, inset: (top:6pt, x: 4pt, bottom:4pt), radius: (top-left: 4pt, bottom-right: 4pt), width:2.6cm)[
          #text("Acesse o material do Indiques", fill: txBranco, weight: "bold", size: sizeBody * 0.7)
        ]
      ]

      #v(.25cm)

      #shadow(blur: 4pt, dx: 1pt, dy: 1pt,  fill: rgb(0, 0, 0, 25%), radius: 4pt)[
        #box(
          fill: white,
          inset: .25cm,
          radius: (top: 4pt),
          width: 2.5cm
        )[#image("../assets/qrcodes/py/desenho-das-comissoes-locais.svg", width: 100%)]
      ]
      #v(-.58cm)
      #shadow(blur: 4pt, dx: 1pt, dy: 1pt,  fill: rgb(0, 0, 0, 25%), radius: (top-left: 4pt, bottom-right: 4pt))[
        #box(fill: txPreto, inset: (top:6pt, x: 4pt, bottom:4pt), radius: (top-left: 4pt, bottom-right: 4pt), width:2.9cm)[
          #text("Conheça o desenho das Comissões​", fill: txBranco, weight: "bold", size: sizeBody * 0.7)
        ]
      ]
    ]
  ]
}