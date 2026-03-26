from pathlib import Path

import yaml


def test_dbt_sources_structure() -> None:
    """Validates the dbt sources.yml correctly maps to the bronze schema."""
    sources_path = Path("src/coreason_etl_icd_9/dbt/models/staging/sources.yml")
    assert sources_path.exists(), "sources.yml is missing from the designated staging directory."

    with open(sources_path) as f:
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
        sources_doc = yaml.safe_load(yaml_content)

    assert "sources" in sources_doc
    sources = sources_doc["sources"]
    assert len(sources) == 1

    bronze_source = sources[0]
    assert bronze_source["name"] == "bronze"
    assert bronze_source["schema"] == "bronze"

    assert "tables" in bronze_source
    tables = bronze_source["tables"]
    assert len(tables) == 1

    icd9_table = tables[0]
    assert icd9_table["name"] == "icd9_cm_raw"

    columns = {col["name"]: col for col in icd9_table["columns"]}
    assert "code_type" in columns
    assert "raw_data" in columns

    code_type_col = columns["code_type"]
    assert "tests" in code_type_col
    assert "not_null" in code_type_col["tests"]

    accepted_values_test = None
    for test in code_type_col["tests"]:
        if isinstance(test, dict) and "accepted_values" in test:
            accepted_values_test = test["accepted_values"]
            break

    assert accepted_values_test is not None
    assert "Diagnosis" in accepted_values_test["values"]
    assert "Procedure" in accepted_values_test["values"]
