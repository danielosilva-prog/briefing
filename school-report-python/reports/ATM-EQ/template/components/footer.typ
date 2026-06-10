// ============================================================================
// SHARED FOOTER COMPONENT
// ============================================================================
// Rodapé padrão para relatórios SEGAPE
// ============================================================================

#import "style.typ": *

#let Footer() = context [
  #align(bottom)[
    #move(dx: -8mm, dy: 9mm)[
      #box(width: 211mm, height:2.4cm)[#image("../assets/backgrounds/footer-pages.svg", width: 100%)]
    ]
    #align(center + bottom)[
      //#image("../assets/backgrounds/footer-pages.svg", height: 100%)
      #move(dx: 0pt, dy: -30pt)[
        #text(
          counter(page).display(),
          fill: rgb("000"),
          size: sizeBody,
          weight: weightBody,
        )
      ]
    ]
  ]
]

/// Rodapé simples sem logos (apenas número da página)
#let FooterSimple(
  text-color: rgb("000"),
) = context [
  #align(center + bottom)[
    #text(
      counter(page).display(),
      fill: text-color,
      size: sizeBody,
      weight: weightBody,
    )
  ]
]
