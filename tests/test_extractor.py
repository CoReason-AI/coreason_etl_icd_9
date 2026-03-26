import io
import zipfile

import pytest
import requests
import requests_mock

from coreason_etl_icd_9.extractor import FILENAME_DX, FILENAME_SG, fetch_and_extract_zip, parse_fixed_width_file


def _create_mock_zip(files_content: dict[str, str]) -> io.BytesIO:
    """Helper to generate an in-memory ZIP file with given files and content."""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        for filename, content in files_content.items():
            archive.writestr(filename, content.encode("latin-1"))
    buffer.seek(0)
    return buffer


def test_fetch_and_extract_zip_success(requests_mock: requests_mock.Mocker) -> None:
    url = "https://example.com/mock.zip"
    mock_zip_buffer = _create_mock_zip({"test.txt": "dummy content"})

    requests_mock.get(url, content=mock_zip_buffer.read())

    archive = fetch_and_extract_zip(url)
    assert isinstance(archive, zipfile.ZipFile)
    assert "test.txt" in archive.namelist()


def test_fetch_and_extract_zip_http_error(requests_mock: requests_mock.Mocker) -> None:
    url = "https://example.com/mock.zip"
    requests_mock.get(url, status_code=404)

    with pytest.raises(requests.HTTPError):
        fetch_and_extract_zip(url)


def test_fetch_and_extract_zip_bad_zip(requests_mock: requests_mock.Mocker) -> None:
    url = "https://example.com/mock.zip"
    requests_mock.get(url, content=b"this is not a zip file")

    with pytest.raises(zipfile.BadZipFile):
        fetch_and_extract_zip(url)


def test_parse_fixed_width_file_success() -> None:
    # 01234 678...
    # CODE  DESCRIPTION
    mock_content = (
        "12345 Description for 12345\n"
        "V123  Description for V123 \n"
        "E1234 Description for E1234\n"
        "\n"  # Empty line
        "  \n"  # Whitespace line
    )

    zip_buffer = _create_mock_zip({FILENAME_DX: mock_content})
    archive = zipfile.ZipFile(zip_buffer)

    results = list(parse_fixed_width_file(archive, FILENAME_DX, "Diagnosis"))

    assert len(results) == 3
    assert results[0] == {
        "code_type": "Diagnosis",
        "raw_data": {"raw_code": "12345", "raw_description": "Description for 12345"},
    }
    assert results[1] == {
        "code_type": "Diagnosis",
        "raw_data": {"raw_code": "V123", "raw_description": "Description for V123"},
    }
    assert results[2] == {
        "code_type": "Diagnosis",
        "raw_data": {"raw_code": "E1234", "raw_description": "Description for E1234"},
    }


def test_parse_fixed_width_file_empty_code() -> None:
    mock_content = (
        "12345 Desc 1\n"
        "      Desc 2\n"  # Missing code
        "V123  Desc 3\n"
    )

    zip_buffer = _create_mock_zip({FILENAME_DX: mock_content})
    archive = zipfile.ZipFile(zip_buffer)

    results = list(parse_fixed_width_file(archive, FILENAME_DX, "Diagnosis"))

    assert len(results) == 2
    assert results[0]["raw_data"]["raw_code"] == "12345"
    assert results[1]["raw_data"]["raw_code"] == "V123"


def test_parse_fixed_width_file_missing_file() -> None:
    zip_buffer = _create_mock_zip({"wrong_file.txt": "content"})
    archive = zipfile.ZipFile(zip_buffer)

    with pytest.raises(KeyError, match=f"Missing expected file in ZIP: {FILENAME_SG}"):
        list(parse_fixed_width_file(archive, FILENAME_SG, "Procedure"))
