import pathlib
import zipfile
from datetime import UTC

import pytest
from pytest_mock import MockerFixture

from coreason_etl_icd_9.extractor import fetch_and_extract_zip, parse_fixed_width_file


def _create_mock_zip(files_content: dict[str, str], path: pathlib.Path) -> None:
    """Helper to generate an in-memory ZIP file with given files and content."""
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
        for filename, content in files_content.items():
            archive.writestr(filename, content.encode("latin-1"))


def test_fetch_and_extract_zip_success(tmp_path: pathlib.Path) -> None:
    zip_path = tmp_path / "mock.zip"
    _create_mock_zip({"test.txt": "dummy content"}, zip_path)

    archive = fetch_and_extract_zip(zip_path)
    assert isinstance(archive, zipfile.ZipFile)
    assert "test.txt" in archive.namelist()


def test_fetch_and_extract_zip_bad_zip(tmp_path: pathlib.Path) -> None:
    zip_path = tmp_path / "mock.zip"
    zip_path.write_bytes(b"this is not a zip file")

    with pytest.raises(zipfile.BadZipFile):
        fetch_and_extract_zip(zip_path)


def test_parse_fixed_width_file_success(mocker: MockerFixture, tmp_path: pathlib.Path) -> None:
    # 01234 678...
    # CODE  DESCRIPTION
    mock_content = (
        "12345 Description for 12345\n"
        "V123  Description for V123 \n"
        "E1234 Description for E1234\n"
        "\n"  # Empty line
        "  \n"  # Whitespace line
    )

    zip_path = tmp_path / "mock.zip"
    _create_mock_zip({"CMS32_DESC_LONG_DX.txt": mock_content}, zip_path)
    archive = zipfile.ZipFile(zip_path)

    from datetime import datetime, timezone

    mock_now = datetime(2023, 1, 1, tzinfo=UTC)
    mock_datetime = mocker.patch("coreason_etl_icd_9.extractor.datetime")
    mock_datetime.now.return_value = mock_now
    mock_datetime.timezone = timezone

    results = list(parse_fixed_width_file(archive, "CMS32_DESC_LONG_DX.txt", "Diagnosis"))

    assert len(results) == 3
    assert results[0] == {
        "code_type": "Diagnosis",
        "ingestion_ts": mock_now.isoformat(),
        "raw_data": {"raw_code": "12345", "raw_description": "Description for 12345"},
    }
    assert results[1] == {
        "code_type": "Diagnosis",
        "ingestion_ts": mock_now.isoformat(),
        "raw_data": {"raw_code": "V123", "raw_description": "Description for V123"},
    }
    assert results[2] == {
        "code_type": "Diagnosis",
        "ingestion_ts": mock_now.isoformat(),
        "raw_data": {"raw_code": "E1234", "raw_description": "Description for E1234"},
    }


def test_parse_fixed_width_file_empty_code(mocker: MockerFixture, tmp_path: pathlib.Path) -> None:
    mock_content = (
        "12345 Desc 1\n"
        "      Desc 2\n"  # Missing code
        "V123  Desc 3\n"
    )

    zip_path = tmp_path / "mock.zip"
    _create_mock_zip({"CMS32_DESC_LONG_DX.txt": mock_content}, zip_path)
    archive = zipfile.ZipFile(zip_path)

    from datetime import datetime, timezone

    mock_now = datetime(2023, 1, 1, tzinfo=UTC)
    mock_datetime = mocker.patch("coreason_etl_icd_9.extractor.datetime")
    mock_datetime.now.return_value = mock_now
    mock_datetime.timezone = timezone

    results = list(parse_fixed_width_file(archive, "CMS32_DESC_LONG_DX.txt", "Diagnosis"))

    assert len(results) == 2
    assert results[0]["raw_data"]["raw_code"] == "12345"
    assert results[0]["ingestion_ts"] == mock_now.isoformat()
    assert results[1]["raw_data"]["raw_code"] == "V123"
    assert results[1]["ingestion_ts"] == mock_now.isoformat()


def test_parse_fixed_width_file_missing_file(tmp_path: pathlib.Path) -> None:
    zip_path = tmp_path / "mock.zip"
    _create_mock_zip({"wrong_file.txt": "content"}, zip_path)
    archive = zipfile.ZipFile(zip_path)

    import re

    with pytest.raises(KeyError, match=re.escape("Missing expected file in ZIP: CMS32_DESC_LONG_SG.txt")):
        list(parse_fixed_width_file(archive, "CMS32_DESC_LONG_SG.txt", "Procedure"))
