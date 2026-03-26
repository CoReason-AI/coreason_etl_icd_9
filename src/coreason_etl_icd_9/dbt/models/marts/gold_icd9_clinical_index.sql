select
    formatted_icd9_code,
    long_description
from {{ ref('silver_icd9_ontology') }}
