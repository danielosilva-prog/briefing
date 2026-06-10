// ============================================================================
// SHARED STYLES - SEGAPE School Reports
// ============================================================================
// Este arquivo define estilos compartilhados entre todos os relatórios.
// Cada relatório pode sobrescrever ou extender estes estilos.
// ============================================================================

// ----------------------------------------------------------------------------
// TYPOGRAPHY SIZES
// ----------------------------------------------------------------------------
#let sizeBody = 11pt
#let sizeSubtitle = 13pt
#let sizeTitle = 15pt
#let sizeTotalizerSmall = 15pt
#let sizeTotalizerBig = 24pt
#let sizeBodySmall = 9pt      // Corpo reduzido opcional
#let sizeCaption = 7pt         // Legendas, notas, fontes

// ----------------------------------------------------------------------------
// TYPOGRAPHY WEIGHTS
// ----------------------------------------------------------------------------
#let weightBody = "regular"
#let weightSubtitle = "black"
#let weightTitle = "bold"
#let weightCharts = "semibold"

// ----------------------------------------------------------------------------
// BRAND COLORS - MEC/SEGAPE
// ----------------------------------------------------------------------------
#let mecAzul = rgb("0095DA")        // Azul principal MEC
#let mecAzulEscuro = rgb("0073A8")  // Azul escuro
#let mecVerdeEscuro = rgb("008F00") // Verde escuro
#let mecVerde = rgb("00D000")       // Verde claro
#let mecAmarelo = rgb("FFD000")     // Amarelo
#let mecLaranja = rgb("FF7D00")     // Laranja

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

// ----------------------------------------------------------------------------
// TEXT COLORS
// ----------------------------------------------------------------------------
#let txBranco = rgb("FFFFFF")
#let txAzul = rgb("183EFF")
#let txAzulClaro = rgb("24B0DB")
#let txAmarelo = rgb("FFD000")
#let txCinza = rgb("646464")
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
  let text = if value == none { "" } else { str(value) }
  if text == "" or text == "-" or text == "--" {
    text
  } else {
    "R$ " + text
  }
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
