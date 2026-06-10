// TYP .
// import styles
#import "./components/style.typ": *

// import components
#import "./components/header.typ": Header
#import "./components/footer.typ": Footer

// import páginas de apoio
#import "./pages/capa.typ": Capa
#import "./pages/fichaTecnica.typ": FichaTecnica
#import "./pages/sumario.typ": Sumario
#import "./pages/plateduc.typ": Plateduc
#import "./pages/fundo.typ": Fundo
#import "./pages/glossario.typ": Glossario

// import páginas de conteúdo
#import "./pages/P01-DespesaEmpenhada.typ": DespesaEmpenhada
#import "./pages/P02-CreditoRecebidoPorDestaque.typ": CreditoRecebidoPorDestaque
#import "./pages/P03-CreditoRecebidoPorDestaque26101.typ": CreditoRecebidoPorDestaque26101
#import "./pages/P04-CreditoRecebidoPorDestaque26290.typ": CreditoRecebidoPorDestaque26290
#import "./pages/P05-CreditoRecebidoPorDestaque26291.typ": CreditoRecebidoPorDestaque26291
#import "./pages/P06-CreditoRecebidoPorDestaque26298.typ": CreditoRecebidoPorDestaque26298
#import "./pages/P07-CreditoRecebidoPorDestaque26443.typ": CreditoRecebidoPorDestaque26443

