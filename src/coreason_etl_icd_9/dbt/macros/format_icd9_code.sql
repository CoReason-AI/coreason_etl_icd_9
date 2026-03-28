{% macro format_icd9_code(raw_code, domain_type) %}
    {#
       AGENT INSTRUCTION: This macro handles the complex business logic of formatting legacy ICD-9 fixed-width strings.
       It applies the "decimal rule" to place a period inside the code depending on whether it's a Diagnosis (DX) or Procedure (SG).
       This is strictly executed inside Postgres to ensure deterministic analytical modeling in the Silver layer.
    #}
    CASE
        WHEN LOWER({{ domain_type }}) = 'diagnosis' THEN
            CASE
                -- E-codes (External causes) have their decimal after the 4th character
                WHEN SUBSTRING({{ raw_code }} FROM 1 FOR 1) = 'E' AND LENGTH({{ raw_code }}) > 4 THEN
                    SUBSTRING({{ raw_code }} FROM 1 FOR 4) || '.' || SUBSTRING({{ raw_code }} FROM 5)
                -- V-codes and normal numbers have their decimal after the 3rd character
                WHEN SUBSTRING({{ raw_code }} FROM 1 FOR 1) != 'E' AND LENGTH({{ raw_code }}) > 3 THEN
                    SUBSTRING({{ raw_code }} FROM 1 FOR 3) || '.' || SUBSTRING({{ raw_code }} FROM 4)
                ELSE {{ raw_code }}
            END
        WHEN LOWER({{ domain_type }}) = 'procedure' THEN
            CASE
                -- Procedures have their decimal after the 2nd character
                WHEN LENGTH({{ raw_code }}) > 2 THEN
                    SUBSTRING({{ raw_code }} FROM 1 FOR 2) || '.' || SUBSTRING({{ raw_code }} FROM 3)
                ELSE {{ raw_code }}
            END
        ELSE {{ raw_code }}
    END
{% endmacro %}
