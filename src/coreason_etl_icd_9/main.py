import os
import subprocess
import sys
from pathlib import Path

from coreason_etl_icd_9.pipeline import (
    generate_bronze_ingestion_manifold,
    initialize_ingestion_topology,
)
from coreason_etl_icd_9.utils.logger import logger

def run_dbt_command(command: list[str], cwd: Path) -> None:
    logger.info(f"Executing dbt command: {' '.join(command)}")
    
    # Ensure dbt uses the profiles.yml located in the current directory
    env = os.environ.copy()
    env["DBT_PROFILES_DIR"] = str(cwd)
    
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            env=env,
            check=True,
            capture_output=True,
            text=True,
        )
        logger.info(f"dbt command succeeded\n{result.stdout}")
    except subprocess.CalledProcessError as e:
        logger.error(f"dbt command failed\nError: {e.stderr}\nOutput: {e.stdout}")
        raise

def run_pipeline() -> None:
    logger.info("Starting ICD-9 ETL Pipeline orchestration")

    # 1. Ingestion Phase (dlt)
    try:
        logger.info("Initializing dlt pipeline topology")
        pipeline = initialize_ingestion_topology()

        logger.info("Executing Bronze layer ingestion manifold")
        pipeline.run(generate_bronze_ingestion_manifold())
        logger.info("dlt ingestion completed successfully")
    except Exception:
        logger.exception("dlt ingestion failed. Halting pipeline execution.")
        sys.exit(1)

    # 2. Transformation Phase (dbt)
    dbt_project_dir = Path(__file__).parent / "dbt"
    logger.info(f"Starting dbt transformation phase in {dbt_project_dir}")

    try:
        # Removed redundant --project-dir flag
        run_dbt_command(["dbt", "deps"], cwd=dbt_project_dir)
        run_dbt_command(["dbt", "run"], cwd=dbt_project_dir)
        run_dbt_command(["dbt", "test"], cwd=dbt_project_dir)
        logger.info("dbt transformation phase completed successfully")
    except Exception:
        logger.exception("dbt transformation phase failed.")
        sys.exit(1)

    logger.info("ICD-9 ETL Pipeline completed successfully")

if __name__ == "__main__":
    run_pipeline()