#let Article(
  title: "-",
  sigla: "UFRJ",
  universidade: "Universidade Federal do Rio de Janeiro",
  body,

  // Página 01 - Despesa Empenhada
  // Período 1 (2019-2021)
  p1OrcamentoMedioPeriodo1: "R$ xxx,xx bi",
  p1OrcamentoAcumuladoPeriodo1: "R$ xxx,xx bi",
  p1PercentVariacaoOrcamentoPeriodo1: "xx,xx %",
  p1PercentIPCAPeriodo1: "xx,xx %",
  // Periodo 2 (2023-2025)
  p1OrcamentoMedioPeriodo2: "R$ xxx,xx bi",
  p1OrcamentoAcumuladoPeriodo2: "R$ xxx,xx bi",
  p1IncrementoOrcamentario: "R$ xxx,xx bi",
  p1PercentVariacaoOrcamentoPeriodo2: "xx,xx %",
  p1PercentIPCAPeriodo2: "xx,xx %",
  p1PercentIncrementoOrcamentario: "xx,xx %",

  // Página 02 - Crédito Recebido por Destaque (Geral)
  // Período 1 (2019-2021)
  p2CreditoRecebidoMedioPeriodo1: "R$ xxx,xx bi",
  p2CreditoRecebidoAcumuladoPeriodo1: "R$ xxx,xx bi",
  p2PercentVariacaoOrcamentoPeriodo1: "xx,xx %",
  p2PercentIPCAPeriodo1: "xx,xx %",
  // Periodo 2 (2023-2025)
  p2CreditoRecebidoMedioPeriodo2: "R$ xxx,xx bi",
  p2CreditoRecebidoAcumuladoPeriodo2: "R$ xxx,xx bi",
  p2IncrementoOrcamentario: "R$ xxx,xx bi",
  p2PercentVariacaoOrcamentoPeriodo2: "xx,xx %",
  p2PercentIPCAPeriodo2: "xx,xx %",
  p2PercentIncrementoOrcamentario: "xx,xx %",

  // Página 03 - Crédito Recebido por Destaque - MEC UO 26101
  // Período 1 (2019-2021)
  p3CreditoRecebidoMedioPeriodo1: "R$ xxx,xx bi",
  p3CreditoRecebidoAcumuladoPeriodo1: "R$ xxx,xx bi",
  p3PercentVariacaoOrcamentoPeriodo1: "xx,xx %",
  p3PercentIPCAPeriodo1: "xx,xx %",
  // Periodo 2 (2023-2025)
  p3CreditoRecebidoMedioPeriodo2: "R$ xxx,xx bi",
  p3CreditoRecebidoAcumuladoPeriodo2: "R$ xxx,xx bi",
  p3IncrementoOrcamentario: "R$ xxx,xx bi",
  p3PercentVariacaoOrcamentoPeriodo2: "xx,xx %",
  p3PercentIPCAPeriodo2: "xx,xx %",
  p3PercentIncrementoOrcamentario: "xx,xx %",

  // Página 04 - Crédito Recebido por Destaque - INEP UO 26290
  // Período 1 (2019-2021)
  p4CreditoRecebidoMedioPeriodo1: "R$ xxx,xx bi",
  p4CreditoRecebidoAcumuladoPeriodo1: "R$ xxx,xx bi",
  p4PercentVariacaoOrcamentoPeriodo1: "xx,xx %",
  p4PercentIPCAPeriodo1: "xx,xx %",
  // Periodo 2 (2023-2025)
  p4CreditoRecebidoMedioPeriodo2: "R$ xxx,xx bi",
  p4CreditoRecebidoAcumuladoPeriodo2: "R$ xxx,xx bi",
  p4IncrementoOrcamentario: "R$ xxx,xx bi",
  p4PercentVariacaoOrcamentoPeriodo2: "xx,xx %",
  p4PercentIPCAPeriodo2: "xx,xx %",
  p4PercentIncrementoOrcamentario: "xx,xx %",

  // Página 05 - Crédito Recebido por Destaque - CAPES UO 26291
  // Período 1 (2019-2021)
  p5CreditoRecebidoMedioPeriodo1: "R$ xxx,xx bi",
  p5CreditoRecebidoAcumuladoPeriodo1: "R$ xxx,xx bi",
  p5PercentVariacaoOrcamentoPeriodo1: "xx,xx %",
  p5PercentIPCAPeriodo1: "xx,xx %",
  // Periodo 2 (2023-2025)
  p5CreditoRecebidoMedioPeriodo2: "R$ xxx,xx bi",
  p5CreditoRecebidoAcumuladoPeriodo2: "R$ xxx,xx bi",
  p5IncrementoOrcamentario: "R$ xxx,xx bi",
  p5PercentVariacaoOrcamentoPeriodo2: "xx,xx %",
  p5PercentIPCAPeriodo2: "xx,xx %",
  p5PercentIncrementoOrcamentario: "xx,xx %",

  // Página 06 - Crédito Recebido por Destaque - FNDE UO 26298
  // Período 1 (2019-2021)
  p6CreditoRecebidoMedioPeriodo1: "R$ xxx,xx bi",
  p6CreditoRecebidoAcumuladoPeriodo1: "R$ xxx,xx bi",
  p6PercentVariacaoOrcamentoPeriodo1: "xx,xx %",
  p6PercentIPCAPeriodo1: "xx,xx %",
  // Periodo 2 (2023-2025)
  p6CreditoRecebidoMedioPeriodo2: "R$ xxx,xx bi",
  p6CreditoRecebidoAcumuladoPeriodo2: "R$ xxx,xx bi",
  p6IncrementoOrcamentario: "R$ xxx,xx bi",
  p6PercentVariacaoOrcamentoPeriodo2: "xx,xx %",
  p6PercentIPCAPeriodo2: "xx,xx %",
  p6PercentIncrementoOrcamentario: "xx,xx %",

  // Página 07 - Crédito Recebido por Destaque - EBSERH UO 26443
  // Período 1 (2019-2021)
  p7CreditoRecebidoMedioPeriodo1: "R$ xxx,xx bi",
  p7CreditoRecebidoAcumuladoPeriodo1: "R$ xxx,xx bi",
  p7PercentVariacaoOrcamentoPeriodo1: "xx,xx %",
  p7PercentIPCAPeriodo1: "xx,xx %",
  // Periodo 2 (2023-2025)
  p7CreditoRecebidoMedioPeriodo2: "R$ xxx,xx bi",
  p7CreditoRecebidoAcumuladoPeriodo2: "R$ xxx,xx bi",
  p7IncrementoOrcamentario: "R$ xxx,xx bi",
  p7PercentVariacaoOrcamentoPeriodo2: "xx,xx %",
  p7PercentIPCAPeriodo2: "xx,xx %",
  p7PercentIncrementoOrcamentario: "xx,xx %",
) = {
  // Configuração global de texto
  set text(
    font: "Rawline",
    size: sizeBody,
    tracking: 0.3pt,
    fill: corTitulosTextosGeral,
  )  

  let destinatario = if sigla == "Brasil" { "às universidades federais" } else { "à " + universidade }

  // Configuração global de página
  set page(
    paper: "a4",
    header: none,
    footer: none,
    numbering: none,
    background: none,
  )

  // CAPA
  Capa(
    universidade: universidade,
  )

  pagebreak()

  // FICHA TÉCNICA
  FichaTecnica()

  // SUMÁRIO
  Sumario


  


/*****
   *
   ** PÁGINA 01 - DESPESA EMPENHADA
   *
   *****/

  // Header
  set page(
    paper: "a4",
    margin: (top: 2.5cm, right: 1cm, left: 1cm, bottom: 2.5cm),
    header-ascent: 0.5cm,
    header: Header(
      universidade: universidade,
      sigla: sigla,
      txColor: txBranco,
      titulo: "Glossário",
      subtitulo: "Terminologia utilizada no Aqui Tem MEC - Ensino Superior - Orçamento",
    ),
    footer: [
      #Footer
    ],
    footer-descent: 0.8cm,
    numbering: "1",
  )

  Glossario()


  /*****
   *
   ** PÁGINA 01 - DESPESA EMPENHADA
   *
   *****/

  // Header
  set page(
    paper: "a4",
    margin: (top: 2.5cm, right: 1cm, left: 1cm, bottom: 2.5cm),
    header-ascent: 0.5cm,
    header: Header(
      universidade: universidade,
      sigla: sigla,
      txColor: txBranco,
      titulo: "Despesa Empenhada",
      subtitulo: "Orçamento Originário",
    ),
    footer: [
      #Footer
    ],
    footer-descent: 0.8cm,
    numbering: "1",
  )

  // counter(page).update(1)

  DespesaEmpenhada(
    // Destinatário
    destinatario: destinatario,
    // Período 1 (2019-2021)
    p1OrcamentoMedioPeriodo1: p1OrcamentoMedioPeriodo1,
    p1OrcamentoAcumuladoPeriodo1: p1OrcamentoAcumuladoPeriodo1,
    p1PercentVariacaoOrcamentoPeriodo1: p1PercentVariacaoOrcamentoPeriodo1,
    p1PercentIPCAPeriodo1: p1PercentIPCAPeriodo1,
    // Periodo 2 (2023-2025)
    p1OrcamentoMedioPeriodo2: p1OrcamentoMedioPeriodo2,
    p1OrcamentoAcumuladoPeriodo2: p1OrcamentoAcumuladoPeriodo2,
    p1IncrementoOrcamentario: p1IncrementoOrcamentario,
    p1PercentVariacaoOrcamentoPeriodo2: p1PercentVariacaoOrcamentoPeriodo2,
    p1PercentIPCAPeriodo2: p1PercentIPCAPeriodo2,
    p1PercentIncrementoOrcamentario: p1PercentIncrementoOrcamentario,
  )

  /*****
   *
   ** PÁGINA 02 - CRÉDITO RECEBIDO POR DESTAQUE - Ministério da Educação (Geral)
   *
   *****/

  // Header
  set page(
    paper: "a4",
    margin: (top: 2.5cm, right: 1cm, left: 1cm, bottom: 2.5cm),
    header-ascent: 0.5cm,
    header: Header(
      universidade: universidade,
      sigla: sigla,
      txColor: txBranco,
      titulo: "Crédito Recebido por Destaque",
      subtitulo: "Ministério da Educação",
    ),
    footer: [
      #Footer
    ],
    footer-descent: 0.8cm,
    numbering: "1",
  )

  CreditoRecebidoPorDestaque(
    // Destinatário
    destinatario: destinatario,
    // Período 1 (2019-2021)
    p2CreditoRecebidoMedioPeriodo1: p2CreditoRecebidoMedioPeriodo1,
    p2CreditoRecebidoAcumuladoPeriodo1: p2CreditoRecebidoAcumuladoPeriodo1,
    p2PercentVariacaoOrcamentoPeriodo1: p2PercentVariacaoOrcamentoPeriodo1,
    p2PercentIPCAPeriodo1: p2PercentIPCAPeriodo1,
    // Periodo 2 (2023-2025)
    p2CreditoRecebidoMedioPeriodo2: p2CreditoRecebidoMedioPeriodo2,
    p2CreditoRecebidoAcumuladoPeriodo2: p2CreditoRecebidoAcumuladoPeriodo2,
    p2IncrementoOrcamentario: p2IncrementoOrcamentario,
    p2PercentVariacaoOrcamentoPeriodo2: p2PercentVariacaoOrcamentoPeriodo2,
    p2PercentIPCAPeriodo2: p2PercentIPCAPeriodo2,
    p2PercentIncrementoOrcamentario: p2PercentIncrementoOrcamentario,
  )

  /*****
   *
   ** PÁGINA 03 - CRÉDITO RECEBIDO POR DESTAQUE - Ministério da Educação UO 26101
   *
   *****/

  // Header
  set page(
    paper: "a4",
    margin: (top: 2.5cm, right: 1cm, left: 1cm, bottom: 2.5cm),
    header-ascent: 0.5cm,
    header: Header(
      universidade: universidade,
      sigla: sigla,
      txColor: txBranco,
      titulo: "Crédito Recebido por Destaque",
      subtitulo: "Ministério da Educação UO 26101",
    ),
    footer: [
      #Footer
    ],
    footer-descent: 0.8cm,
    numbering: "1",
  )

  CreditoRecebidoPorDestaque26101(
    // Destinatário
    destinatario: destinatario,
    // Período 1 (2019-2021)
    p3CreditoRecebidoMedioPeriodo1: p3CreditoRecebidoMedioPeriodo1,
    p3CreditoRecebidoAcumuladoPeriodo1: p3CreditoRecebidoAcumuladoPeriodo1,
    p3PercentVariacaoOrcamentoPeriodo1: p3PercentVariacaoOrcamentoPeriodo1,
    p3PercentIPCAPeriodo1: p3PercentIPCAPeriodo1,
    // Periodo 2 (2023-2025)
    p3CreditoRecebidoMedioPeriodo2: p3CreditoRecebidoMedioPeriodo2,
    p3CreditoRecebidoAcumuladoPeriodo2: p3CreditoRecebidoAcumuladoPeriodo2,
    p3IncrementoOrcamentario: p3IncrementoOrcamentario,
    p3PercentVariacaoOrcamentoPeriodo2: p3PercentVariacaoOrcamentoPeriodo2,
    p3PercentIPCAPeriodo2: p3PercentIPCAPeriodo2,
    p3PercentIncrementoOrcamentario: p3PercentIncrementoOrcamentario,
  )

  /*****
   *
   ** PÁGINA 04 - CRÉDITO RECEBIDO POR DESTAQUE - INEP - UO 26290
   *
   *****/

  // Header
  set page(
    paper: "a4",
    margin: (top: 2.5cm, right: 1cm, left: 1cm, bottom: 2.5cm),
    header-ascent: 0.5cm,
    header: Header(
      universidade: universidade,
      sigla: sigla,
      txColor: txBranco,
      titulo: "Crédito Recebido por Destaque",
      subtitulo: "INEP - UO 26290",
    ),
    footer: [
      #Footer
    ],
    footer-descent: 0.8cm,
    numbering: "1",
  )

  CreditoRecebidoPorDestaque26290(
    // Destinatário
    destinatario: destinatario,
    // Período 1 (2019-2021)
    p4CreditoRecebidoMedioPeriodo1: p4CreditoRecebidoMedioPeriodo1,
    p4CreditoRecebidoAcumuladoPeriodo1: p4CreditoRecebidoAcumuladoPeriodo1,
    p4PercentVariacaoOrcamentoPeriodo1: p4PercentVariacaoOrcamentoPeriodo1,
    p4PercentIPCAPeriodo1: p4PercentIPCAPeriodo1,
    // Periodo 2 (2023-2025)
    p4CreditoRecebidoMedioPeriodo2: p4CreditoRecebidoMedioPeriodo2,
    p4CreditoRecebidoAcumuladoPeriodo2: p4CreditoRecebidoAcumuladoPeriodo2,
    p4IncrementoOrcamentario: p4IncrementoOrcamentario,
    p4PercentVariacaoOrcamentoPeriodo2: p4PercentVariacaoOrcamentoPeriodo2,
    p4PercentIPCAPeriodo2: p4PercentIPCAPeriodo2,
    p4PercentIncrementoOrcamentario: p4PercentIncrementoOrcamentario,
  )

  /*****
   *
   ** PÁGINA 05 - CRÉDITO RECEBIDO POR DESTAQUE - CAPES - UO 26291
   *
   *****/

  // Header
  set page(
    paper: "a4",
    margin: (top: 2.5cm, right: 1cm, left: 1cm, bottom: 2.5cm),
    header-ascent: 0.5cm,
    header: Header(
      universidade: universidade,
      sigla: sigla,
      txColor: txBranco,
      titulo: "Crédito Recebido por Destaque",
      subtitulo: "CAPES - UO 26291",
    ),
    footer: [
      #Footer
    ],
    footer-descent: 0.8cm,
    numbering: "1",
  )

  CreditoRecebidoPorDestaque26291(
    // Destinatário
    destinatario: destinatario,
    // Período 1 (2019-2021)
    p5CreditoRecebidoMedioPeriodo1: p5CreditoRecebidoMedioPeriodo1,
    p5CreditoRecebidoAcumuladoPeriodo1: p5CreditoRecebidoAcumuladoPeriodo1,
    p5PercentVariacaoOrcamentoPeriodo1: p5PercentVariacaoOrcamentoPeriodo1,
    p5PercentIPCAPeriodo1: p5PercentIPCAPeriodo1,
    // Periodo 2 (2023-2025)
    p5CreditoRecebidoMedioPeriodo2: p5CreditoRecebidoMedioPeriodo2,
    p5CreditoRecebidoAcumuladoPeriodo2: p5CreditoRecebidoAcumuladoPeriodo2,
    p5IncrementoOrcamentario: p5IncrementoOrcamentario,
    p5PercentVariacaoOrcamentoPeriodo2: p5PercentVariacaoOrcamentoPeriodo2,
    p5PercentIPCAPeriodo2: p5PercentIPCAPeriodo2,
    p5PercentIncrementoOrcamentario: p5PercentIncrementoOrcamentario,
  )

  /*****
   *
   ** PÁGINA 06 - CRÉDITO RECEBIDO POR DESTAQUE - FNDE - UO 26298
   *
   *****/

  // Header
  set page(
    paper: "a4",
    margin: (top: 2.5cm, right: 1cm, left: 1cm, bottom: 2.5cm),
    header-ascent: 0.5cm,
    header: Header(
      universidade: universidade,
      sigla: sigla,
      txColor: txBranco,
      titulo: "Crédito Recebido por Destaque",
      subtitulo: "FNDE - UO 26298",
    ),
    footer: [
      #Footer
    ],
    footer-descent: 0.8cm,
    numbering: "1",
  )

  CreditoRecebidoPorDestaque26298(
    // Destinatário
    destinatario: destinatario,
    // Período 1 (2019-2021)
    p6CreditoRecebidoMedioPeriodo1: p6CreditoRecebidoMedioPeriodo1,
    p6CreditoRecebidoAcumuladoPeriodo1: p6CreditoRecebidoAcumuladoPeriodo1,
    p6PercentVariacaoOrcamentoPeriodo1: p6PercentVariacaoOrcamentoPeriodo1,
    p6PercentIPCAPeriodo1: p6PercentIPCAPeriodo1,
    // Periodo 2 (2023-2025)
    p6CreditoRecebidoMedioPeriodo2: p6CreditoRecebidoMedioPeriodo2,
    p6CreditoRecebidoAcumuladoPeriodo2: p6CreditoRecebidoAcumuladoPeriodo2,
    p6IncrementoOrcamentario: p6IncrementoOrcamentario,
    p6PercentVariacaoOrcamentoPeriodo2: p6PercentVariacaoOrcamentoPeriodo2,
    p6PercentIPCAPeriodo2: p6PercentIPCAPeriodo2,
    p6PercentIncrementoOrcamentario: p6PercentIncrementoOrcamentario,
  )

  /*****
   *
   ** PÁGINA 07 - CRÉDITO RECEBIDO POR DESTAQUE - EBSERH - UO 26443
   *
   *****/

  // Header
  set page(
    paper: "a4",
    margin: (top: 2.5cm, right: 1cm, left: 1cm, bottom: 2.5cm),
    header-ascent: 0.5cm,
    header: Header(
      universidade: universidade,
      sigla: sigla,
      txColor: txBranco,
      titulo: "Crédito Recebido por Destaque",
      subtitulo: "EBSERH - UO 26443",
    ),
    footer: [
      #Footer
    ],
    footer-descent: 0.8cm,
    numbering: "1",
  )

  CreditoRecebidoPorDestaque26443(
    // Destinatário
    destinatario: destinatario,
    // Período 1 (2019-2021)
    p7CreditoRecebidoMedioPeriodo1: p7CreditoRecebidoMedioPeriodo1,
    p7CreditoRecebidoAcumuladoPeriodo1: p7CreditoRecebidoAcumuladoPeriodo1,
    p7PercentVariacaoOrcamentoPeriodo1: p7PercentVariacaoOrcamentoPeriodo1,
    p7PercentIPCAPeriodo1: p7PercentIPCAPeriodo1,
    // Periodo 2 (2023-2025)
    p7CreditoRecebidoMedioPeriodo2: p7CreditoRecebidoMedioPeriodo2,
    p7CreditoRecebidoAcumuladoPeriodo2: p7CreditoRecebidoAcumuladoPeriodo2,
    p7IncrementoOrcamentario: p7IncrementoOrcamentario,
    p7PercentVariacaoOrcamentoPeriodo2: p7PercentVariacaoOrcamentoPeriodo2,
    p7PercentIPCAPeriodo2: p7PercentIPCAPeriodo2,
    p7PercentIncrementoOrcamentario: p7PercentIncrementoOrcamentario,
  )

  // PLATEDUC
  Plateduc()

  // CAPA FINAL
  Fundo
}
