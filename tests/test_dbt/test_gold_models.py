import re
from pathlib import Path

import pytest
from jinja2 import Environment, FileSystemLoader


@pytest.fixture
def jinja_env() -> Environment:
    """Creates a Jinja2 environment configured to load Gold dbt models."""
    models_dir = Path("src/coreason_etl_icd_9/dbt/models/gold")
    env = Environment(loader=FileSystemLoader(str(models_dir)))

    # Mock dbt config and ref functions
    env.globals["config"] = lambda **_kwargs: ""
    env.globals["ref"] = lambda table_name: f"test_schema.{table_name}"

    return env


def normalize_sql(sql: str) -> str:
    """Helper to remove excess whitespace and newlines from compiled SQL for easy comparison."""
    return re.sub(r"\s+", " ", sql).strip()


def test_gold_icd9_clinical_index_model(jinja_env: Environment) -> None:
    """Verifies that the `gold_icd9_clinical_index` model selects all columns from Silver."""

    template = jinja_env.get_template("gold_icd9_clinical_index.sql")
    compiled_sql = template.render()
    normalized_sql = normalize_sql(compiled_sql)

    # Verify FROM ref
    assert "FROM test_schema.silver_icd9_ontology" in normalized_sql

    # Verify exact lineage columns are present
    assert "coreason_id," in normalized_sql
    assert "formatted_icd9_code," in normalized_sql
    assert "raw_code_string," in normalized_sql
    assert "long_description," in normalized_sql
    assert "domain_type," in normalized_sql
    assert "code_type," in normalized_sql
    assert "ingestion_ts," in normalized_sql
    assert "raw_data" in normalized_sql


def test_gold_icd9_to_10_crosswalk_stub_model(jinja_env: Environment) -> None:
    """Verifies that the `gold_icd9_to_10_crosswalk_stub` model selects all columns from Silver."""

    template = jinja_env.get_template("gold_icd9_to_10_crosswalk_stub.sql")
    compiled_sql = template.render()
    normalized_sql = normalize_sql(compiled_sql)

    # Verify FROM ref
    assert "FROM test_schema.silver_icd9_ontology" in normalized_sql

    # Verify exact lineage columns are present
    assert "coreason_id," in normalized_sql
    assert "formatted_icd9_code," in normalized_sql
    assert "raw_code_string," in normalized_sql
    assert "long_description," in normalized_sql
    assert "domain_type," in normalized_sql
    assert "code_type," in normalized_sql
    assert "ingestion_ts," in normalized_sql
    assert "raw_data" in normalized_sql
