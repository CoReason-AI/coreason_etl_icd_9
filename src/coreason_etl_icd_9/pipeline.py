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
AGENT INSTRUCTION: This module provides the purely deterministic dlt ingestion pipeline
to extract the legacy ICD-9 fixed-width text files and load them into the Bronze layer.
"""

from collections.abc import Iterator
from typing import Any

import dlt
import requests

from coreason_etl_icd_9.config import ICD9ConfigManifest
from coreason_etl_icd_9.extractor import FILENAME_DX, FILENAME_SG, fetch_and_extract_zip, parse_fixed_width_file
from coreason_etl_icd_9.utils.logger import logger


@dlt.resource(name="icd9_cm_raw", write_disposition="replace", max_table_nesting=0)  # type: ignore[misc]
def generate_bronze_ingestion_manifold() -> Iterator[dict[str, Any]]:
    """
    Epistemic state ingestion intent for the ICD-9 raw codes.
    Downloads the CMS master ZIP archive, parses both Diagnosis (DX) and Procedure (SG)
    fixed-width text files, and yields normalized records to a dlt pipeline.
    """
    logger.info("Starting Bronze layer ingestion manifold for ICD-9")

    config = ICD9ConfigManifest()
    url = config.cms_zip_url

    try:
        archive = fetch_and_extract_zip(url)

        # Process Diagnosis Codes
        yield from parse_fixed_width_file(archive, FILENAME_DX, "Diagnosis")

        # Process Procedure Codes
        yield from parse_fixed_width_file(archive, FILENAME_SG, "Procedure")

        logger.info("Successfully yielded all DX and SG codes for Bronze layer ingestion")
    except requests.exceptions.HTTPError as e:
        logger.exception("Failed to execute Bronze layer ingestion manifold due to HTTP error")
        raise e
    except Exception as e:
        logger.exception("Failed to execute Bronze layer ingestion manifold")
        raise e


def initialize_ingestion_topology() -> dlt.Pipeline:
    """
    Configures and returns the dlt pipeline for the coreason_etl_icd9 project.
    """
    return dlt.pipeline(
        pipeline_name="coreason_etl_icd9",
        destination="postgres",
        dataset_name="bronze",
    )
