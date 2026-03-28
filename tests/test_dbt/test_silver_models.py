import re
from pathlib import Path

import pytest
from jinja2 import Environment, FileSystemLoader


@pytest.fixture
def jinja_env() -> Environment:
    """Creates a Jinja2 environment configured to load dbt models and macros from the source directory."""
    models_dir = Path("src/coreason_etl_icd_9/dbt/models/silver")
    macros_dir = Path("src/coreason_etl_icd_9/dbt/macros")
    env = Environment(loader=FileSystemLoader([str(models_dir), str(macros_dir)]))

    # Mock dbt config, ref, and source functions
    env.globals['config'] = lambda **_kwargs: ""
    env.globals['source'] = lambda source_name, table_name: f"{source_name}.{table_name}"

    # Load the macro explicitly into the global context so templates can find it without dbt's context processor
    macro_template = env.get_template('format_icd9_code.sql')
    env.globals['format_icd9_code'] = macro_template.module.format_icd9_code # type: ignore

    return env


def normalize_sql(sql: str) -> str:
    """Helper to remove excess whitespace and newlines from compiled SQL for easy comparison."""
    return re.sub(r"\s+", " ", sql).strip()


def test_silver_icd9_ontology_model(jinja_env: Environment) -> None:
    """Verifies that the `silver_icd9_ontology` model generates the correct structural Postgres SQL."""

    template = jinja_env.get_template('silver_icd9_ontology.sql')

    compiled_sql = template.render()
    normalized_sql = normalize_sql(compiled_sql)

    # Verify Passthrough Bronze Columns exist in CTE
    assert "code_type, code_type AS domain_type, ingestion_ts, raw_data," in normalized_sql

    # Verify Source
    assert "FROM bronze.icd9_cm_raw" in normalized_sql

    # Verify JSON Extraction
    assert "TRIM(raw_data->>'raw_code') AS raw_code_string" in normalized_sql
    assert "TRIM(raw_data->>'raw_description') AS long_description" in normalized_sql

    # Verify UUID Generation
    uuid_logic = (
        "uuid_generate_v5( 'a7cffe80-da93-4ef3-8bf2-e6ea241d7ee2'::uuid, "
        "formatted_icd9_code || domain_type ) AS coreason_id"
    )
    assert uuid_logic in normalized_sql

    # Verify Final Select includes pass-through columns
    assert "domain_type, code_type, ingestion_ts, raw_data FROM formatted_silver" in normalized_sql
