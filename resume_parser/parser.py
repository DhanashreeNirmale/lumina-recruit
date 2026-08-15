from pathlib import Path


def extract_text(uploaded_file):

    suffix = Path(
        uploaded_file.name
    ).suffix.lower()

    data = uploaded_file.getvalue()


    if suffix == ".pdf":

        from io import BytesIO
        from pypdf import PdfReader

        reader = PdfReader(
            BytesIO(data)
        )

        return "\n".join(
            page.extract_text() or ""
            for page in reader.pages
        ).strip()


    if suffix == ".docx":

        from io import BytesIO
        from docx import Document

        document = Document(
            BytesIO(data)
        )

        return "\n".join(
            paragraph.text
            for paragraph in document.paragraphs
        ).strip()


    if suffix == ".txt":

        return data.decode(
            "utf-8",
            errors="ignore"
        ).strip()


    raise ValueError(
        "Unsupported file. "
        "Upload PDF, DOCX or TXT."
    )