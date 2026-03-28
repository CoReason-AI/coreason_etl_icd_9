with raw_data as (
    select
        _dlt_id,
        code_type as domain_type,
        ingestion_ts,
        -- Extract the fields from the flexible JSONB column and trim whitespace
        trim(raw_data->>'raw_code') as raw_code_string,
        trim(raw_data->>'raw_description') as long_description
    from {{ source('bronze', 'icd9_cm_raw') }}
),

formatted as (
    select
        *,
        -- Call the formatting macro which inserts the clinical decimal point based on type
        {{ format_icd9_code('raw_code_string', 'domain_type') }} as formatted_icd9_code
    from raw_data
)

select
    -- Call the UUIDv5 deterministic generation macro for the coreason_id
    {{ generate_coreason_id('raw_code_string', 'domain_type') }} as coreason_id,
    formatted_icd9_code,
    raw_code_string,
    long_description,
    domain_type,
    ingestion_ts
from formatted
