#import "../components/style.typ": *

#let Sumario = context [
  #set page(
    background: image("../assets/backgrounds/sumario.svg", width: 100%, height: 100%),
    margin: (top: 3cm, right: 2cm, left: 8cm, bottom: 3cm),
    footer: [],
  )

  #set text(
    hyphenate: false,
    font: "Rawline",
  )

  #show outline.entry: it => box(inset: (top: 12pt))[
    #link(
      it.element.location(),
      it.indented(it.prefix(), it.inner()),
    )
  ]
  
  #box(inset: (top: 12pt))[
    #show outline: set text(size: sizeBody - 1pt, tracking: -0.025em, weight: weightBody, fill: txCinza, hyphenate: false)
    #outline(
      title: "Sumário",
    )
  ]
]
