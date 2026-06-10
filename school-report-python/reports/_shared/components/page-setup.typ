// ============================================================================
// SHARED PAGE SETUP
// ============================================================================
// Configurações padrão de página para relatórios SEGAPE
// ============================================================================

#import "style.typ": *
#import "header.typ": Header
#import "footer.typ": Footer

/// Configuração padrão de documento SEGAPE
///
/// Args:
///   paper: Tamanho do papel (padrão: "a4")
///   margin: Margens do documento
///   font: Fonte do documento
///   font-size: Tamanho da fonte
///   language: Idioma do documento
#let document-setup(
  paper: "a4",
  margin: (
    left: 2cm,
    right: 2cm,
    top: 2.5cm,
    bottom: 2cm,
  ),
  font: "Rawline",
  font-size: 10pt,
  language: "pt",
) = {
  set page(
    paper: paper,
    margin: margin,
  )

  set text(
    font: font,
    size: font-size,
    lang: language,
  )

  // Configurações de parágrafo
  set par(
    justify: true,
    leading: 0.65em,
  )

  // Configurações de heading
  set heading(
    numbering: "1.1",
  )

  show heading.where(level: 1): it => [
    #set text(size: sizeTitle, weight: "bold", fill: mecAzul)
    #block(above: 20pt, below: 15pt)[#it]
  ]

  show heading.where(level: 2): it => [
    #set text(size: sizeSubtitle, weight: "bold", fill: corTitulosTextosGeral)
    #block(above: 15pt, below: 10pt)[#it]
  ]

  show heading.where(level: 3): it => [
    #set text(size: sizeBody, weight: "semibold", fill: corTitulosTextosGeral)
    #block(above: 10pt, below: 8pt)[#it]
  ]
}

/// Configuração de página com header e footer padrão
///
/// Args:
///   universidade: Nome da universidade
///   sigla: Sigla da universidade
///   header-title: Título customizado do header
///   header-subtitle: Subtítulo do header
///   show-logo: Se deve mostrar logo no header
///   show-footer: Se deve mostrar footer
///   show-page-number: Se deve mostrar número da página
#let page-with-header-footer(
  universidade: "",
  sigla: "",
  header-title: "",
  header-subtitle: "",
  show-logo: true,
  show-footer: true,
  show-page-number: true,
) = {
  set page(
    header: [
      #Header(
        universidade: universidade,
        sigla: sigla,
        titulo: header-title,
        subtitulo: header-subtitle,
        mostrarLogo: show-logo,
      )
      #v(10pt)
    ],
    footer: if show-footer [
      #v(10pt)
      #Footer(show-page-number: show-page-number)
    ],
  )
}

/// Esquema de numeração de páginas customizado
///
/// Exemplos:
///   - "1" - números simples
///   - "1 / 1" - número / total
///   - "I" - números romanos
///   - "Página 1 de 10" - texto customizado
#let page-numbering(
  format: "1",
  prefix: "",
  suffix: "",
  separator: " / ",
  show-total: false,
) = context {
  let current = counter(page).get().first()
  let total = counter(page).final().first()

  if show-total {
    prefix + str(current) + separator + str(total) + suffix
  } else {
    prefix + counter(page).display(format) + suffix
  }
}

/// Reinicia numeração de páginas
#let reset-page-counter() = {
  counter(page).update(1)
}

/// Oculta header e footer para uma página específica
#let page-no-header-footer(content) = {
  set page(
    header: none,
    footer: none,
  )
  content
}
