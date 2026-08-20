from resume_parser.resume_extractor import parse_resume_file

def extract_text(uploaded_file):
    """Legacy compatibility helper."""
    # Mimic old behavior of reading from streamlit UploadedFile wrapper
    name = uploaded_file.name
    bytes_data = uploaded_file.getvalue()
    
    from pathlib import Path
    suffix = Path(name).suffix.lower()
    
    if suffix == ".pdf":
        from resume_parser.pdf_parser import extract_pdf_text
        return extract_pdf_text(bytes_data)
    elif suffix == ".docx":
        from resume_parser.docx_parser import extract_docx_text
        return extract_docx_text(bytes_data)
    else:
        return bytes_data.decode("utf-8", errors="ignore").strip()