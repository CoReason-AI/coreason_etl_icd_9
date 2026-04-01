from typing import Final
from uuid import UUID
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Hardcoded base namespace UUIDv4 as a constant for identity resolution
NAMESPACE_ICD9: Final[UUID] = UUID("a7cffe80-da93-4ef3-8bf2-e6ea241d7ee2")

class ICD9ConfigManifest(BaseSettings):
    """Configuration for the ICD-9 pipeline parameters."""
    model_config = SettingsConfigDict(
        env_prefix="ICD9_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    cms_zip_path: Path = Field(
        default=Path("icd_9-data.zip"),
        description="The target local file path to the master ZIP archive."
    )

    namespace_uuid: UUID = Field(
        default=NAMESPACE_ICD9,
        description="The constant UUIDv4 used as the namespace for deterministic UUIDv5 identity resolution."
    )
