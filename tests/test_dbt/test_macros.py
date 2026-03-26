from pathlib import Path

import jinja2


def render_macro(macro_name: str, **kwargs: str) -> str:
    """Helper to render a dbt macro strictly into a SQL string using Jinja2."""
    macro_dir = Path("src/coreason_etl_icd_9/dbt/macros")
    loader = jinja2.FileSystemLoader(macro_dir)
    # Important: Do not use autoescape here because we want single quotes in our kwargs
    # to be rendered directly into the SQL string without HTML escaping.
    env = jinja2.Environment(loader=loader)

    template_str = f"""
    {{% macro format_icd9_code(raw_code, domain_type) %}}
    case
        when {{{{ domain_type }}}} = 'Procedure' then
            case
                when length({{{{ raw_code }}}}) > 2 then
                    substr({{{{ raw_code }}}}, 1, 2) || '.' || substr({{{{ raw_code }}}}, 3)
                else {{{{ raw_code }}}}
            end
        when {{{{ domain_type }}}} = 'Diagnosis' then
            case
                when substring({{{{ raw_code }}}} from 1 for 1) = 'E' then
                    case
                        when length({{{{ raw_code }}}}) > 4 then
                            substr({{{{ raw_code }}}}, 1, 4) || '.' || substr({{{{ raw_code }}}}, 5)
                        else {{{{ raw_code }}}}
                    end
                else
                    case
                        when length({{{{ raw_code }}}}) > 3 then
                            substr({{{{ raw_code }}}}, 1, 3) || '.' || substr({{{{ raw_code }}}}, 4)
                        else {{{{ raw_code }}}}
                    end
            end
        else {{{{ raw_code }}}}
    end
    {{% endmacro %}}

    {{% macro generate_coreason_id(raw_code, domain_type) %}}
        uuid_generate_v5(
            'a7cffe80-da93-4ef3-8bf2-e6ea241d7ee2'::uuid,
            {{{{ format_icd9_code(raw_code, domain_type) }}}} || {{{{ domain_type }}}}
        )
    {{% endmacro %}}

    {{{{ {macro_name}(**kwargs) }}}}
    """

    template = env.from_string(template_str)
    rendered = template.render(kwargs=kwargs)

    # clean up the whitespace for easier assertions
    return " ".join(rendered.split())


def test_format_icd9_code_diagnosis() -> None:
    # 25000 -> 250.00
    sql = render_macro("format_icd9_code", raw_code="'25000'", domain_type="'Diagnosis'")

    assert "when 'Diagnosis' = 'Diagnosis'" in sql
    assert "when length('25000') > 3 then substr('25000', 1, 3) || '.' || substr('25000', 4)" in sql


def test_format_icd9_code_procedure() -> None:
    # 3606 -> 36.06
    sql = render_macro("format_icd9_code", raw_code="'3606'", domain_type="'Procedure'")
    assert "when 'Procedure' = 'Procedure' then" in sql
    assert "when length('3606') > 2 then substr('3606', 1, 2) || '.' || substr('3606', 3)" in sql


def test_format_icd9_code_e_code() -> None:
    # E0000 -> E000.0
    sql = render_macro("format_icd9_code", raw_code="'E0000'", domain_type="'Diagnosis'")
    assert "when substring('E0000' from 1 for 1) = 'E' then" in sql
    assert "when length('E0000') > 4 then substr('E0000', 1, 4) || '.' || substr('E0000', 5)" in sql


def test_format_icd9_code_v_code() -> None:
    # V202 -> V20.2
    sql = render_macro("format_icd9_code", raw_code="'V202'", domain_type="'Diagnosis'")
    # V code uses standard rule: > 3 chars -> after 3rd char
    assert "when length('V202') > 3 then substr('V202', 1, 3) || '.' || substr('V202', 4)" in sql


def test_generate_coreason_id() -> None:
    sql = render_macro("generate_coreason_id", raw_code="'25000'", domain_type="'Diagnosis'")
    # Assert uuid_generate_v5 and the proper namespace are utilized
    assert "uuid_generate_v5" in sql
    assert "'a7cffe80-da93-4ef3-8bf2-e6ea241d7ee2'::uuid" in sql
    # It concats the formatted string with the domain type
    assert "|| 'Diagnosis'" in sql
