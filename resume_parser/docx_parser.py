from docx import Document

from utils.helpers import clean_text


def extract_docx_text(file) -> str:
    """
    Extract text from a DOCX resume.
    """

    try:
        document = Document(file)

        paragraphs = []

        for paragraph in document.paragraphs:
            if paragraph.text.strip():
                paragraphs.append(paragraph.text)

        # Also read tables because many resumes store data in tables.
        for table in document.tables:
            for row in table.rows:
                row_text = []

                for cell in row.cells:
                    if cell.text.strip():
                        row_text.append(cell.text.strip())

                if row_text:
                    paragraphs.append(" | ".join(row_text))

        return clean_text("\n".join(paragraphs))

    except Exception as exc:
        raise RuntimeError(
            f"Unable to read DOCX resume: {exc}"
        ) from exc