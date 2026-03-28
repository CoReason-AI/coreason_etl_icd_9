import io
import zipfile

import dlt
import pytest
import requests_mock

from coreason_etl_icd_9.config import ICD9ConfigManifest
from coreason_etl_icd_9.extractor import FILENAME_DX, FILENAME_SG
from coreason_etl_icd_9.pipeline import generate_bronze_ingestion_manifold, initialize_ingestion_topology


def _create_mock_zip(files_content: dict[str, str]) -> io.BytesIO:
    """Helper to generate an in-memory ZIP file with given files and content."""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        for filename, content in files_content.items():
            archive.writestr(filename, content.encode("latin-1"))
    buffer.seek(0)
    return buffer


def test_generate_bronze_ingestion_manifold_success(requests_mock: requests_mock.Mocker) -> None:
    # 01234 678...
    # CODE  DESCRIPTION
    mock_content_dx = "12345 Description DX 1\nV123  Description DX 2\n"

    mock_content_sg = "67890 Description SG 1\n"

    zip_buffer = _create_mock_zip({FILENAME_DX: mock_content_dx, FILENAME_SG: mock_content_sg})

    config = ICD9ConfigManifest()
    requests_mock.get(str(config.cms_zip_url), content=zip_buffer.read())

    # We can iterate the resource directly
    resource = generate_bronze_ingestion_manifold()
    results = list(resource)

    assert len(results) == 3
    assert results[0]["code_type"] == "Diagnosis"
    assert "ingestion_ts" in results[0]
    assert results[0]["raw_data"] == {"raw_code": "12345", "raw_description": "Description DX 1"}

    assert results[1]["code_type"] == "Diagnosis"
    assert "ingestion_ts" in results[1]
    assert results[1]["raw_data"] == {"raw_code": "V123", "raw_description": "Description DX 2"}

    assert results[2]["code_type"] == "Procedure"
    assert "ingestion_ts" in results[2]
    assert results[2]["raw_data"] == {"raw_code": "67890", "raw_description": "Description SG 1"}


def test_generate_bronze_ingestion_manifold_http_error(requests_mock: requests_mock.Mocker) -> None:
    config = ICD9ConfigManifest()
    requests_mock.get(str(config.cms_zip_url), status_code=500)

    resource = generate_bronze_ingestion_manifold()

    with pytest.raises(Exception, match="500 Server Error"):
        list(resource)


def test_generate_bronze_ingestion_manifold_generic_error(monkeypatch: pytest.MonkeyPatch) -> None:
    # Trigger a generic exception inside the manifold
    def mock_fetch(*_args: object, **_kwargs: object) -> zipfile.ZipFile:
        raise ValueError("Generic error")

    monkeypatch.setattr("coreason_etl_icd_9.pipeline.fetch_and_extract_zip", mock_fetch)

    resource = generate_bronze_ingestion_manifold()

    with pytest.raises(Exception, match="Generic error"):
        list(resource)


def test_initialize_ingestion_topology() -> None:
    pipeline = initialize_ingestion_topology()
    assert isinstance(pipeline, dlt.Pipeline)
    assert pipeline.pipeline_name == "coreason_etl_icd9"
    assert pipeline.dataset_name == "bronze"


def test_pipeline_integration(requests_mock: requests_mock.Mocker) -> None:
    mock_content_dx = "12345 Desc DX\n"
    mock_content_sg = "67890 Desc SG\n"
    zip_buffer = _create_mock_zip({FILENAME_DX: mock_content_dx, FILENAME_SG: mock_content_sg})

    config = ICD9ConfigManifest()
    requests_mock.get(str(config.cms_zip_url), content=zip_buffer.read())

    # Test that dlt can extract it successfully. Using destination "dummy" throws timeouts, so we only test extraction.
    pipeline = dlt.pipeline(pipeline_name="test_pl", destination="dummy", dataset_name="bronze_test")

    # We can use the pipeline.extract() method directly to test the extraction step
    pipeline.extract(generate_bronze_ingestion_manifold())

    # Validate it created a package
    schema = pipeline.default_schema
    assert "icd9_cm_raw" in schema.tables
