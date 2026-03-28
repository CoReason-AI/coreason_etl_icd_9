# Copyright (c) 2026 CoReason, Inc.
#
# This software is proprietary and dual-licensed.
# Licensed under the Prosperity Public License 3.0 (the "License").
# A copy of the license is available at https://prosperitylicense.com/versions/3.0.0
# For details, see the LICENSE file.
# Commercial use beyond a 30-day trial requires a separate license.
#
# Source Code: https://github.com/CoReason-AI/coreason_etl_icd_9

import subprocess
import sys
from collections.abc import Iterator
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from coreason_etl_icd_9.main import run_dbt_command, run_pipeline

@pytest.fixture
def mock_subprocess_run() -> Iterator[MagicMock]:
    with patch("subprocess.run") as mock_run:
        yield mock_run

@pytest.fixture
def mock_initialize_ingestion_topology() -> Iterator[tuple[MagicMock, MagicMock]]:
    with patch("coreason_etl_icd_9.main.initialize_ingestion_topology") as mock_init:
        mock_pipeline = MagicMock()
        mock_init.return_value = mock_pipeline
        yield mock_init, mock_pipeline

@pytest.fixture
def mock_generate_bronze_ingestion_manifold() -> Iterator[MagicMock]:
    with patch("coreason_etl_icd_9.main.generate_bronze_ingestion_manifold") as mock_gen:
        mock_gen.return_value = [{"dummy": "data"}]
        yield mock_gen

@pytest.fixture
def mock_sys_exit() -> Iterator[MagicMock]:
    with patch("sys.exit") as mock_exit:
        yield mock_exit

def test_run_dbt_command_success(mock_subprocess_run: MagicMock) -> None:
    mock_subprocess_run.return_value = MagicMock(stdout="Success output")
    run_dbt_command(["dbt", "run"], cwd=Path("/opt/test"))
    mock_subprocess_run.assert_called_once_with(
        ["dbt", "run"],
        cwd=Path("/opt/test"),
        check=True,
        capture_output=True,
        text=True,
    )

def test_run_dbt_command_failure(mock_subprocess_run: MagicMock) -> None:
    mock_subprocess_run.side_effect = subprocess.CalledProcessError(
        returncode=1, cmd=["dbt", "run"], output="output", stderr="error"
    )
    with pytest.raises(subprocess.CalledProcessError):
        run_dbt_command(["dbt", "run"], cwd=Path("/opt/test"))

def test_run_pipeline_success(
    mock_subprocess_run: MagicMock,
    mock_initialize_ingestion_topology: tuple[MagicMock, MagicMock],
    mock_generate_bronze_ingestion_manifold: MagicMock,
    mock_sys_exit: MagicMock,
) -> None:
    mock_subprocess_run.return_value = MagicMock(stdout="Success output")
    _, mock_pipeline = mock_initialize_ingestion_topology
    mock_pipeline.run.return_value = None

    run_pipeline()

    # Verify dlt was run
    mock_pipeline.run.assert_called_once()
    mock_generate_bronze_ingestion_manifold.assert_called_once()

    # Verify dbt was run
    assert mock_subprocess_run.call_count == 3

    calls = mock_subprocess_run.call_args_list
    assert calls[0].args[0][-1] == "deps"
    assert calls[1].args[0][-1] == "run"
    assert calls[2].args[0][-1] == "test"

    mock_sys_exit.assert_not_called()

def test_run_pipeline_dlt_failure(
    mock_subprocess_run: MagicMock,
    mock_initialize_ingestion_topology: tuple[MagicMock, MagicMock],
    mock_sys_exit: MagicMock,
) -> None:
    _, mock_pipeline = mock_initialize_ingestion_topology
    mock_pipeline.run.side_effect = Exception("dlt failed")
    mock_sys_exit.side_effect = SystemExit(1)

    with pytest.raises(SystemExit) as exc_info:
        run_pipeline()

    assert exc_info.value.code == 1
    mock_sys_exit.assert_called_once_with(1)
    mock_subprocess_run.assert_not_called()

def test_run_pipeline_dbt_failure(
    mock_subprocess_run: MagicMock,
    mock_initialize_ingestion_topology: tuple[MagicMock, MagicMock],
    mock_sys_exit: MagicMock,
) -> None:
    _, mock_pipeline = mock_initialize_ingestion_topology
    mock_pipeline.run.return_value = None
    mock_sys_exit.side_effect = SystemExit(1)

    mock_subprocess_run.side_effect = subprocess.CalledProcessError(
        returncode=1, cmd=["dbt", "run"], output="output", stderr="error"
    )

    with pytest.raises(SystemExit) as exc_info:
        run_pipeline()

    assert exc_info.value.code == 1
    mock_sys_exit.assert_called_once_with(1)
    assert mock_subprocess_run.call_count == 1  # Fails on the first dbt command (deps)

def test_main_block(
    mock_subprocess_run: MagicMock,
    mock_initialize_ingestion_topology: tuple[MagicMock, MagicMock],
    mock_generate_bronze_ingestion_manifold: MagicMock,
) -> None:
    """Tests the standalone module execution."""
    import coreason_etl_icd_9.main
    with patch.object(coreason_etl_icd_9.main, "run_pipeline") as mock_run:
        # Load the content
        with open(coreason_etl_icd_9.main.__file__) as f:
            code_text = f.read()

        # Find the main block lines to execute in a controlled mocked environment
        block_lines = []
        in_block = False
        for line in code_text.splitlines():
            if line.startswith('if __name__ == "__main__":'):
                in_block = True
            if in_block:
                block_lines.append(line)

        # Replace the function call with mock
        modified_block = "\n".join(block_lines).replace("run_pipeline()", "mock_run()")

        # Provide a safe namespace
        namespace = {
            "__name__": "__main__",
            "mock_run": mock_run
        }

        exec(modified_block, namespace)
        mock_run.assert_called_once()
