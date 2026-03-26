from pathlib import Path

import yaml


def test_dbt_gold_model_structure() -> None:
    """Validates the dbt schema.yml correctly implements the Gold layer requirements."""
    schema_path = Path("src/coreason_etl_icd_9/dbt/models/marts/schema.yml")
    assert schema_path.exists(), "schema.yml is missing from the designated marts directory."

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
    models = {model["name"]: model for model in schema_doc["models"]}
    assert "gold_icd9_clinical_index" in models
    assert "gold_icd9_to_10_crosswalk_stub" in models

    index_model = models["gold_icd9_clinical_index"]
    index_columns = {col["name"]: col for col in index_model["columns"]}

    assert "formatted_icd9_code" in index_columns
    assert "long_description" in index_columns

    assert "tests" in index_columns["formatted_icd9_code"]
    assert "unique" in index_columns["formatted_icd9_code"]["tests"]
    assert "not_null" in index_columns["formatted_icd9_code"]["tests"]


def test_dbt_gold_models_sql() -> None:
    """Validates the gold SQL models compile logic appropriately."""
    index_path = Path("src/coreason_etl_icd_9/dbt/models/marts/gold_icd9_clinical_index.sql")
    stub_path = Path("src/coreason_etl_icd_9/dbt/models/marts/gold_icd9_to_10_crosswalk_stub.sql")

    assert index_path.exists(), "Clinical Index Model SQL is missing."
    assert stub_path.exists(), "Crosswalk Stub Model SQL is missing."

    with open(index_path) as f:
        sql = f.read()
    assert "formatted_icd9_code" in sql
    assert "long_description" in sql
    assert "{{ ref('silver_icd9_ontology') }}" in sql

    with open(stub_path) as f:
        sql = f.read()
    assert "formatted_icd9_code" in sql
    assert "target_icd10_code" in sql
    assert "{{ ref('silver_icd9_ontology') }}" in sql
