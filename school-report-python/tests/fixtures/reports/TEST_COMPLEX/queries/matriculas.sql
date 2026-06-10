-- Matriculas query
SELECT
    etapa,
    COUNT(*) AS total
FROM matriculas
WHERE cod_ibge = @cod_ibge
  AND ano = @ano
GROUP BY etapa
