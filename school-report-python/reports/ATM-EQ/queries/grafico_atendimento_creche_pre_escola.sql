SELECT
  etapa,
  categoria,
  quantidade,
  percentual,
  anoReferencia,
  mesRefCarga
FROM `br-mec-segape-sandbox.projeto_segape_dmape_relat_automatico.atm_eq_grafico_atendimento_creche_pre_escola`
WHERE cod_ibge = @cod_ibge
  AND situacao = "Estuda"
ORDER BY
  CASE etapa
    WHEN "Creche" THEN 1
    WHEN "Pré-Escola" THEN 2
    ELSE 9
  END,
  CASE categoria
    WHEN "Branca" THEN 1
    WHEN "Preta" THEN 2
    WHEN "Parda" THEN 3
    WHEN "Amarela" THEN 4
    WHEN "Indígena" THEN 5
    ELSE 99
  END;
