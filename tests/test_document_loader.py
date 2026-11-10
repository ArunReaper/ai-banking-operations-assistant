from pathlib import Path

import pytest
from backend.rag.document_loader import (
    extract_metadata,
    load_markdown_documents,
)


def test_extract_metadata():
    content = """# Synthetic SOP: IMPS Failure Handling

Document ID: SOP-IMPS-001
Version: 1.0
Document Type: Demonstration SOP
Effective Date: 2026-11-01

Some document content.
"""

    metadata = extract_metadata(content, "imps.md")

    assert metadata["title"] == "Synthetic SOP: IMPS Failure Handling"
    assert metadata["document_id"] == "SOP-IMPS-001"
    assert metadata["version"] == "1.0"
    assert metadata["document_type"] == "Demonstration SOP"
    assert metadata["effective_date"] == "2026-11-01"
    assert metadata["source"] == "imps.md"


def test_load_markdown_documents(tmp_path: Path):
    document = tmp_path / "sample.md"
    document.write_text(
        "# Sample SOP\n\nDocument ID: SOP-001\n\nSample content.",
        encoding="utf-8",
    )

    documents = load_markdown_documents(tmp_path)

    assert len(documents) == 1
    assert documents[0]["metadata"]["document_id"] == "SOP-001"
    assert "Sample content." in documents[0]["content"]


def test_load_documents_skips_empty_files(tmp_path: Path):
    (tmp_path / "empty.md").write_text("", encoding="utf-8")

    documents = load_markdown_documents(tmp_path)

    assert documents == []


def test_load_documents_missing_directory():
    with pytest.raises(FileNotFoundError):
        load_markdown_documents(Path("/nonexistent/documents"))