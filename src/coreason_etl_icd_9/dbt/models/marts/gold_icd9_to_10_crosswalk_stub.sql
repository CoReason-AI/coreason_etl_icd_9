select
    formatted_icd9_code,
    -- Placeholder columns for future integration with CMS GEMs (General Equivalence Mappings)
    cast(null as varchar(20)) as target_icd10_code,
    cast(null as varchar(255)) as map_type_flag,
    ingestion_ts
from {{ ref('silver_icd9_ontology') }}
