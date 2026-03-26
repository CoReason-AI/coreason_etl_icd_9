{% macro generate_coreason_id(raw_code, domain_type) %}
    {#
       AGENT INSTRUCTION: This macro generates the coreason_id via UUIDv5
       using the required deterministic NAMESPACE_ICD9.
    #}
    uuid_generate_v5(
        'a7cffe80-da93-4ef3-8bf2-e6ea241d7ee2'::uuid,
        {{ format_icd9_code(raw_code, domain_type) }} || {{ domain_type }}
    )
{% endmacro %}
