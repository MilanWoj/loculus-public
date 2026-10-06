# Author: MilanWoj
from pathlib import Path
from pypdf import PdfReader
from docx import Document


class UnsupportedFormatError(Exception):
    pass


def extract_text(file_path: Path) -> str:
    suffix = file_path.suffix.lower()

    if suffix == ".pdf":
        reader = PdfReader(str(file_path))
        return "\n".join(page.extract_text() or "" for page in reader.pages)

    if suffix == ".docx":
        doc = Document(str(file_path))
        return "\n".join(p.text for p in doc.paragraphs)

    if suffix in (".txt", ".md"):
        return file_path.read_text(encoding="utf-8", errors="ignore")

    raise UnsupportedFormatError(f"Unsupported format: {suffix}")
