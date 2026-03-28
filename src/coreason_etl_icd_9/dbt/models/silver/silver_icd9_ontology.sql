{{ config(materialized='table') }}

{#
   AGENT INSTRUCTION: This model implements the Silver analytical layer.
   It extracts data from the Bronze JSONB column, applies deterministic formatting via macro,
   and strictly passes through the original Bronze columns (`code_type`, `ingestion_ts`, `raw_data`).
   UUIDv5 identity resolution relies on the pre-configured Postgres namespace.
#}

WITH parsed_bronze AS (
    SELECT
        -- Pass-through original columns
        code_type,
        code_type AS domain_type,
        ingestion_ts,
        raw_data,

        -- Extract and clean JSONB fields
        TRIM(raw_data->>'raw_code') AS raw_code_string,
        TRIM(raw_data->>'raw_description') AS long_description

    FROM {{ source('bronze', 'icd9_cm_raw') }}
),

formatted_silver AS (
    SELECT
        code_type,
        domain_type,
        ingestion_ts,
        raw_data,
        raw_code_string,
        long_description,

        -- Apply the Decimal Rule Macro
        {{ format_icd9_code('raw_code_string', 'domain_type') }} AS formatted_icd9_code

    FROM parsed_bronze
)

SELECT
    -- Generate UUIDv5 using the fixed Namespace ID and a deterministic string payload
    uuid_generate_v5(
        'a7cffe80-da93-4ef3-8bf2-e6ea241d7ee2'::uuid,
        formatted_icd9_code || domain_type
    ) AS coreason_id,

    formatted_icd9_code,
    raw_code_string,
    long_description,
    domain_type,
    code_type,
    ingestion_ts,
    raw_data

FROM formatted_silver
