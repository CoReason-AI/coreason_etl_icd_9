from pathlib import Path

import yaml


def test_dbt_profiles_structure() -> None:
    """Validates the dbt profiles.yml adheres to strict PG* environment variables requirements."""
    profiles_path = Path("src/coreason_etl_icd_9/dbt/profiles.yml")
    assert profiles_path.exists(), "profiles.yml is missing from the designated directory."

    with open(profiles_path) as f:
        content = f.read()
        # Filter out block comments manually (docstrings not valid in YAML)
        lines = []
        in_docstring = False
        for line in content.splitlines():
            if line.strip().startswith('"""'):
                in_docstring = not in_docstring
                continue
            if not in_docstring:
                lines.append(line)
        yaml_content = "\n".join(lines)
        profiles = yaml.safe_load(yaml_content)

    assert "coreason_etl_icd9" in profiles

    project_profile = profiles["coreason_etl_icd9"]
    assert project_profile["target"] == "dev"
    assert "outputs" in project_profile
    assert "dev" in project_profile["outputs"]

    dev_config = project_profile["outputs"]["dev"]
    assert dev_config["type"] == "postgres"

    # Verify environment variables logic is present
    assert "{{ env_var('PGHOST'" in dev_config["host"]
    assert "{{ env_var('PGPORT'" in dev_config["port"]
    assert "{{ env_var('PGUSER'" in dev_config["user"]
    assert "{{ env_var('PGPASSWORD'" in dev_config["password"]
    assert "{{ env_var('PGDATABASE'" in dev_config["dbname"]


def test_dbt_project_structure() -> None:
    """Validates the dbt_project.yml settings."""
    project_path = Path("src/coreason_etl_icd_9/dbt/dbt_project.yml")
    assert project_path.exists(), "dbt_project.yml is missing from the designated directory."

    with open(project_path) as f:
        content = f.read()
        # Filter out block comments manually (docstrings not valid in YAML)
        lines = []
        in_docstring = False
        for line in content.splitlines():
            if line.strip().startswith('"""'):
                in_docstring = not in_docstring
                continue
            if not in_docstring:
                lines.append(line)
        yaml_content = "\n".join(lines)
        project = yaml.safe_load(yaml_content)

    assert project["name"] == "coreason_etl_icd9"
    assert project["profile"] == "coreason_etl_icd9"
    assert "models" in project
    assert "coreason_etl_icd9" in project["models"]

    model_config = project["models"]["coreason_etl_icd9"]
    assert model_config["staging"]["+schema"] == "silver"
    assert model_config["marts"]["+schema"] == "gold"
