from pathlib import Path

import jinja2


def test_silver_model_compilation() -> None:
    """Test that the silver_icd9_ontology model compiles to expected SQL structure."""
    model_path = Path("src/coreason_etl_icd_9/dbt/models/staging/silver_icd9_ontology.sql")

    with open(model_path) as f:
        template_str = f.read()

    # We mock the global dbt functions required for the compilation
    def mock_source(source_name: str, table_name: str) -> str:
        return f"{source_name}_{table_name}"

    def mock_format_icd9_code(raw_code: str, domain_type: str) -> str:
        # Note: the sql file passes 'raw_code_string' and 'domain_type' as
        # unquoted strings because they are variables in sql
        return f"mock_format({raw_code}, {domain_type})"

    def mock_generate_coreason_id(raw_code: str, domain_type: str) -> str:
        return f"mock_generate_id({raw_code}, {domain_type})"

    env = jinja2.Environment()
    env.globals["source"] = mock_source
    env.globals["format_icd9_code"] = mock_format_icd9_code
    env.globals["generate_coreason_id"] = mock_generate_coreason_id

    template = env.from_string(template_str)
    rendered = template.render()
    sql = " ".join(rendered.split())

    # Verify key CTEs and column logic
    assert "from bronze_icd9_cm_raw" in sql
    assert "trim(raw_data->>'raw_code') as raw_code_string" in sql
    # The actual call is {{ format_icd9_code('raw_code_string', 'domain_type') }}
    # so raw_code is 'raw_code_string' and domain_type is 'domain_type'
    assert "mock_format(raw_code_string, domain_type) as formatted_icd9_code" in sql
    assert "mock_generate_id(raw_code_string, domain_type) as coreason_id" in sql
    assert "formatted_icd9_code," in sql
    assert "long_description," in sql
    assert "domain_type," in sql
    assert "ingestion_ts" in sql
