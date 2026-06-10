-- ===================================
-- {{ cookiecutter.report_id }} - Example Query
-- {{ cookiecutter.report_name }}
-- ===================================
--
-- Description: {{ cookiecutter.description }}
--
-- This is a sample query. Replace with your actual BigQuery SQL.
--
{% if cookiecutter.has_parameters == 'yes' -%}
-- Parameters:
--   @{{ cookiecutter.parameter_name }}: {{ cookiecutter.parameter_description }}
--
{% endif -%}
-- Usage:
--   This query is executed automatically by the report pipeline.
--   Results are passed to the Typst template as JSON data.
--

SELECT
    'Example Category' AS category,
    100 AS value,
    'Sample description' AS description
{% if cookiecutter.has_parameters == 'yes' -%}
WHERE
    -- Replace with your actual filter condition
    1 = 1
    -- Example: cod_ibge = @{{ cookiecutter.parameter_name }}
{% endif %}
