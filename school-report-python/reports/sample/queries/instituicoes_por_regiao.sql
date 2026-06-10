-- Query simples para teste - instituições por região
SELECT
  regiao,
  COUNT(DISTINCT id_ies_capes) AS total
FROM `br-mec-segape.educacao_politica_capes.capes_ies_campus`
WHERE status_juridico = 'FEDERAL'
  AND regiao IS NOT NULL
  AND ano = (SELECT MAX(ano) FROM `br-mec-segape.educacao_politica_capes.capes_ies_campus`)
GROUP BY regiao
ORDER BY total DESC
