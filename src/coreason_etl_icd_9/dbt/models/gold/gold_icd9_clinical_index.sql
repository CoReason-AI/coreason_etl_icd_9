{{ config(materialized='table') }}

{#
   AGENT INSTRUCTION: This model implements the comprehensive Gold analytical layer table.
   It must explicitly SELECT * from the Silver layer to retain ALL Bronze lineage columns,
   including `raw_data`, `ingestion_ts`, and `code_type`.
   This table is optimized for AI agents, vectorization, and NLP legacy medical note translation.
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
