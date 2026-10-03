"""Read policy documents (.txt, .md, .pdf) from a folder."""
from pathlib import Path

from pypdf import PdfReader

from src import config

SUPPORTED = {".txt", ".md", ".pdf"}


def read_file(path: Path) -> str:
    if path.suffix.lower() == ".pdf":
        reader = PdfReader(str(path))
        return "\n\n".join((page.extract_text() or "") for page in reader.pages)
    return path.read_text(encoding="utf-8")


def load_documents(folder: Path = config.POLICIES_DIR) -> list[dict]:
    """Return [{'source': 'leave_policy.txt', 'text': '...'}, ...]."""
    docs = []
    for path in sorted(Path(folder).glob("*")):
        if path.suffix.lower() in SUPPORTED:
            text = read_file(path).strip()
            if text:
                docs.append({"source": path.name, "text": text})
    return docs
