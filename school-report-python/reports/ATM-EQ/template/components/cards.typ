// ============================================================================
// SHARED CARDS & CONTAINERS
// ============================================================================
// Componentes de cards e containers para relatórios SEGAPE
// ============================================================================

#import "style.typ": *

/// Card simples com título e conteúdo
///
/// Args:
///   title: Título do card
///   content: Conteúdo do card
///   title-size: Tamanho do título
///   title-color: Cor do título
///   title-weight: Peso da fonte do título
#let Card(
  title: "",
  content,
  title-size: sizeSubtitle,
  title-color: corTituloGraficosTabelas,
  title-weight: weightSubtitle,
) = [
  #if title != "" [
    #align(center)[
      #par(justify: false)[
        #text(
          title,
          size: title-size,
          weight: title-weight,
          fill: title-color,
          hyphenate: false,
        )
      ]
    ]
    #v(10pt)
  ]
  #content
]

/// Card com borda e background
///
/// Args:
///   title: Título do card
///   content: Conteúdo do card
///   bg-color: Cor de fundo
///   border-color: Cor da borda
///   border-width: Largura da borda
///   radius: Raio dos cantos
///   inset: Padding interno
#let CardBoxed(
  title: none,
  content,
  bg-color: bgCinzaClaro,
  border-color: borderCinza,
  border-width: 1pt,
  radius: 5pt,
  inset: 15pt,
) = [
  #box(
    width: 100%,
    fill: bg-color,
    stroke: (paint: border-color, thickness: border-width),
    radius: radius,
    inset: inset,
  )[
    #if title != none [
      #align(center)[
        #text(
          title,
          size: sizeSubtitle,
          weight: weightSubtitle,
          fill: corTitulosTextosGeral,
        )
      ]
      #v(10pt)
    ]
    #content
  ]
]

/// Card com ícone e texto
///
/// Args:
///   icon: Caminho do ícone
///   title: Título
///   value: Valor principal
///   subtitle: Subtítulo/legenda
///   icon-size: Tamanho do ícone
///   bg-color: Cor de fundo
#let CardWithIcon(
  icon: none,
  title: "",
  value: "",
  subtitle: none,
  icon-size: 40pt,
  bg-color: bgCinzaClaro,
) = [
  #box(
    width: 100%,
    fill: bg-color,
    radius: 5pt,
    inset: 15pt,
  )[
    #grid(
      columns: (auto, 1fr),
      column-gutter: 15pt,
      align: horizon,

      // Ícone
      if icon != none [
        #image(icon, height: icon-size)
      ],

      // Texto
      [
        #if title != "" [
          #text(
            title,
            size: sizeBody,
            weight: "semibold",
            fill: txCinza,
          )
          #v(5pt)
        ]

        #text(
          value,
          size: sizeTotalizerBig,
          weight: "black",
          fill: corTitulosTextosGeral,
        )

        #if subtitle != none [
          #v(3pt)
          #text(
            subtitle,
            size: sizeCaption,
            weight: "regular",
            fill: txCinza,
          )
        ]
      ],
    )
  ]
]

/// Grid de cards
///
/// Args:
///   cards: Array de cards
///   columns: Número de colunas
///   gap: Espaçamento entre cards
#let CardGrid(
  cards: (),
  columns: 2,
  gap: 15pt,
) = [
  #grid(
    columns: columns,
    column-gutter: gap,
    row-gutter: gap,
    ..cards
  )
]
