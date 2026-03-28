select
    formatted_icd9_code,
    long_description,
    ingestion_ts
from {{ ref('silver_icd9_ontology') }}
