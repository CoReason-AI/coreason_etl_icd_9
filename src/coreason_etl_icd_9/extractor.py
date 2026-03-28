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
AGENT INSTRUCTION: This module provides the purely deterministic, in-memory extraction
and defensive parsing logic for legacy ICD-9 fixed-width text files.
"""

import io
import zipfile
from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pydantic import FilePath

from coreason_etl_icd_9.utils.logger import logger


def fetch_and_extract_zip(path: FilePath | str | Path) -> zipfile.ZipFile:
    """
    Opens the CMS ZIP file from the local filesystem and returns the opened ZipFile object.

    Args:
        path: The exact local path to the ZIP archive.

    Returns:
        A loaded `zipfile.ZipFile` instance containing the extracted text documents.

    Raises:
        zipfile.BadZipFile: If the file cannot be parsed as a valid ZIP archive.
    """
    logger.info("Opening local ICD-9 master ZIP", path=str(path))

    try:
        archive = zipfile.ZipFile(path)
        logger.info("Successfully loaded ZIP archive into memory", num_files=len(archive.namelist()))
        return archive
    except zipfile.BadZipFile as e:
        logger.error("Failed to parse local file as a valid ZIP archive", error=str(e))
        raise


def parse_fixed_width_file(archive: zipfile.ZipFile, filename: str, domain_type: str) -> Iterator[dict[str, Any]]:
    """
    Defensively parses a fixed-width ICD-9 text file from within an open ZIP archive.

    The legacy format requires strict string slicing:
    - Characters 0-4 (inclusive): Raw code (with implicit, missing decimal).
    - Character 5: Whitespace delimiter (defensively stripped).
    - Characters 6+: Long clinical description.

    Args:
        archive: The `zipfile.ZipFile` containing the CMS resources.
        filename: The exact path of the text file inside the ZIP.
        domain_type: The categorical flag ('Diagnosis' or 'Procedure') assigned to `code_type`.

    Yields:
        A `Dict` containing the normalized Bronze layer JSONB structure.

    Raises:
        KeyError: If the requested filename is not present within the archive.
    """
    logger.info("Starting fixed-width defensive parsing", filename=filename, domain_type=domain_type)

    if filename not in archive.namelist():
        logger.error("Target file not found in ZIP archive", filename=filename)
        raise KeyError(f"Missing expected file in ZIP: {filename}")

    with archive.open(filename, "r") as file_handle:
        # Wrap bytes in a TextIOWrapper for standard Python string iteration
        # (CMS uses varied encodings, latin-1 is safest for legacy text)
        text_stream = io.TextIOWrapper(file_handle, encoding="latin-1")

        # Capture ingestion time for the current file parsing
        ingestion_ts = datetime.now(UTC).isoformat()

        for line_number, raw_line in enumerate(text_stream, start=1):
            # Skip empty lines, typical of EOF or legacy anomalies
            if not raw_line.strip():
                continue

            # Defensive fixed-width slicing based on absolute index (do not strip line first)
            raw_code = raw_line[:5].strip()
            raw_description = raw_line[6:].strip()

            if not raw_code:
                logger.warning("Empty raw code identified during parsing; skipping line", line_number=line_number)
                continue

            yield {
                "code_type": domain_type,
                "ingestion_ts": ingestion_ts,
                "raw_data": {"raw_code": raw_code, "raw_description": raw_description},
            }

    logger.info("Completed parsing of fixed-width file", filename=filename, domain_type=domain_type)
