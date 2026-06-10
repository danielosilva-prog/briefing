#import "../components/style.typ": *

#import "../components/header.typ": Header

#let Notas(..args) = {

  let dados = args.at(0)

  [


    #Header(
      titulo: [#v(.58cm)#text(weight: "extrabold")[Notas] de leitura],
      municipio: dados.municipio,
      uf: dados.uf,
      bgColor: rgb("265793"),
      textoDoSumario: "Notas de leitura",
      esconderDoSumario: false
    )

    #box(
      inset: (right: .22cm)
    )[
      #set text(fill: black, size: sizeBodySmall)

      #set par(spacing: 1.5em)

      #box(
        fill: rgb("EAEAEA50"),
        inset: (top: .75cm, right: .75cm, bottom: .6cm, left: .75cm),
        radius: (top-left: 20pt, bottom-right: 20pt),
        width: 100%
      )[

        #set par(leading: 1.15em, spacing: 18pt)

        Conteúdo em desenvolvimento.
      ]
    ]
  ]
}