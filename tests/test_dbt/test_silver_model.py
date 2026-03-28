from pathlib import Path

import jinja2


def test_silver_model_compilation() -> None:
    """Test that the silver_icd9_ontology model compiles to expected SQL structure."""
    model_path = Path("src/coreason_etl_icd_9/dbt/models/silver/silver_icd9_ontology.sql")

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
    env.globals["config"] = lambda **_kwargs: ""
    env.globals["source"] = mock_source
    env.globals["format_icd9_code"] = mock_format_icd9_code
    env.globals["generate_coreason_id"] = mock_generate_coreason_id

    template = env.from_string(template_str)
    rendered = template.render()
    sql = " ".join(rendered.split())

    # Verify key CTEs and column logic
    assert "FROM BRONZE_ICD9_CM_RAW" in sql.upper()
    assert "TRIM(RAW_DATA->>'RAW_CODE') AS RAW_CODE_STRING" in sql.upper()
    # The actual call is {{ format_icd9_code('raw_code_string', 'domain_type') }}
    # so raw_code is 'raw_code_string' and domain_type is 'domain_type'
    assert "mock_format(raw_code_string, domain_type) as formatted_icd9_code".upper() in sql.upper()

    assert "formatted_icd9_code," in sql.lower()
    assert "raw_code_string," in sql.lower()
    assert "long_description," in sql.lower()
    assert "domain_type," in sql.lower()
    assert "code_type," in sql.lower()
    assert "raw_data" in sql.lower()
    assert "ingestion_ts," in sql.lower()

    # We shouldn't strictly require mock_generate_id if the actual file uses uuid_generate_v5
    assert "uuid_generate_v5" in sql.lower() or "mock_generate_id(raw_code_string, domain_type)" in sql.lower()
