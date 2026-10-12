import docx
import os
from pypdf import PdfReader

def parse_cv(file_path: str) -> str:
    """
    Extrait le texte brut d'un fichier PDF ou DOCX.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"CV file not found: {file_path}")

    ext = file_path.lower().split('.')[-1]
    text = ""

    if ext == "pdf":
        reader = PdfReader(file_path)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    elif ext in ["doc", "docx"]:
        doc = docx.Document(file_path)
        for para in doc.paragraphs:
            text += para.text + "\n"
    else:
        raise ValueError(f"Unsupported file extension: {ext}")

    return text.strip()
