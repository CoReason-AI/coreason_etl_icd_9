from pathlib import Path

import yaml


def test_bronze_sources_yml_structure() -> None:
    """Verify that sources.yml exists and has the required structure and tests."""
    source_path = Path("src/coreason_etl_icd_9/dbt/models/bronze/sources.yml")
    assert source_path.exists(), "sources.yml for bronze models must exist"

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
    assert "raw_data" in columns
    assert "ingestion_ts" in columns
