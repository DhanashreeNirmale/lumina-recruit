import io
from pypdf import PdfReader

def extract_pdf_text(file_bytes: bytes) -> str:
    """Extracts text from PDF bytes using pypdf."""
    try:
        reader = PdfReader(io.BytesIO(file_bytes))
        text = ""
        for page in reader.pages:
            content = page.extract_text()
            if content:
                text += content + "\n"
        return text.strip()
    except Exception as exc:
        raise ValueError(f"Error parsing PDF: {exc}")
