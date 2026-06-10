#import "../components/style.typ": *

#import "../components/header.typ": Header

#let EstrategiasAspectosPedagogicos03(..args) = {

  let dados = args.at(0)

  [

    #Header(
      titulo: [#text(weight: "extrabold")[Estratégias] de ação para a #linebreak()promoção da equidade racial],
      municipio: dados.municipio,
      uf: dados.uf,
      bgColor: rgb("265793"),
      esconderDoSumario: true
    )

    #grid(
      columns: (auto, 1fr),
      gutter: .5cm,
      box(
        fill: rgb("00000050"),
        radius: (top-left: 2cm),
        width: 2cm,
        height: 2cm,
        inset: (left: .82cm, top: 1.25cm)
      )[#text(fill: white, weight: "black", size: 64pt)[3]],
      box(
        inset: (top: .7cm)
      )[
        #set par(leading: 14pt)
        #text(size: 18pt, weight: "light", fill: black)[Aspectos #linebreak() #text(weight: "extrabold")[Pedagógicos]]
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
        #set par(leading: .7em)

        #move(dx: -1cm, dy: -.35cm)[
          #box(fill: rgb("265793"), inset: (top:.35cm, x:.25cm, bottom:.25cm), width: 45%, radius: (right:4pt, bottom-left:4pt))[
            #text(fill: white, weight: weightTitle, size: sizeBody)[=== Materiais didático-pedagógicos]
          ]
        ]

        #v(-.45cm)

        #set par(leading: 1.15em)
        É fundamental que a secretaria de educação garanta que os materiais didáticos usados nas escolas sejam #strong[revisados e selecionados de forma crítica e propositiva]. Isso significa: #strong[orientar as escolas] para que escolham livros que não utilizem pessoas PPI em situações de inferioridade, seja por meio de imagens e no texto;  incluam de fato a história e a cultura afro-brasileira, africana e indígena; #strong[adquirir recursos diversos] (como filmes, jogos e bonecas com diferentes representações étnico-raciais) que promovam o respeito à diversidade; e #strong[investir em obras literárias] infantis e infanto-juvenis que abordem essas temáticas, conforme as diretrizes educacionais de ERER e implementação da Educação Escolar Quilombola - EQQ. Essa revisão ativa dos materiais é um passo concreto para uma educação antirracista, que combate estereótipos e valoriza a pluralidade que forma o Brasil.
      ]

      #v(-.5cm)

      #box(
        fill: rgb("EAEAEA50"),
        inset: (top: .75cm, right: .75cm, bottom: .6cm, left: .75cm),
        radius: (top-right: 20pt, bottom-left: 20pt)
      )[
        #set par(leading: .7em)

        #move(dx: -1cm, dy: -.35cm)[
          #box(fill: rgb("265793"), inset: (top:.35cm, x:.25cm, bottom:.25cm), width: 99%, radius: (right:4pt, bottom-left:4pt))[
            #text(fill: white, weight: weightTitle, size: sizeBody)[=== Uso do PDDE para avançar em estratégias pedagógicas de equidade racial]
          ]
        ]

        #v(-.45cm)

        #set par(leading: 1.15em, spacing: 16pt)
        As escolas da sua rede podem usar o PDDE para a aquisição de materiais didáticos e de apoio pedagógico de ERER e EQQ, formação dos profissionais da educação em estratégias pedagógicas de equidade racial, oficinas de letramento racial, de autoidentificação racial, autodeclaração quilombola, bem como na organização de visitas pedagógicas, feiras e mostras culturais relacionadas ao tema.​

        Há os recursos do PDDE Equidade ERER/EEQ (R\$ 114 milhões entre 2025 e 2026), mas os recursos do PDDE Básico também podem ser utilizados com foco em equidade.​

        Apoie e incentive suas escolas no planejamento do uso dos recursos do PDDE Básico e do PDDE Equidade, cuidando de respeitar a autonomia escolar na escolha final.​

        As escolas quilombolas também podem ser contempladas no Programa PDDE Água e Campo.
        ​
      ]

      #v(-.5cm)

      #box(
        fill: bgTabela,
        inset: (top: .75cm, right: .75cm, bottom: .6cm, left: .75cm),
        radius: (top-left: 20pt, bottom-right: 20pt)
      )[
        #set par(leading: .7em)

        #move(dx: -1cm, dy: -.35cm)[
          #box(fill: rgb("265793"), inset: (top:.35cm, x:.25cm, bottom:.25cm), width: 55%, radius: (right:4pt, bottom-left:4pt))[
            #text(fill: white, weight: weightTitle, size: sizeBody)[=== Selo Petronilha Beatriz Gonçalves e Silva]
          ]
        ]

        #v(-.45cm)

        #set par(leading: 1.15em, spacing: 16pt)
        Essa iniciativa do MEC reconhece secretarias de educação comprometidas com a #strong[equidade racial e quilombola], para fortalecer políticas públicas que transformem realidades por meio de uma educação antirracista e equitativa​.

        Em sua primeira edição (2025), o Selo foi concedido a #strong[436 secretarias] (428 municipais e 8 estaduais). Dessas, 20 receberam destaque nacional por suas práticas inspiradoras, documentadas em um catálogo da SECADI para incentivar outras redes.​

        As iniciativas premiadas descritas na cartilha incluem ações como: #strong[formação continuada] de professores e #strong[revisão curricular] alinhada à lei e à BNCC; #strong[ações de planejamento] baseadas em dados e indicadores; #strong[apoio financeiro e pedagógico] às escolas; projetos que #strong[valorizam a cultura afro-brasileira e quilombola] por meio de metodologias ativas; #strong[modernização da infraestrutura] e produção de #strong[materiais pedagógicos inclusivos; foco na educação infantil antirracista], saberes ancestrais e no estímulo à #strong[autodeclaração e declaração étnico-racial].
                ​
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
        )[#image("../assets/qrcodes/py/pagina-da-pneerq-no-mec-red.svg", width: 100%)]
      ]

      #v(-.58cm)

      #shadow(blur: 4pt, dx: 1pt, dy: 1pt,  fill: rgb(0, 0, 0, 25%), radius: (top-left: 4pt, bottom-right: 4pt))[
        #box(fill: txPreto, inset: (top:6pt, x: 4pt, bottom:4pt), radius: (top-left: 4pt, bottom-right: 4pt), width:3.1cm)[
          #text("Conheça materiais produzidos por instituições parceiras da PNEERQ", fill: txBranco, weight: "bold", size: sizeBody * 0.7)
        ]
      ]

      #v(2cm)

      #shadow(blur: 4pt, dx: 1pt, dy: 1pt,  fill: rgb(0, 0, 0, 25%), radius: (top-left: 4pt, bottom-left: 4pt, top-right: 4pt))[
        #box(fill: txPreto, inset: (top:6pt, x: 4pt, bottom:4pt), radius: (top-left: 4pt, bottom-left: 4pt, top-right: 4pt), width:2.6cm)[
          #text("Conheça as dicas de uso do PDDE", fill: txBranco, weight: "bold", size: sizeBody * 0.7)
        ]
      ]
      #v(-.58cm)
      #shadow(blur: 4pt, dx: 1pt, dy: 1pt,  fill: rgb(0, 0, 0, 25%), radius: (top-left: 4pt))[
        #box(
          fill: white,
          inset: .25cm,
          radius: (top-left: 4pt),
          width: 2.5cm
        )[#image("../assets/qrcodes/py/guia-de-uso-dos-recursos-do-pdde.svg", width: 100%)]
      ]
      #v(-.58cm)
      #shadow(blur: 4pt, dx: 1pt, dy: 1pt,  fill: rgb(0, 0, 0, 25%), radius: (bottom: 4pt))[
        #box(
          fill: white,
          inset: .25cm,
          radius: (bottom: 4pt),
          width: 2.5cm
        )[#image("../assets/qrcodes/py/live-sobre-uso-dos-recursos-do-pdde.svg", width: 100%)]
      ]

      #v(.45cm)

      #shadow(blur: 4pt, dx: 1pt, dy: 1pt,  fill: rgb(0, 0, 0, 25%), radius: 4pt)[
        #box(
          fill: white,
          inset: .25cm,
          radius: (top: 4pt),
          width: 2.5cm
        )[#image("../assets/qrcodes/py/cartilha-do-selo-petronilha.svg", width: 100%)]
      ]
      #v(-.58cm)
      #shadow(blur: 4pt, dx: 1pt, dy: 1pt,  fill: rgb(0, 0, 0, 25%), radius: (top-left: 4pt, bottom-right: 4pt))[
        #box(fill: txPreto, inset: (top:6pt, x: 4pt, bottom:4pt), radius: (top-left: 4pt, bottom-right: 4pt), width:3.2cm)[
          #text("Acesse o material que resume as ações premiadas no Selo Petronilha", fill: txBranco, weight: "bold", size: sizeBody * 0.7)
        ]
      ]

    ]
  ]
}