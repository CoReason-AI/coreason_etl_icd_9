from pathlib import Path

import jinja2


def test_gold_clinical_index_compilation() -> None:
    """Test that the gold_icd9_clinical_index model compiles to expected SQL structure."""
    model_path = Path("src/coreason_etl_icd_9/dbt/models/marts/gold_icd9_clinical_index.sql")

    with open(model_path) as f:
        template_str = f.read()

    def mock_ref(model_name: str) -> str:
        return f"mock_{model_name}"

    env = jinja2.Environment()
    env.globals["ref"] = mock_ref

    template = env.from_string(template_str)
    rendered = template.render()
    sql = " ".join(rendered.split())

    # Verify key CTEs and column logic
    assert "select formatted_icd9_code, long_description, ingestion_ts" in sql
    assert "from mock_silver_icd9_ontology" in sql


def test_gold_crosswalk_stub_compilation() -> None:
    """Test that the gold_icd9_to_10_crosswalk_stub model compiles to expected SQL structure."""
    model_path = Path("src/coreason_etl_icd_9/dbt/models/marts/gold_icd9_to_10_crosswalk_stub.sql")

    with open(model_path) as f:
        template_str = f.read()

    def mock_ref(model_name: str) -> str:
        return f"mock_{model_name}"

    env = jinja2.Environment()
    env.globals["ref"] = mock_ref

    template = env.from_string(template_str)
    rendered = template.render()
    sql = " ".join(rendered.split())

    # Verify key CTEs and column logic
    assert "select formatted_icd9_code," in sql
    assert "cast(null as varchar(20)) as target_icd10_code," in sql
    assert "cast(null as varchar(255)) as map_type_flag," in sql
    assert "ingestion_ts" in sql
    assert "from mock_silver_icd9_ontology" in sql
