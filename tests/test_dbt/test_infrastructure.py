from pathlib import Path

import yaml


def test_silver_schema_yml_structure() -> None:
    """Verify that silver schema.yml exists and has the required structure and tests."""
    schema_path = Path("src/coreason_etl_icd_9/dbt/models/silver/schema.yml")
    assert schema_path.exists(), "schema.yml for silver models must exist"

    with open(schema_path) as f:
        data = yaml.safe_load(f)

    assert "models" in data
    models = {m["name"]: m for m in data["models"]}

    # Check silver_icd9_ontology
    assert "silver_icd9_ontology" in models
    model = models["silver_icd9_ontology"]

    columns = {c["name"]: c for c in model.get("columns", [])}

    # Check specific fields and tests as per FRD/TRD
    assert "coreason_id" in columns
    assert set(columns["coreason_id"].get("data_tests", [])) == {"unique", "not_null"}

    assert "formatted_icd9_code" in columns
    # We have dbt_utils.unique_combination_of_columns instead of simple not_null
    tests = columns["formatted_icd9_code"].get("data_tests", [])
    assert "not_null" in tests
    assert any(isinstance(t, dict) and "dbt_utils.unique_combination_of_columns" in t for t in tests)

    assert "long_description" in columns
    assert "not_null" in columns["long_description"].get("data_tests", [])

    assert "code_type" in columns
    assert "not_null" in columns["code_type"].get("data_tests", [])


def test_gold_schema_yml_structure() -> None:
    """Verify that gold schema.yml exists and has the required structure and tests."""
    schema_path = Path("src/coreason_etl_icd_9/dbt/models/gold/schema.yml")
    assert schema_path.exists(), "schema.yml for gold models must exist"

    with open(schema_path) as f:
        data = yaml.safe_load(f)

    assert "models" in data
    models = {m["name"]: m for m in data["models"]}

    # gold_icd9_clinical_index
    assert "gold_icd9_clinical_index" in models
    index_cols = {c["name"]: c for c in models["gold_icd9_clinical_index"].get("columns", [])}
    assert "formatted_icd9_code" in index_cols
    assert "not_null" in index_cols["formatted_icd9_code"].get("data_tests", [])
    assert "long_description" in index_cols
    assert "not_null" in index_cols["long_description"].get("data_tests", [])

    # gold_icd9_to_10_crosswalk_stub
    assert "gold_icd9_to_10_crosswalk_stub" in models
    crosswalk_cols = {c["name"]: c for c in models["gold_icd9_to_10_crosswalk_stub"].get("columns", [])}
    assert "formatted_icd9_code" in crosswalk_cols
    assert "not_null" in crosswalk_cols["formatted_icd9_code"].get("data_tests", [])
