// ============================================================================
// SHARED SUMÁRIO (TABLE OF CONTENTS) COMPONENT
// ============================================================================
// Sumário/Índice padrão para relatórios SEGAPE
// ============================================================================

#import "style.typ": *

/// Sumário padrão SEGAPE com estilo visual
///
/// Args:
///   titulo: Título do sumário (padrão: "Sumário")
///   background-image: Imagem de fundo (opcional)
///   show-page-numbers: Se deve mostrar números de página
///   depth: Profundidade do outline (1, 2, ou 3)
#let Sumario(
  titulo: "Sumário",
  background-image: none,
  show-page-numbers: true,
  depth: 2,
) = [
  #set page(
    background: if background-image != none [
      #image(background-image, width: 100%, height: 100%)
    ]
  )

  // Título do Sumário
  #align(center)[
    #text(
      titulo,
      size: 24pt,
      weight: "black",
      fill: mecAzul,
    )
  ]

  #v(20pt)

  // Conteúdo do sumário
  #outline(
    title: none,
    depth: depth,
    indent: auto,
    fill: if show-page-numbers [ #repeat[ #h(2pt).#h(2pt) ] ] else [ none ],
  )
]

/// Sumário simples sem decorações
#let SumarioSimples(
  titulo: "Sumário",
  depth: 2,
) = [
  #align(center)[
    #text(
      titulo,
      size: 20pt,
      weight: "bold",
      fill: corTitulosTextosGeral,
    )
  ]

  #v(15pt)

  #outline(
    title: none,
    depth: depth,
    indent: auto,
  )
]

/// Sumário customizado com grid layout
#let SumarioGrid(
  titulo: "Índice",
  items: (),
  columns: 1,
) = [
  #align(center)[
    #text(
      titulo,
      size: 24pt,
      weight: "black",
      fill: mecAzul,
    )
  ]

  #v(20pt)

  #grid(
    columns: columns,
    column-gutter: 20pt,
    row-gutter: 10pt,
    ..items.map(item => {
      box(
        width: 100%,
        inset: 10pt,
        fill: bgCinzaClaro,
        radius: 5pt,
      )[
        #grid(
          columns: (1fr, auto),
          column-gutter: 10pt,

          // Título da seção
          align(left)[
            #text(
              item.at("titulo", default: ""),
              size: sizeBody,
              weight: "semibold",
              fill: corTitulosTextosGeral,
            )
          ],

          // Número da página
          align(right)[
            #text(
              str(item.at("pagina", default: "")),
              size: sizeBody,
              weight: "regular",
              fill: txCinza,
            )
          ],
        )
      ]
    })
  )
]
