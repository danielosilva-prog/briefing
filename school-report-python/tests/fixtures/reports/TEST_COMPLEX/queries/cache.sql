-- Cache lookup query
SELECT
    gcs_path,
    created_at
FROM report_cache
WHERE report_id = :report_id
  AND parameters_hash = :params_hash
  AND expires_at > NOW()
