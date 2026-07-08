import csv
import io
import zipfile
from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pydantic import FilePath

from coreason_etl_icd_9.utils.logger import logger

def fetch_and_extract_zip(path: FilePath | str | Path) -> zipfile.ZipFile:
    logger.info("Opening local OMOP Athena master ZIP", path=str(path))
    try:
        archive = zipfile.ZipFile(path)
        logger.info("Successfully loaded ZIP archive into memory", num_files=len(archive.namelist()))
        return archive
    except zipfile.BadZipFile as e:
        logger.error("Failed to parse local file as a valid ZIP archive", error=str(e))
        raise

def parse_omop_concept_file(archive: zipfile.ZipFile, filename: str) -> Iterator[dict[str, Any]]:
    """Defensively parses an OMOP Athena TSV file."""
    logger.info("Starting OMOP TSV parsing", filename=filename)

    if filename not in archive.namelist():
        logger.error("Target file not found in ZIP archive", filename=filename)
        raise KeyError(f"Missing expected file in ZIP: {filename}")

    with archive.open(filename, "r") as file_handle:
        # Athena OMOP files are utf-8 encoded TSVs
        text_stream = io.TextIOWrapper(file_handle, encoding="utf-8")
        reader = csv.DictReader(text_stream, delimiter='\t')

        ingestion_ts = datetime.now(UTC).isoformat()

        for line_number, row in enumerate(reader, start=1):
            vocab_id = row.get("vocabulary_id", "")
            
            # Filter to extract only ICD-9 CM and ICD-9 Proc codes
            if vocab_id not in ("ICD9CM", "ICD9Proc"):
                continue
            
            domain_type = "diagnosis" if vocab_id == "ICD9CM" else "procedure"
            raw_code = row.get("concept_code", "").strip()
            raw_description = row.get("concept_name", "").strip()

            if not raw_code:
                continue

            yield {
                "code_type": domain_type,
                "ingestion_ts": ingestion_ts,
                "raw_data": {"raw_code": raw_code, "raw_description": raw_description},
            }

    logger.info("Completed parsing of OMOP file", filename=filename)
