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
AGENT INSTRUCTION: This module provides comprehensive unit tests for the ICD9ConfigManifest.
"""

import os
import pathlib
from unittest import mock
from uuid import UUID

import pytest
from pydantic import ValidationError

from coreason_etl_icd_9.config import NAMESPACE_ICD9, ICD9ConfigManifest


def test_icd9_config_manifest_defaults(tmp_path: pathlib.Path) -> None:
    """Test that the default configuration values are properly applied."""
    # We use tmp_path to mock the default env var to avoid hitting real filesystem
    default_file = tmp_path / "ICD-9-CM-v32-master-descriptions.zip"
    default_file.touch()

    with mock.patch.dict(os.environ, {"ICD9_CMS_ZIP_PATH": str(default_file)}):
        config = ICD9ConfigManifest()
        assert str(config.cms_zip_path) == str(default_file)
        assert config.namespace_uuid == NAMESPACE_ICD9
        assert isinstance(config.namespace_uuid, UUID)


def test_icd9_config_manifest_env_override(tmp_path: pathlib.Path) -> None:
    """Test that the environment variables successfully override the defaults."""
    custom_file = tmp_path / "custom.zip"
    custom_file.touch()

    custom_uuid = "123e4567-e89b-12d3-a456-426614174000"

    with mock.patch.dict(os.environ, {"ICD9_CMS_ZIP_PATH": str(custom_file), "ICD9_NAMESPACE_UUID": custom_uuid}):
        config = ICD9ConfigManifest()
        assert str(config.cms_zip_path) == str(custom_file)
        assert config.namespace_uuid == UUID(custom_uuid)


def test_icd9_config_manifest_invalid_path() -> None:
    """Test that providing an invalid path throws a ValidationError."""
    invalid_path = "not-a-valid-path.zip"

    with mock.patch.dict(os.environ, {"ICD9_CMS_ZIP_PATH": invalid_path}):
        with pytest.raises(ValidationError) as exc_info:
            ICD9ConfigManifest()
        assert "cms_zip_path" in str(exc_info.value)


def test_icd9_config_manifest_invalid_uuid() -> None:
    """Test that providing an invalid UUID throws a ValidationError."""
    invalid_uuid = "not-a-valid-uuid"

    with mock.patch.dict(os.environ, {"ICD9_NAMESPACE_UUID": invalid_uuid}):
        with pytest.raises(ValidationError) as exc_info:
            ICD9ConfigManifest()
        assert "namespace_uuid" in str(exc_info.value)


def test_icd9_config_manifest_namespace_constant() -> None:
    """Test that the NAMESPACE_ICD9 constant matches the expected structure."""
    assert isinstance(NAMESPACE_ICD9, UUID)
    assert str(NAMESPACE_ICD9) == "a7cffe80-da93-4ef3-8bf2-e6ea241d7ee2"
