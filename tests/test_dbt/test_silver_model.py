from pathlib import Path

import yaml


def test_dbt_silver_model_structure() -> None:
    """Validates the dbt schema.yml correctly implements the Silver layer requirements."""
    schema_path = Path("src/coreason_etl_icd_9/dbt/models/staging/schema.yml")
    assert schema_path.exists(), "schema.yml is missing from the designated staging directory."

    with open(schema_path) as f:
        content = f.read()
        lines = []
        in_docstring = False
        for line in content.splitlines():
            if line.strip().startswith('"""'):
                in_docstring = not in_docstring
                continue
            if not in_docstring:
                lines.append(line)
        yaml_content = "\n".join(lines)
        schema_doc = yaml.safe_load(yaml_content)

    assert "models" in schema_doc
    models = schema_doc["models"]
    assert len(models) == 1

    silver_model = models[0]
    assert silver_model["name"] == "silver_icd9_ontology"

    columns = {col["name"]: col for col in silver_model["columns"]}
    assert "coreason_id" in columns
    assert "formatted_icd9_code" in columns
    assert "raw_code_string" in columns
    assert "long_description" in columns
    assert "domain_type" in columns

    # Check testing constraints as defined in the spec
    assert "tests" in columns["coreason_id"]
    assert "unique" in columns["coreason_id"]["tests"]
    assert "not_null" in columns["coreason_id"]["tests"]

    assert "not_null" in columns["long_description"]["tests"]
    assert "not_null" in columns["formatted_icd9_code"]["tests"]


def test_dbt_silver_model_sql() -> None:
    """Validates the silver SQL model compiles logic appropriately."""
    model_path = Path("src/coreason_etl_icd_9/dbt/models/staging/silver_icd9_ontology.sql")
    assert model_path.exists(), "Model SQL is missing."

    with open(model_path) as f:
        sql = f.read()

    assert "{{ source('bronze', 'icd9_cm_raw') }}" in sql
    assert "trim(raw_data->>'raw_code')" in sql
    assert "trim(raw_data->>'raw_description')" in sql
    assert "{{ format_icd9_code('raw_code_string', 'domain_type') }}" in sql
    assert "{{ generate_coreason_id('raw_code_string', 'domain_type') }}" in sql
