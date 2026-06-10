
#import "@preview/shadowed:0.3.0": shadow

#let sizeBody = 11pt
#let sizeSubtitle = 13pt
#let sizeTitle = 15pt
#let sizeTotalizerSmall = 15pt
#let sizeTotalizerBig = 24pt

// corpo “reduzido” opcional
#let sizeBodySmall = 9pt

// legendas / notas / fonte
#let sizeCaption = 7pt

#let weightBody = "regular"
#let weightSubtitle = "black"
#let weightTitle = "bold"
#let weightCharts = "semibold"

// Distâncias
#let gap = 6pt

// Background colors:
#let bgAzul = rgb("183EFF")
#let bgAzulClaro = rgb("24B0DB")
#let bgAmarelo = rgb("FFD000")
#let bgCinza = rgb("8C8C8C")
#let bgVerde = rgb("00D000")
#let bgVerdeEscuro = rgb("008F00")
#let bgBranco = rgb("FFFFFF")
#let bgLaranja = rgb("FF7D00")
#let bgCinzaClaro = rgb("F5F5F5")

// Text colors:
#let txBranco = rgb("fff")
#let txAzul = rgb("183EFF")
#let txAzulClaro = rgb("24B0DB")
#let txAmarelo = rgb("FFD000")
#let txCinza = rgb("646464")
#let txVerde = rgb("00D000")
#let txVerdeEscuro = rgb("008F00")
#let corTitulosTextosGeral = rgb("3c3c3c")
#let txLaranja = rgb("FF7D00")

// Border colors:
#let borderAzul = rgb("183EFF")
#let borderAzulClaro = rgb("24B0DB")
#let borderAmarelo = rgb("FFD000")
#let borderCinza = rgb("8C8C8C")
#let borderVerde = rgb("00D000")
#let borderVerdeEscuro = rgb("008F00")
#let borderBranco = rgb("FFFFFF")
#let borderLaranja = rgb("FF7D00")

/*
// Modalidades e Turnos
#let presencial = rgb("#01b601");
#let presencialDiurno = rgb("1BDE1B");
#let presencialNoturno = rgb("89FF80");
#let ead = rgb("005F00");

// Tipos de Vagas
#let vagasNovas = rgb("FFD000");
#let vagasEspeciais = rgb("4AB46D");
#let vagasRemanescentes = rgb("FF7D00");
#let inscritosVagasRemanescentes = rgb("0095DA");
#let ingressantesVagasRemanescentes = rgb("AAB46D");
#let reservaVagas = rgb("00008C");
#let vagasGerais = rgb("183EFF");

// Cores de Texto e Títulos
#let corTitulosTextosGeral = rgb("3C3C3C");
#let corTituloGraficosTabelas = rgb("646464");
#let corCaixasTextos = rgb("F5F5F5");

// Taxas de Ocupação
#let maiorTaxaOcupacao = rgb("0059DA");
#let menorTaxaOcupacao = rgb("0095DA");

// Sexo
#let masculino = rgb("8D00CE");
#let feminino = rgb("540D74");
#let naoInformadoSexo = rgb("BBBBBB");

// Ingressantes por Modalidade e Turno
#let ingressantesPorCursoTurnoEModalide = rgb("0095DA");
#let ingressantesDiurno = rgb("0073A8");
#let ingressantesNoturno = rgb("C46D19");
#let ingressantesEAD = rgb("589258");

// Raça/Cor dos Ingressantes
#let brancos = rgb("0073A8");
#let pretos = rgb("C46D19");
#let pardos = rgb("589258");
#let amarelos = rgb("80CC32");
#let indigenas = rgb("A94B4B");
#let naoDeclaradoRacaCor = rgb("BBBBBB");

// Categoria de rede
#let redePublica = rgb("FFA73D");
#let redePrivada = rgb("784D7A");
#let redeNaoInformada = rgb("24B0DB");
#let matriculas = rgb("0095DA")
#let concluintes = rgb("0095DA")
*/



#let format-currency(value) = {
  let text = if value == none { "" } else { str(value) }
  if text == "" or text == "-" or text == "--" {
    text
  } else {
    "R$ " + text
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
