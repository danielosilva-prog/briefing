// TYP .
// import styles
#import "./components/style.typ": *

// import páginas de conteúdo
#import "./pages/P01-DespesaEmpenhada.typ": DespesaEmpenhada
#import "./pages/P02-CreditoRecebidoPorDestaque.typ": CreditoRecebidoPorDestaque

#let Article(
  title: "-",
  sigla: "UFRJ",
  universidade: "Universidade Federal do Rio de Janeiro",
  body,

  // Página 01 - Despesa Empenhada
  // Período 1 (2019-2022)
  p1OrcamentoMedioPeriodo1: "R$ xxx,xx bi",
  p1OrcamentoAcumuladoPeriodo1: "R$ xxx,xx bi",
  p1PercentVariacaoOrcamentoPeriodo1: "xx,xx %",
  p1PercentIPCAPeriodo1: "xx,xx %",
  // Periodo 2 (2023-2026)
  p1OrcamentoMedioPeriodo2: "R$ xxx,xx bi",
  p1OrcamentoAcumuladoPeriodo2: "R$ xxx,xx bi",
  p1IncrementoOrcamentario: "R$ xxx,xx bi",
  p1PercentVariacaoOrcamentoPeriodo2: "xx,xx %",
  p1PercentIPCAPeriodo2: "xx,xx %",
  p1PercentIncrementoOrcamentario: "xx,xx %",

  // Página 02 - Orçamento Geral + 
  ////
  // Orçamento Geral
  /////
  // Período 1 (2019-2022)
  p2CreditoRecebidoMedioPeriodo1: "R$ xxx,xx bi",
  p2CreditoRecebidoAcumuladoPeriodo1: "R$ xxx,xx bi",
  p2PercentVariacaoOrcamentoPeriodo1: "xx,xx %",
  p2PercentIPCAPeriodo1: "xx,xx %",
  // Periodo 2 (2023-2026)
  p2CreditoRecebidoMedioPeriodo2: "R$ xxx,xx bi",
  p2CreditoRecebidoAcumuladoPeriodo2: "R$ xxx,xx bi",
  p2IncrementoOrcamentario: "R$ xxx,xx bi",
  p2PercentVariacaoOrcamentoPeriodo2: "xx,xx %",
  p2PercentIPCAPeriodo2: "xx,xx %",
  p2PercentIncrementoOrcamentario: "xx,xx %",
  /////
  // Creditos Extraorçamentários
  /////
  // Período 1 (2019-2022)
  p2CECreditoRecebidoMedioPeriodo1:  "R$ xxx,xx bi",
  p2CECreditoRecebidoAcumuladoPeriodo1:  "R$ xxx,xx bi",
  p2CEPercentVariacaoOrcamentoPeriodo1:  "xx,xx %",
  p2CEPercentIPCAPeriodo1:  "xx,xx %",
  // Periodo 2 (2023-2026)
  p2CECreditoRecebidoMedioPeriodo2:  "R$ xxx,xx bi",
  p2CECreditoRecebidoAcumuladoPeriodo2:  "R$ xxx,xx bi",
  p2CEIncrementoOrcamentario:  "R$ xxx,xx bi",
  p2CEPercentVariacaoOrcamentoPeriodo2:  "xx,xx %",
  p2CEPercentIPCAPeriodo2:  "xx,xx %",
  p2CEPercentIncrementoOrcamentario:  "xx,xx %",

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


  /*****
   *
   ** PÁGINA 01 - DESPESA EMPENHADA
   *
   *****/

  // Header
  set page(
    paper: "a4",
    margin: (top: 4cm, right: .8cm, left: .8cm, bottom: 0cm),
    background: [
      #image("assets/background/Pagina01.svg", width: 100%)
    ],
    header-ascent: 0.5cm,
    header: [],
    footer: [],
    footer-descent: 0.8cm,
    numbering: "1",
  )

  // counter(page).update(1)

  DespesaEmpenhada(
    // Destinatário
    destinatario: destinatario,
    // Período 1 (2019-2022)
    p1OrcamentoMedioPeriodo1: p1OrcamentoMedioPeriodo1,
    p1OrcamentoAcumuladoPeriodo1: p1OrcamentoAcumuladoPeriodo1,
    p1PercentVariacaoOrcamentoPeriodo1: p1PercentVariacaoOrcamentoPeriodo1,
    p1PercentIPCAPeriodo1: p1PercentIPCAPeriodo1,
    // Periodo 2 (2023-2026)
    p1OrcamentoMedioPeriodo2: p1OrcamentoMedioPeriodo2,
    p1OrcamentoAcumuladoPeriodo2: p1OrcamentoAcumuladoPeriodo2,
    p1IncrementoOrcamentario: p1IncrementoOrcamentario,
    p1PercentVariacaoOrcamentoPeriodo2: p1PercentVariacaoOrcamentoPeriodo2,
    p1PercentIPCAPeriodo2: p1PercentIPCAPeriodo2,
    p1PercentIncrementoOrcamentario: p1PercentIncrementoOrcamentario,
    sigla: sigla,
    universidade: universidade,
  )

  /*****
   *
   ** PÁGINA 02 - CRÉDITO RECEBIDO POR DESTAQUE - Ministério da Educação (Geral)
   *
   *****/

  // Header
  set page(
    paper: "a4",
    margin: (top: 1.5cm, right: .75cm, left: .75cm, bottom: 0cm),
    header-ascent: 0.5cm,
    background: [
      #image("assets/background/Pagina02.svg", width: 100%)
    ],
    header: [],
    footer: [],
    footer-descent: 0.8cm,
    numbering: "1",
  )

  CreditoRecebidoPorDestaque(
    // Destinatário
    destinatario: destinatario,
    /////
    // Orçamento Geral
    /////
    // Período 1 (2019-2022)
    p2CreditoRecebidoMedioPeriodo1: p2CreditoRecebidoMedioPeriodo1,
    p2CreditoRecebidoAcumuladoPeriodo1: p2CreditoRecebidoAcumuladoPeriodo1,
    p2PercentVariacaoOrcamentoPeriodo1: p2PercentVariacaoOrcamentoPeriodo1,
    p2PercentIPCAPeriodo1: p2PercentIPCAPeriodo1,
    // Periodo 2 (2023-2026)
    p2CreditoRecebidoMedioPeriodo2: p2CreditoRecebidoMedioPeriodo2,
    p2CreditoRecebidoAcumuladoPeriodo2: p2CreditoRecebidoAcumuladoPeriodo2,
    p2IncrementoOrcamentario: p2IncrementoOrcamentario,
    p2PercentVariacaoOrcamentoPeriodo2: p2PercentVariacaoOrcamentoPeriodo2,
    p2PercentIPCAPeriodo2: p2PercentIPCAPeriodo2,
    p2PercentIncrementoOrcamentario: p2PercentIncrementoOrcamentario,
    /////
    // Creditos Extraorçamentários
    /////
    // Período 1 (2019-2022)
    p2CECreditoRecebidoMedioPeriodo1: p2CECreditoRecebidoMedioPeriodo1,
    p2CECreditoRecebidoAcumuladoPeriodo1: p2CECreditoRecebidoAcumuladoPeriodo1,
    p2CEPercentVariacaoOrcamentoPeriodo1: p2CEPercentVariacaoOrcamentoPeriodo1,
    p2CEPercentIPCAPeriodo1: p2CEPercentIPCAPeriodo1,
    // Periodo 2 (2023-2026)
    p2CECreditoRecebidoMedioPeriodo2: p2CECreditoRecebidoMedioPeriodo2,
    p2CECreditoRecebidoAcumuladoPeriodo2: p2CECreditoRecebidoAcumuladoPeriodo2,
    p2CEIncrementoOrcamentario: p2CEIncrementoOrcamentario,
    p2CEPercentVariacaoOrcamentoPeriodo2: p2CEPercentVariacaoOrcamentoPeriodo2,
    p2CEPercentIPCAPeriodo2: p2CEPercentIPCAPeriodo2,
    p2CEPercentIncrementoOrcamentario: p2CEPercentIncrementoOrcamentario,
    sigla: sigla,
    universidade: universidade,
  )
}
