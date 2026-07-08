{{ config(materialized='table') }}

{#
   AGENT INSTRUCTION: This model implements a placeholder stub for the Gold analytical layer.
   It serves as a bridge intended to be joined later with the official CMS GEMs (General Equivalence Mappings).
   It MUST retain all columns from the Silver layer for auditability, particularly `raw_data`.
#}

SELECT
    coreason_id,
    formatted_icd9_code,
    raw_code_string,
    long_description,
    domain_type,
    code_type,
    ingestion_ts,
    raw_data
FROM {{ ref('silver_icd9_ontology') }}
