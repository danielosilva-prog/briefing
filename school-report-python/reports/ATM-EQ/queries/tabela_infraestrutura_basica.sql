SELECT
  indicador,
  percentualBranca,
  percentualBrancaFmt,
  percentualPreta,
  percentualPretaFmt,
  percentualParda,
  percentualPardaFmt,
  percentualAmarela,
  percentualAmarelaFmt,
  percentualIndigena,
  percentualIndigenaFmt,
  percentualNaoDeclarada,
  percentualNaoDeclaradaFmt,
  percentualQuilombola,
  percentualQuilombolaFmt,
  anoReferencia
FROM `br-mec-segape-sandbox.projeto_segape_dmape_relat_automatico.atm_eq_tabela_infraestrutura_basica`
WHERE cod_ibge = @cod_ibge
ORDER BY
  CASE indicador
    WHEN "Água potável" THEN 1
    WHEN "Energia elétrica" THEN 2
    WHEN "Esgotamento sanitário" THEN 3
    WHEN "Biblioteca ou sala de leitura" THEN 4
    WHEN "Internet para alunos" THEN 5
    WHEN "Sala de professores" THEN 6
    WHEN "Banheiro" THEN 7
    WHEN "Todos os requisitos" THEN 8
    ELSE 99
  END;
