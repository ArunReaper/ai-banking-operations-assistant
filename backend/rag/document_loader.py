import re
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DOCUMENTS_DIR = PROJECT_ROOT / "data" / "documents"


def extract_metadata(content: str, source: str) -> dict[str, str]:
    """Extract document metadata from the Markdown header."""

    metadata = {
        "source": source,
        "title": "",
        "document_id": "",
        "version": "",
        "document_type": "",
        "effective_date": "",
    }

    title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)

    if title_match:
        metadata["title"] = title_match.group(1).strip()

    field_mapping = {
        "Document ID": "document_id",
        "Version": "version",
        "Document Type": "document_type",
        "Effective Date": "effective_date",
    }

    for label, key in field_mapping.items():
        match = re.search(
            rf"^{re.escape(label)}:\s*(.+)$",
            content,
            re.MULTILINE,
        )

        if match:
            metadata[key] = match.group(1).strip()

    return metadata


def load_markdown_documents(
        documents_dir: Path = DEFAULT_DOCUMENTS_DIR,
) -> list[dict[str, Any]]:
    """Load Markdown documents and their metadata."""

    if not documents_dir.exists():
        raise FileNotFoundError(
            f"Documents directory does not exist: {documents_dir}"
        )

    documents = []

    for file_path in sorted(documents_dir.glob("*.md")):
        content = file_path.read_text(encoding="utf-8").strip()

        if not content:
            continue

        metadata = extract_metadata(content, file_path.name)

        documents.append(
            {
                "content": content,
                "metadata": metadata,
            }
        )

    return documents