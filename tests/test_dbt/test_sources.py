from pathlib import Path

import yaml


def test_staging_sources_yml_structure() -> None:
    """Verify that sources.yml exists and has the required structure and tests."""
    source_path = Path("src/coreason_etl_icd_9/dbt/models/staging/sources.yml")
    assert source_path.exists(), "sources.yml for staging models must exist"

    with open(source_path) as f:
        data = yaml.safe_load(f)

    assert "sources" in data
    sources = {s["name"]: s for s in data["sources"]}

    # Check bronze source
    assert "bronze" in sources
    source = sources["bronze"]

    tables = {t["name"]: t for t in source.get("tables", [])}

    # Check icd9_cm_raw
    assert "icd9_cm_raw" in tables
    table = tables["icd9_cm_raw"]

    columns = {c["name"]: c for c in table.get("columns", [])}

    # Check specific fields and tests as per source file
    assert "code_type" in columns
    code_type_tests = columns["code_type"].get("tests", [])
    assert "not_null" in code_type_tests
    accepted = [t for t in code_type_tests if isinstance(t, dict) and "accepted_values" in t]
    assert len(accepted) == 1
    assert set(accepted[0]["accepted_values"]["values"]) == {"Diagnosis", "Procedure"}

    assert "raw_data" in columns
    assert "not_null" in columns["raw_data"].get("tests", [])

    assert "_dlt_load_id" in columns
    assert "_dlt_id" in columns
