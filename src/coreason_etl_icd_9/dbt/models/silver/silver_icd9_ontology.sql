{{ config(materialized='table') }}
WITH parsed_bronze AS (
    SELECT
        code_type,
        code_type AS domain_type,
        ingestion_ts,
        raw_data,
        TRIM(raw_data->>'raw_code') AS raw_code_string,
        TRIM(raw_data->>'raw_description') AS long_description
    FROM {{ source('bronze', 'icd9_cm_raw') }}
),
formatted_silver AS (
    SELECT
        code_type, domain_type, ingestion_ts, raw_data, raw_code_string, long_description,
        {{ format_icd9_code('raw_code_string', 'domain_type') }} AS formatted_icd9_code
    FROM parsed_bronze
)
SELECT
    uuid_generate_v5(
        'a7cffe80-da93-4ef3-8bf2-e6ea241d7ee2'::uuid,
        formatted_icd9_code || domain_type
    ) AS coreason_id,
    formatted_icd9_code, raw_code_string, long_description, domain_type, code_type, ingestion_ts, raw_data
FROM formatted_silver
