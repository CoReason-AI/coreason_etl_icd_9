import pathlib
import zipfile

import dlt
import pytest

from coreason_etl_icd_9.config import ICD9ConfigManifest
from coreason_etl_icd_9.pipeline import generate_bronze_ingestion_manifold, initialize_ingestion_topology


def _create_mock_zip(files_content: dict[str, str], path: pathlib.Path) -> None:
    """Helper to generate an in-memory ZIP file with given files and content."""
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
        for filename, content in files_content.items():
            archive.writestr(filename, content.encode("latin-1"))


def test_generate_bronze_ingestion_manifold_success(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # 01234 678...
    # CODE  DESCRIPTION
    mock_content_dx = "12345 Description DX 1\nV123  Description DX 2\n"

    mock_content_sg = "67890 Description SG 1\n"

    zip_path = tmp_path / "mock.zip"
    _create_mock_zip({"CMS32_DESC_LONG_DX.txt": mock_content_dx, "CMS32_DESC_LONG_SG.txt": mock_content_sg}, zip_path)

    config = ICD9ConfigManifest(cms_zip_path=zip_path)
    monkeypatch.setattr("coreason_etl_icd_9.pipeline.ICD9ConfigManifest", lambda: config)

    # We can iterate the resource directly
    resource = generate_bronze_ingestion_manifold()
    results = list(resource)

    assert len(results) == 3
    assert results[0]["code_type"] == "diagnosis"
    assert "ingestion_ts" in results[0]
    assert results[0]["raw_data"] == {"raw_code": "12345", "raw_description": "Description DX 1"}

    assert results[1]["code_type"] == "diagnosis"
    assert "ingestion_ts" in results[1]
    assert results[1]["raw_data"] == {"raw_code": "V123", "raw_description": "Description DX 2"}

    assert results[2]["code_type"] == "procedure"
    assert "ingestion_ts" in results[2]
    assert results[2]["raw_data"] == {"raw_code": "67890", "raw_description": "Description SG 1"}


def test_generate_bronze_ingestion_manifold_bad_zip(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    zip_path = tmp_path / "mock.zip"
    zip_path.write_bytes(b"bad zip content")

    config = ICD9ConfigManifest(cms_zip_path=zip_path)
    monkeypatch.setattr("coreason_etl_icd_9.pipeline.ICD9ConfigManifest", lambda: config)

    resource = generate_bronze_ingestion_manifold()

    with pytest.raises(Exception, match="File is not a zip file"):
        list(resource)


def test_generate_bronze_ingestion_manifold_generic_error(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Trigger a generic exception inside the manifold
    def mock_fetch(*_args: object, **_kwargs: object) -> zipfile.ZipFile:
        raise ValueError("Generic error")

    zip_path = tmp_path / "mock.zip"
    zip_path.touch()
    config = ICD9ConfigManifest(cms_zip_path=zip_path)
    monkeypatch.setattr("coreason_etl_icd_9.pipeline.ICD9ConfigManifest", lambda: config)
    monkeypatch.setattr("coreason_etl_icd_9.pipeline.fetch_and_extract_zip", mock_fetch)

    resource = generate_bronze_ingestion_manifold()

    with pytest.raises(Exception, match="Generic error"):
        list(resource)


def test_initialize_ingestion_topology() -> None:
    pipeline = initialize_ingestion_topology()
    assert isinstance(pipeline, dlt.Pipeline)
    assert pipeline.pipeline_name == "coreason_etl_icd9"
    assert pipeline.dataset_name == "bronze"


def test_pipeline_integration(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    mock_content_dx = "12345 Desc DX\n"
    mock_content_sg = "67890 Desc SG\n"

    zip_path = tmp_path / "mock.zip"
    _create_mock_zip({"CMS32_DESC_LONG_DX.txt": mock_content_dx, "CMS32_DESC_LONG_SG.txt": mock_content_sg}, zip_path)

    config = ICD9ConfigManifest(cms_zip_path=zip_path)
    monkeypatch.setattr("coreason_etl_icd_9.pipeline.ICD9ConfigManifest", lambda: config)

    # Test that dlt can extract it successfully. Using destination "dummy" throws timeouts, so we only test extraction.
    pipeline = dlt.pipeline(pipeline_name="test_pl", destination="dummy", dataset_name="bronze_test")

    # We can use the pipeline.extract() method directly to test the extraction step
    pipeline.extract(generate_bronze_ingestion_manifold())

    # Validate it created a package
    schema = pipeline.default_schema
    assert "icd9_cm_raw" in schema.tables
