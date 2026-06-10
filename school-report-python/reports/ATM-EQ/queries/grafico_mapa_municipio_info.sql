WITH municipio_geo AS (
  SELECT
    id_municipio,
    nome,
    id_uf,
    sigla_uf,
    centroide
  FROM `br-mec-segape.educacao_dados_mestres.municipio`
  WHERE id_municipio = @cod_ibge
),
capital_geo AS (
  SELECT
    id_municipio,
    nome,
    id_uf,
    sigla_uf,
    centroide
  FROM `br-mec-segape.educacao_dados_mestres.municipio`
  WHERE capital_uf = 1
)
SELECT
  m.id_municipio AS codIbge,
  m.nome AS municipioNome,
  m.sigla_uf AS UF,
  ST_X(m.centroide) AS municipioLon,
  ST_Y(m.centroide) AS municipioLat,
  c.id_municipio AS codIbgeCapital,
  c.nome AS nomeCapital,
  ST_X(c.centroide) AS municipioLonCap,
  ST_Y(c.centroide) AS municipioLatCap
FROM municipio_geo m
JOIN capital_geo c
  ON c.id_uf = m.id_uf
