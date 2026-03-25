# coreason_etl_icd_9

Legacy medical coding dataset utilized for historical health data pipelines

[![CI/CD](https://github.com/CoReason-AI/coreason_etl_icd_9/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/CoReason-AI/coreason_etl_icd_9/actions/workflows/ci-cd.yml)
[![PyPI](https://img.shields.io/pypi/v/coreason_etl_icd_9.svg)](https://pypi.org/project/coreason_etl_icd_9/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/coreason_etl_icd_9.svg)](https://pypi.org/project/coreason_etl_icd_9/)
[![License](https://img.shields.io/github/license/CoReason-AI/coreason_etl_icd_9)](https://github.com/CoReason-AI/coreason_etl_icd_9/blob/main/LICENSE)
[![Codecov](https://codecov.io/gh/CoReason-AI/coreason_etl_icd_9/branch/main/graph/badge.svg)](https://codecov.io/gh/CoReason-AI/coreason_etl_icd_9)
[![Downloads](https://static.pepy.tech/badge/coreason_etl_icd_9)](https://pepy.tech/project/coreason_etl_icd_9)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)

## Getting Started

### Prerequisites

- Python 3.14+
- uv

### Installation

1.  Clone the repository:
    ```sh
    git clone https://github.com/CoReason-AI/coreason_etl_icd_9.git
    cd coreason_etl_icd_9
    ```
2.  Install dependencies:
    ```sh
    uv sync --all-extras --dev
    ```

### Usage

-   Run the linter:
    ```sh
    uv run pre-commit run --all-files
    ```
-   Run the tests:
    ```sh
    uv run pytest
    ```
