{% macro format_icd9_code(raw_code, domain_type) %}
    {#
       AGENT INSTRUCTION: This macro reconstructs the clinical decimal point.
       Rules:
       - Diagnosis Rule: If code starts with 'E', place decimal after 4th char.
         Else (including V or numbers), if > 3 chars, place decimal after 3rd char.
       - Procedure Rule: Place decimal after 2nd char if > 2 chars.
    #}
    case
        when {{ domain_type }} = 'Procedure' then
            case
                when length({{ raw_code }}) > 2 then substr({{ raw_code }}, 1, 2) || '.' || substr({{ raw_code }}, 3)
                else {{ raw_code }}
            end
        when {{ domain_type }} = 'Diagnosis' then
            case
                when substring({{ raw_code }} from 1 for 1) = 'E' then
                    case
                        when length({{ raw_code }}) > 4 then substr({{ raw_code }}, 1, 4) || '.' || substr({{ raw_code }}, 5)
                        else {{ raw_code }}
                    end
                else
                    case
                        when length({{ raw_code }}) > 3 then substr({{ raw_code }}, 1, 3) || '.' || substr({{ raw_code }}, 4)
                        else {{ raw_code }}
                    end
            end
        else {{ raw_code }}
    end
{% endmacro %}
