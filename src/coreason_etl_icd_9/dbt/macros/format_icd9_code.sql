{% macro format_icd9_code(raw_code, domain_type) %}
    CASE
        -- Athena OMOP safeguard: if decimal already exists, pass through
        WHEN POSITION('.' IN {{ raw_code }}) > 0 THEN {{ raw_code }}
        
        WHEN LOWER({{ domain_type }}) = 'diagnosis' THEN
            CASE
                WHEN SUBSTRING({{ raw_code }} FROM 1 FOR 1) = 'E' AND LENGTH({{ raw_code }}) > 4 THEN
                    SUBSTRING({{ raw_code }} FROM 1 FOR 4) || '.' || SUBSTRING({{ raw_code }} FROM 5)
                WHEN SUBSTRING({{ raw_code }} FROM 1 FOR 1) != 'E' AND LENGTH({{ raw_code }}) > 3 THEN
                    SUBSTRING({{ raw_code }} FROM 1 FOR 3) || '.' || SUBSTRING({{ raw_code }} FROM 4)
                ELSE {{ raw_code }}
            END
        WHEN LOWER({{ domain_type }}) = 'procedure' THEN
            CASE
                WHEN LENGTH({{ raw_code }}) > 2 THEN
                    SUBSTRING({{ raw_code }} FROM 1 FOR 2) || '.' || SUBSTRING({{ raw_code }} FROM 3)
                ELSE {{ raw_code }}
            END
        ELSE {{ raw_code }}
    END
{% endmacro %}
