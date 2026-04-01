import re
from pathlib import Path

import pytest
from jinja2 import Environment, FileSystemLoader


@pytest.fixture
def jinja_env() -> Environment:
    """Creates a Jinja2 environment configured to load dbt macros from the source directory."""
    macros_dir = Path("src/coreason_etl_icd_9/dbt/macros")
    return Environment(loader=FileSystemLoader(str(macros_dir)))


def normalize_sql(sql: str) -> str:
    """Helper to remove excess whitespace and newlines from compiled SQL for easy comparison."""
    return re.sub(r"\s+", " ", sql).strip()


def test_format_icd9_code_macro(jinja_env: Environment) -> None:
    """Verifies that the `format_icd9_code` macro generates the correct Postgres SQL."""

    template = jinja_env.from_string("""
        {% from 'format_icd9_code.sql' import format_icd9_code %}
        {{ format_icd9_code('raw_code_col', 'domain_type_col') }}
    """)

    compiled_sql = template.render()
    normalized_sql = normalize_sql(compiled_sql)

    # Basic structural assertions
    assert "CASE" in normalized_sql
    assert "WHEN LOWER(domain_type_col) = 'diagnosis' THEN" in normalized_sql
    assert "WHEN LOWER(domain_type_col) = 'procedure' THEN" in normalized_sql

    # Test Diagnosis E-Code Logic
    e_code_logic = (
        "WHEN SUBSTRING(raw_code_col FROM 1 FOR 1) = 'E' AND LENGTH(raw_code_col) > 4 "
        "THEN SUBSTRING(raw_code_col FROM 1 FOR 4) || '.' || SUBSTRING(raw_code_col FROM 5)"
    )
    assert e_code_logic in normalized_sql

    # Test Diagnosis V-Code / Normal Logic
    v_code_logic = (
        "WHEN SUBSTRING(raw_code_col FROM 1 FOR 1) != 'E' AND LENGTH(raw_code_col) > 3 "
        "THEN SUBSTRING(raw_code_col FROM 1 FOR 3) || '.' || SUBSTRING(raw_code_col FROM 4)"
    )
    assert v_code_logic in normalized_sql

    # Test Procedure Logic
    proc_logic = (
        "WHEN LENGTH(raw_code_col) > 2 "
        "THEN SUBSTRING(raw_code_col FROM 1 FOR 2) || '.' || SUBSTRING(raw_code_col FROM 3)"
    )
    assert proc_logic in normalized_sql


def test_format_icd9_code_macro_edge_cases(jinja_env: Environment) -> None:
    """Tests that the `format_icd9_code` macro generates correct SQL with specific edge cases."""

    # We will simulate the execution of the SQL macro with string inputs.
    # While we cannot easily *run* the SQL in Postgres here, we can confirm the structure for literal edge cases.

    template = jinja_env.from_string("""
        {% from 'format_icd9_code.sql' import format_icd9_code %}
        {{ format_icd9_code("'E123'", "'diagnosis'") }}
        {{ format_icd9_code("'E12345'", "'diagnosis'") }}
        {{ format_icd9_code("'V12'", "'diagnosis'") }}
        {{ format_icd9_code("'V1234'", "'diagnosis'") }}
        {{ format_icd9_code("'12'", "'procedure'") }}
        {{ format_icd9_code("'1234'", "'procedure'") }}
        {{ format_icd9_code("'1234'", "'unknown'") }}
        {{ format_icd9_code("NULL", "NULL") }}
        {{ format_icd9_code("''", "''") }}
        {{ format_icd9_code("'A B C D E'", "'diagnosis'") }}
    """)
    compiled_sql = template.render()
    normalized_sql = normalize_sql(compiled_sql)

    assert "CASE WHEN LOWER('diagnosis') = 'diagnosis'" in normalized_sql
    assert "WHEN SUBSTRING('E123' FROM 1 FOR 1) = 'E' AND LENGTH('E123') > 4" in normalized_sql
    assert "WHEN SUBSTRING('E12345' FROM 1 FOR 1) = 'E' AND LENGTH('E12345') > 4" in normalized_sql
    assert "WHEN SUBSTRING('V12' FROM 1 FOR 1) != 'E' AND LENGTH('V12') > 3" in normalized_sql
    assert "WHEN SUBSTRING('V1234' FROM 1 FOR 1) != 'E' AND LENGTH('V1234') > 3" in normalized_sql

    assert "WHEN LOWER('procedure') = 'procedure'" in normalized_sql
    assert "WHEN LENGTH('12') > 2" in normalized_sql
    assert "WHEN LENGTH('1234') > 2" in normalized_sql

    assert "ELSE '1234'" in normalized_sql

    # Edge cases
    assert "WHEN LOWER(NULL) = 'diagnosis'" in normalized_sql
    assert "WHEN LOWER('') = 'diagnosis'" in normalized_sql
    assert (
        "WHEN SUBSTRING('A B C D E' FROM 1 FOR 1) != 'E' AND LENGTH('A B C D E') > 3 THEN "
        "SUBSTRING('A B C D E' FROM 1 FOR 3) || '.' || SUBSTRING('A B C D E' FROM 4)"
    ) in normalized_sql
