{{ config(materialized='table') }}
SELECT
    coreason_id, formatted_icd9_code, raw_code_string, long_description, domain_type, code_type, ingestion_ts, raw_data
FROM {{ ref('silver_icd9_ontology') }}
