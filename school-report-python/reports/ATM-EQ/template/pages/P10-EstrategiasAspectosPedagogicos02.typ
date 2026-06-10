#import "../components/style.typ": *

#import "../components/header.typ": Header

#let EstrategiasAspectosPedagogicos02(..args) = {
  
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
        inset: (top: .7cm, right: .75cm, bottom: .45cm, left: .75cm),
        radius: (top-left: 20pt, bottom-right: 20pt)
      )[
        #set par(leading: .7em)

        #move(dx: -1cm, dy: -.35cm)[
          #box(fill: rgb("265793"), inset: (top:.35cm, x:.25cm, bottom:.25cm), width: 33%, radius: (right:4pt, bottom-left:4pt))[
            #text(fill: white, weight: weightTitle, size: sizeBody)[Formações ERER e EEQ]
          ]
        ]

        #v(-.35cm)

        #set text(hyphenate: false)
        #set par(leading: 1em)
        Como parte central da Política Nacional de Equidade (PNEERQ), o MEC oferece formações continuadas para gestores e professores sobre relações étnico-raciais e educação escolar quilombola. Essa capacitação é feita em parceria com universidades e institutos, tanto presencialmente quanto a distância. Um exemplo é a oferta de vagas ilimitadas em cursos sobre o tema na plataforma AVAMEC, além de outras formações planejadas para 2026. Entre 2023 e 2025, mais de 262 mil vagas já foram oferecidas.
        
        Além das formações promovidas pelo MEC, é essencial que a secretaria promova formações contínuas e abrangentes sobre equidade racial e ERER para todos os profissionais da rede, além de EEQ, nas Redes com Escolas Quilombolas. Isso inclui cursos de, no mínimo, 30 horas para professores e para diretores/coordenadores pedagógicos, além de formações específicas para técnicos responsáveis pelo censo escolar. Adicionalmente, é essencial oferecer atividades formativas de curta duração (como palestras e oficinas) ao longo do ano, mantendo uma programação regular e mensal para garantir a atualização constante de toda a equipe. Abaixo, sugestões essenciais para as ações formativas das redes.
      ]

      #v(-.5cm)

      #box(
        fill: rgb("EAEAEA50"),
        inset: (top: .75cm, right: .75cm, bottom: .2cm, left: .75cm),
        radius: (top-right: 20pt, bottom-left: 20pt)
      )[
        #set par(leading: .7em)

        #move(dx: -1cm, dy: -.35cm)[
          #box(fill: rgb("265793"), inset: (top:.35cm, x:.25cm, bottom:.25cm), width: 99%, radius: (right:4pt, bottom-left:4pt))[
            #text(fill: white, weight: weightTitle, size: sizeBody)[Sugestões de eixos para ações de formação continuada nas redes de ensino para professores, gestores e outros profissionais da educação, incluindo:]
          ]
        ]

        #v(-.35cm)

        #set par(leading: 1em)
        Para a prática docente:​

        - #strong[Metodologias para a equidade e estratégias de ensino:] ampliar as referências dos docentes sobre critérios e formas de ensinar que potencializem processos de aprendizagens;​
        - #strong[Metodologias para a equidade:] desenvolvimento de práticas pedagógicas que valorizem identidades diversas e combatam vieses inconscientes, incluindo cuidado e atenção com discentes e nas inferências sobre as possibilidades de aprendizagem e sucesso escolar de alunos PPI e quilombolas;​
        - #strong[Gestão de sala de aula antirracista:] estratégias para uma boa gestão de sala, que ao tempo em que favoreça organização didática incidam na criação de ambientes inclusivos, com valorização da diversidade étnico-racial e que favoreçam fruição do ensino e da aprendizagem.
        
        #v(.1cm)

        Para a gestão escolar:​

        - #strong[Protocolos contra o racismo:] adoção e implementação de normativas institucionais para a prevenção, mediação e enfrentamento do racismo na escola;​
        - #strong[PPPs com metas de equidade:] estabelecer metas e estratégias de redução das desigualdades raciais; ​
        - #strong[Priorização de matrículas:] priorizar as matrículas de crianças PPI e quilombolas na educação infantil e nas escolas em tempo integral; ​
        - #strong[Uso de dados raciais:] preparação para a coleta, leitura e utilização de dados raça/cor + quilombola no planejamento de ações e políticas escolares;​
        - #strong[Desenvolvimento e aprendizagem:] estabelecer com docentes e coordenação pedagógica mecanismos perenes de acompanhamento pedagógico com base na desagregação raça/cor;​
        - #strong[Composição diversas de salas regulares], sem estabelecimento de "turmas fortes" e "turmas fracas";​
        - #strong[Formação em Educação Escolar Quilombola:] aplicação prática das Diretrizes Nacionais Curriculares de Educação Escolar Quilombola na Educação Básica (CNE, Resolução n°08/2012).​
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
        )[#image("../assets/qrcodes/py/painel-mais-professores.svg", width: 100%)]
      ]

      #v(-.58cm)

      #shadow(blur: 4pt, dx: 1pt, dy: 1pt,  fill: rgb(0, 0, 0, 25%), radius: (top-left: 4pt, bottom-right: 4pt))[
        #box(fill: txPreto, inset: (top:6pt, x: 4pt, bottom:4pt), radius: (top-left: 4pt, bottom-right: 4pt), width:3.46cm)[
          #text("Acesse formações disponíveis  entrando no Painel Mais Professores e colocando “equidade racial” no filtro", fill: txBranco, weight: "bold", size: sizeBody * 0.7)
        ]
      ]

      #v(0cm)

      #shadow(blur: 4pt, dx: 1pt, dy: 1pt,  fill: rgb(0, 0, 0, 25%), radius: 4pt)[
        #box(
          fill: white,
          inset: .25cm,
          radius: (top: 4pt),
          width: 2.5cm
        )[#image("../assets/qrcodes/py/avamec.svg", width: 100%)]
      ]
      #v(-.58cm)
      #shadow(blur: 4pt, dx: 1pt, dy: 1pt,  fill: rgb(0, 0, 0, 25%), radius: (top-left: 4pt, bottom-right: 4pt))[
        #box(fill: txPreto, inset: (top:6pt, x: 4pt, bottom:4pt), radius: (top-left: 4pt, bottom-right: 4pt), width:2.6cm)[
          #text("Acesse o AVAMEC", fill: txBranco, weight: "bold", size: sizeBody * 0.7)
        ]
      ]

      #v(0cm)

      #shadow(blur: 4pt, dx: 1pt, dy: 1pt,  fill: rgb(0, 0, 0, 25%), radius: 4pt)[
        #box(
          fill: white,
          inset: .25cm,
          radius: (top: 4pt),
          width: 2.5cm
        )[#image("../assets/qrcodes/py/formacoes-pneerq.svg", width: 100%)]
      ]
      #v(-.58cm)
      #shadow(blur: 4pt, dx: 1pt, dy: 1pt,  fill: rgb(0, 0, 0, 25%), radius: (top-left: 4pt, bottom-right: 4pt))[
        #box(fill: txPreto, inset: (top:6pt, x: 4pt, bottom:4pt), radius: (top-left: 4pt, bottom-right: 4pt), width:2.5cm)[
          #text("Acesse a página de formações da PNEERQ", fill: txBranco, weight: "bold", size: sizeBody * 0.7)
        ]
      ]
    ]
  ]
}