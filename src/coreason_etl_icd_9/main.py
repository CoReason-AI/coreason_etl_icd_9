# Copyright (c) 2026 CoReason, Inc.
#
# This software is proprietary and dual-licensed.
# Licensed under the Prosperity Public License 3.0 (the "License").
# A copy of the license is available at https://prosperitylicense.com/versions/3.0.0
# For details, see the LICENSE file.
# Commercial use beyond a 30-day trial requires a separate license.
#
# Source Code: https://github.com/CoReason-AI/coreason_etl_icd_9

"""
AGENT INSTRUCTION: This module is the main entry point to run the ICD-9 ETL Pipeline.
It orchestrates the 'dlt' ingestion and 'dbt' transformation phases.
"""

import subprocess
import sys
from pathlib import Path

from coreason_etl_icd_9.pipeline import (
    generate_bronze_ingestion_manifold,
    initialize_ingestion_topology,
)
from coreason_etl_icd_9.utils.logger import logger


def run_dbt_command(command: list[str], cwd: Path) -> None:
    """
    Executes a dbt command via subprocess in the specified directory.
    """
    logger.info("Executing dbt command", command=" ".join(command))
    try:
        result = subprocess.run(  # noqa: S603
            command,
            cwd=cwd,
            check=True,
            capture_output=True,
            text=True,
        )
        logger.info("dbt command succeeded", output=result.stdout)
    except subprocess.CalledProcessError as e:
        logger.error(
            "dbt command failed",
            command=" ".join(command),
            error=e.stderr,
            output=e.stdout,
        )
        raise


def run_pipeline() -> None:
    """
    Orchestrates the entire ICD-9 ETL pipeline.
    Executes the dlt ingestion first, then the dbt transformations.
    """
    logger.info("Starting ICD-9 ETL Pipeline orchestration")

    # 1. Ingestion Phase (dlt)
    try:
        logger.info("Initializing dlt pipeline topology")
        pipeline = initialize_ingestion_topology()

        logger.info("Executing Bronze layer ingestion manifold")
        # Run dlt ingestion
        pipeline.run(generate_bronze_ingestion_manifold())
        logger.info("dlt ingestion completed successfully")
    except Exception:
        logger.exception("dlt ingestion failed. Halting pipeline execution.")
        sys.exit(1)

    # 2. Transformation Phase (dbt)
    dbt_project_dir = Path(__file__).parent / "dbt"
    logger.info("Starting dbt transformation phase", dbt_project_dir=str(dbt_project_dir))

    try:
        base_cmd = ["dbt", "--project-dir", str(dbt_project_dir)]
        run_dbt_command([*base_cmd, "deps"], cwd=dbt_project_dir)
        run_dbt_command([*base_cmd, "run"], cwd=dbt_project_dir)
        run_dbt_command([*base_cmd, "test"], cwd=dbt_project_dir)
        logger.info("dbt transformation phase completed successfully")
    except Exception:
        logger.exception("dbt transformation phase failed.")
        sys.exit(1)

    logger.info("ICD-9 ETL Pipeline completed successfully")


if __name__ == "__main__":
    run_pipeline()  # pragma: no cover
