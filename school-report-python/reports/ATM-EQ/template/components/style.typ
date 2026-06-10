// ============================================================================
// SHARED STYLES - SEGAPE School Reports
// ============================================================================
// Este arquivo define estilos compartilhados entre todos os relatórios.
// Cada relatório pode sobrescrever ou extender estes estilos.
// ============================================================================

// ----------------------------------------------------------------------------
// EXTERNAL LIBRARIES
// ----------------------------------------------------------------------------
#import "@preview/shadowed:0.3.0": shadow

// ----------------------------------------------------------------------------
// TYPOGRAPHY SIZES
// ----------------------------------------------------------------------------
#let sizeBody = 11pt
#let sizeSubtitle = 13pt
#let sizeTitle = 13pt
#let sizeTotalizerSmall = 15pt
#let sizeTotalizerBig = 24pt
#let sizeTitlePage = 20pt
#let sizeBodySmall = 9pt  
#let sizeChartTitle = 8.8pt       // Corpo reduzido opcional
#let sizeCaption = 7pt         // Legendas, notas, fontes
#let gap = 12pt

// ----------------------------------------------------------------------------
// TYPOGRAPHY WEIGHTS
// ----------------------------------------------------------------------------
#let weightBody = "regular"
#let weightSubtitle = "black"
#let weightTitle = "bold"
#let weightCharts = "semibold"
#let weightTitlePage = 400
#let weightTitleChart = "black"

// ----------------------------------------------------------------------------
// BRAND COLORS - MEC/SEGAPE
// ----------------------------------------------------------------------------
#let mecAzul = rgb("0095DA")        // Azul principal MEC
#let mecAzulEscuro = rgb("0073A8")  // Azul escuro
#let mecVerdeEscuro = rgb("008F00") // Verde escuro
#let mecVerde = rgb("00D000")       // Verde claro
#let mecAmarelo = rgb("FFD000")     // Amarelo
#let mecLaranja = rgb("FF7D00")     // Laranja
#let pneerqLaranja = rgb("E05625")
#let pneerqLaranjaClaro = rgb("F39517")
#let pneerqVermelho = rgb("9A1915")
#let pneerqMarrom = rgb("330201")
#let pneerqMarromClaro = rgb("33020160")

// ----------------------------------------------------------------------------
// BACKGROUND COLORS
// ----------------------------------------------------------------------------
#let bgAzul = rgb("183EFF")
#let bgAzulClaro = rgb("24B0DB")
#let bgAmarelo = rgb("FFD000")
#let bgCinza = rgb("8C8C8C")
#let bgVerde = rgb("00D000")
#let bgVerdeEscuro = rgb("008F00")
#let bgBranco = rgb("FFFFFF")
#let bgLaranja = rgb("FF7D00")
#let bgCinzaClaro = rgb("F5F5F5")
#let bgTabela = rgb("EAEAEA")

// ----------------------------------------------------------------------------
// TEXT COLORS
// ----------------------------------------------------------------------------
#let txBranco = rgb("FFFFFF")
#let txPreto = rgb("000000")
#let txAzul = rgb("183EFF")
#let txAzulClaro = rgb("24B0DB")
#let txAmarelo = rgb("FFD000")
#let txCinza = rgb("646464")
#let txCinzaClaro = rgb("AAA")
#let txCinzaMedio = rgb("999")
#let txCinzaEscuro = rgb("333")
#let txVerde = rgb("00D000")
#let txVerdeEscuro = rgb("008F00")
#let txLaranja = rgb("FF7D00")
#let corTitulosTextosGeral = rgb("3C3C3C")
#let corTituloGraficosTabelas = rgb("646464")
#let corCaixasTextos = rgb("F5F5F5")

// ----------------------------------------------------------------------------
// BORDER COLORS
// ----------------------------------------------------------------------------
#let borderAzul = rgb("183EFF")
#let borderAzulClaro = rgb("24B0DB")
#let borderAmarelo = rgb("FFD000")
#let borderCinza = rgb("8C8C8C")
#let borderVerde = rgb("00D000")
#let borderVerdeEscuro = rgb("008F00")
#let borderBranco = rgb("FFFFFF")
#let borderLaranja = rgb("FF7D00")

// ----------------------------------------------------------------------------
// HELPER FUNCTIONS
// ----------------------------------------------------------------------------

/// Formata valor monetário brasileiro
/// Exemplo: format-currency(1234.56) -> "R$ 1.234,56"
#let format-currency(value) = {
  if value == none { return "" }
  if type(value) == str {
    if value == "" or value == "-" or value == "--" { return value }
    value = float(value)
  }

  let val = float(value)
  let negative = val < 0
  val = calc.abs(val)

  let integer = int(val)
  let decimal = int(calc.round((val - integer) * 100))

  if decimal == 100 {
    integer = integer + 1
    decimal = 0
  }

  let str-int = str(integer)
  let str-dec = str(decimal)
  if str-dec.len() < 2 { str-dec = "0" + str-dec }

  let result = ""
  let len = str-int.len()
  for i in range(len) {
    if i > 0 and calc.rem(len - i, 3) == 0 {
      result = result + "."
    }
    result = result + str-int.at(i)
  }

  "R$ " + (if negative { "-" } else { "" }) + result + "," + str-dec
}

/// Formata número brasileiro com separador de milhares
/// Exemplo: format-number(1234567) -> "1.234.567"
#let format-number(value) = {
  let text = if value == none { "" } else { str(value) }
  if text == "" or text == "-" or text == "--" {
    text
  } else {
    text
  }
}

/// Formata percentual brasileiro
/// Exemplo: format-percent(0.8531) -> "85,31%"
#let format-percent(value, decimals: 2) = {
  if value == none {
    ""
  } else {
    str(calc.round(value * 100, digits: decimals)) + "%"
  }
}
// Remove a casa deciamal se o número terminar com 0,0
#let format-no-zero(v) = {
  let text = if v == none {
    "-"
  } else {
    str(v)
  }

  if text == "0,0" {
    text
  } else if text.ends-with(
    ",0") {
    text.slice(0, text.len() - 2)
  } else if text.ends-with(
    ".0") {
    text.slice(0, text.len() - 2)
  } else {
    text
  }
}

#let chart-legend(..args) = {

  let dados = args.at(0)

  for (item) in dados {
      box(
        width: 0.7em,
        height: 0.7em,
        fill: rgb(item.color)
      )
      h(0.4em)
      text(size:sizeBodySmall)[#item.label]
      h(1em)
  }
}
