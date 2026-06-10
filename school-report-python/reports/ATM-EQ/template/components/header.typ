// ============================================================================
// SHARED HEADER COMPONENT
// ============================================================================
// Cabeçalho padrão para relatórios SEGAPE
// ============================================================================

#import "style.typ": *
#import "@preview/shadowed:0.3.0": shadow

/// Cabeçalho padrão SEGAPE
///
/// Args:
///   universidade: Nome da universidade
///   sigla: Sigla da universidade (para buscar logo)
///   bgColor: Cor de fundo do cabeçalho
///   txColor: Cor do texto
///   titulo: Título customizado (se vazio, usa nome da universidade)
///   subtitulo: Subtítulo opcional
///   mostrarLogo: Se deve mostrar logo da universidade
///   logoBasePath: Caminho base para os logos (relativo ao template)
#let Header(
  titulo: [],
  municipio: "",
  uf: "",
  bgColor: pneerqLaranja,
  txColor: txPreto,
  textoDoSumario: "",
  esconderDoSumario: false,
) = context [

  #pagebreak()

  #let to-string(it) = {
    if type(it) == str {
      it
    } else if type(it) != content {
      str(it)
    } else if it.has("text") {
      it.text
    } else if it.has("children") {
      it.children.map(to-string).join()
    } else if it.has("body") {
      to-string(it.body)
    } else if it == [ ] {
      " "
    }
  }

  #let textoSumarioFinal = if textoDoSumario == "" { to-string(titulo) } else { textoDoSumario }

  #set par(justify: false)

  #if esconderDoSumario == true {
    v(.5cm)
  } else {
    hide[
      = #textoSumarioFinal
    ]
  }

  // Município (UF)
  #place(
    top + right,
    dx: .8cm,
    dy: -.3cm
  )[
    #set text(fill: white, size: 10pt)
    #set par(leading: 8pt)
    #align(center + horizon)[
      #grid(
        columns: (auto, auto),
        gutter: .25cm,
        image("../assets/logos/pneerq.svg", height: 1cm),
        box()[
          #shadow(blur: 4pt, dx: 1pt, dy: 1pt,  fill: rgb(0, 0, 0, 25%), radius: (left: 50%, bottom: 50%))[
            #box(
              fill: pneerqLaranja,
              inset: (x:.25cm, bottom: .35cm, top: .5cm),
              width: 3cm,
              height: 3cm,
              radius: (left: 50%, bottom: 50%)
            )[
              #set par(leading: .8em)
              #text(weight: weightTitle, size: 11pt, fill: white)[
                #municipio
              ]
              #linebreak()
              #text(weight: weightTitle, size: 9pt, fill: white)[
                (#uf)
              ]
              // Bandeira da UF
              #place(
                center + bottom,
                dx: 0cm,
                dy: .65cm
              )[
                #shadow(blur: 4pt, dx: 1pt, dy: 1pt,  fill: rgb(0, 0, 0, 25%), radius: (bottom: 2pt, top-left: 2pt))[
                  #box(
                    radius: (bottom: 2pt, top-left: 2pt),
                    clip: true,
                  )[
                    #image(
                      "../assets/flags/" + upper(uf) + ".png",
                      height: .7cm
                    )
                  ]
                ]
              ]
            ]
          ]
        ]
      )
    ]
  ]

  // Título da seção
  #place(
    top + left,
    dx: -.75cm,
    dy: .25cm
  )[
    #box(
      width: 1.05cm,
      height: 2.15cm,
      fill: bgColor
    )
  ]

  #box(
    inset: (top: .5cm, right: 3.5cm, bottom: .28cm, left: .75cm)
  )[
    #set par(leading: 14pt)
    #text(weight: weightTitlePage, size: sizeTitlePage, fill: rgb(txColor))[#titulo]
  ]


  #v(.25cm)
]
