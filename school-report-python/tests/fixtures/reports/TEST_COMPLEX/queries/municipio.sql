-- Municipio query with parameters
SELECT
    cod_ibge,
    nome,
    populacao
FROM municipios
WHERE cod_ibge = @cod_ibge
  AND ano_referencia = @ano
