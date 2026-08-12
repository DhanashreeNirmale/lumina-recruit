from pypdf import PdfReader

from utils.helpers import clean_text


def extract_pdf_text(file) -> str:
    """
    Extract text from a PDF resume.
    """

    try:
        reader = PdfReader(file)

        pages = []

        for page in reader.pages:
            page_text = page.extract_text()

            if page_text:
                pages.append(page_text)

        return clean_text("\n".join(pages))

    except Exception as exc:
        raise RuntimeError(
            f"Unable to read PDF resume: {exc}"
        ) from exc