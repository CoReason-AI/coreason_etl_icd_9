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
AGENT INSTRUCTION: This module provides comprehensive unit tests for the logging module.
"""

from unittest import mock


def test_logger_initialization() -> None:
    """Test that the logger initializes correctly and creates the logs directory."""
    with (
        mock.patch("coreason_etl_icd_9.utils.logger.Path.exists") as mock_exists,
        mock.patch("coreason_etl_icd_9.utils.logger.Path.mkdir") as mock_mkdir,
    ):
        mock_exists.return_value = False

        # We need to reload the module to trigger the `if not log_path.exists():` logic
        import importlib

        import coreason_etl_icd_9.utils.logger

        importlib.reload(coreason_etl_icd_9.utils.logger)

        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
