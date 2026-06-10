#import "../components/style.typ": *

#let Capa(..args) = {
  let dados = args.at(0)
  [
    #set page(
      background: [
        #image("../assets/backgrounds/capa-v2.svg", width: 100%)
      ],
      margin: (top: 0pt, right: 0pt, bottom: 0pt, left: 40pt),
      footer: [],
    )
    #set text(
      font: "Rawline",
      size: sizeTitle,
    )
    #align(left + top)[
      #set par(justify: false, leading: .8em)
      #move(dy: 22.25cm)[
        #box(width: 65%)[ 
          #text(size: 26pt, weight: weightSubtitle, fill: txPreto)[#upper(dados.municipio) (#upper(dados.uf))]
        ]
      ]
    ]
    #place(bottom + right, dy: -.5cm, dx: -.5cm)[
      #text(size:sizeCaption)[
        Versão gerada em #linebreak()#datetime.today().display("[day].[month].[year]")
      ]
    ]
  ]
}
