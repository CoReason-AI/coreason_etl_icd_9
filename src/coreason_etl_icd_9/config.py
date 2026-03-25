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
AGENT INSTRUCTION: This module defines the strict configuration state for the ICD-9 ingestion pipeline.
"""

from typing import Final
from uuid import UUID

from pydantic import Field, HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

# Hardcoded base namespace UUIDv4 as a constant for identity resolution
NAMESPACE_ICD9: Final[UUID] = UUID("a7cffe80-da93-4ef3-8bf2-e6ea241d7ee2")


class ICD9ConfigManifest(BaseSettings):
    """
    Epistemic state configuration for the ICD-9 pipeline parameters.
    Handles environment variable overrides with hardcoded defaults.
    """

    model_config = SettingsConfigDict(
        env_prefix="ICD9_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    cms_zip_url: HttpUrl = Field(
        default=HttpUrl(
            "https://www.cms.gov/Medicare/Coding/ICD9ProviderDiagnosticCodes/Downloads/ICD-9-CM-v32-master-descriptions.zip"
        ),
        description="The target URL to download the CMS ICD-9 master ZIP file.",
    )

    namespace_uuid: UUID = Field(
        default=NAMESPACE_ICD9,
        description="The constant UUIDv4 used as the namespace for deterministic UUIDv5 identity resolution.",
    )
