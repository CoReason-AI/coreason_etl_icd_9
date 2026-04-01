import zipfile
from collections.abc import Iterator
from typing import Any

import dlt

from coreason_etl_icd_9.config import ICD9ConfigManifest
from coreason_etl_icd_9.extractor import fetch_and_extract_zip, parse_omop_concept_file
from coreason_etl_icd_9.utils.logger import logger

@dlt.resource(name="icd9_cm_raw", write_disposition="replace", max_table_nesting=0)
def generate_bronze_ingestion_manifold() -> Iterator[dict[str, Any]]:
    logger.info("Starting Bronze layer ingestion manifold for OMOP ICD-9")

    config = ICD9ConfigManifest()
    path = config.cms_zip_path

    try:
        archive = fetch_and_extract_zip(path)
        # Process the main OMOP concepts file
        yield from parse_omop_concept_file(archive, "CONCEPT.csv")
        logger.info("Successfully yielded all OMOP codes for Bronze layer ingestion")
    except zipfile.BadZipFile as e:
        logger.exception("Failed to parse local file as a valid ZIP archive")
        raise e
    except Exception as e:
        logger.exception("Failed to execute Bronze layer ingestion manifold")
        raise e

def initialize_ingestion_topology() -> dlt.Pipeline:
    return dlt.pipeline(
        pipeline_name="coreason_etl_icd9",
        destination="postgres",
        dataset_name="bronze",
    )
