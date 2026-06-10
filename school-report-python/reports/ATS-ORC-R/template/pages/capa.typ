#import "../components/style.typ": *

#let Capa(universidade: str) = [
  #set page(
    background: [
      #image("../assets/background/Capa.svg", width: 100%)
    ],
    margin: (top: 0pt, right: 0pt, bottom: 0pt, left: 40pt),
  )
  #set text(
    font: "Rawline",
    size: sizeTitle,
  )
  #set par(
    leading: 20pt
  )
  #align(left + top)[
    #move(dy: 22cm)[
      #box(width: 65%)[ 
        #text(upper(universidade), size: 26pt, weight: weightSubtitle, fill: txAmarelo)
      ]
    ]
  ]
]
