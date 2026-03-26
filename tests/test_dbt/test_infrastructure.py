from pathlib import Path

import yaml


def test_staging_schema_yml_structure() -> None:
    """Verify that staging schema.yml exists and has the required structure and tests."""
    schema_path = Path("src/coreason_etl_icd_9/dbt/models/staging/schema.yml")
    assert schema_path.exists(), "schema.yml for staging models must exist"

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
    assert set(columns["coreason_id"].get("tests", [])) == {"unique", "not_null"}

    assert "formatted_icd9_code" in columns
    assert "not_null" in columns["formatted_icd9_code"].get("tests", [])

    assert "raw_code_string" in columns

    assert "long_description" in columns
    assert "not_null" in columns["long_description"].get("tests", [])

    assert "domain_type" in columns
    domain_tests = columns["domain_type"].get("tests", [])
    assert "not_null" in domain_tests
    # Check accepted values
    accepted = [t for t in domain_tests if isinstance(t, dict) and "accepted_values" in t]
    assert len(accepted) == 1
    assert set(accepted[0]["accepted_values"]["values"]) == {"Diagnosis", "Procedure"}


def test_marts_schema_yml_structure() -> None:
    """Verify that marts schema.yml exists and has the required structure and tests."""
    schema_path = Path("src/coreason_etl_icd_9/dbt/models/marts/schema.yml")
    assert schema_path.exists(), "schema.yml for marts models must exist"

    with open(schema_path) as f:
        data = yaml.safe_load(f)

    assert "models" in data
    models = {m["name"]: m for m in data["models"]}

    # gold_icd9_clinical_index
    assert "gold_icd9_clinical_index" in models
    index_cols = {c["name"]: c for c in models["gold_icd9_clinical_index"].get("columns", [])}
    assert "formatted_icd9_code" in index_cols
    assert "not_null" in index_cols["formatted_icd9_code"].get("tests", [])
    assert "unique" in index_cols["formatted_icd9_code"].get("tests", [])
    assert "long_description" in index_cols
    assert "not_null" in index_cols["long_description"].get("tests", [])

    # gold_icd9_to_10_crosswalk_stub
    assert "gold_icd9_to_10_crosswalk_stub" in models
    crosswalk_cols = {c["name"]: c for c in models["gold_icd9_to_10_crosswalk_stub"].get("columns", [])}
    assert "formatted_icd9_code" in crosswalk_cols
    assert "not_null" in crosswalk_cols["formatted_icd9_code"].get("tests", [])
    assert "target_icd10_code" in crosswalk_cols
    assert "map_type_flag" in crosswalk_cols
