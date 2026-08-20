from pathlib import Path
from resume_parser.pdf_parser import extract_pdf_text
from resume_parser.docx_parser import extract_docx_text
from agents.resume_agent import ResumeAgent

def parse_resume_file(file_name: str, file_bytes: bytes) -> dict:
    """
    Parses a resume file based on extension and returns structured analysis dict.
    Supports .pdf, .docx, .txt.
    """
    suffix = Path(file_name).suffix.lower()
    
    if suffix == ".pdf":
        text = extract_pdf_text(file_bytes)
    elif suffix == ".docx":
        text = extract_docx_text(file_bytes)
    elif suffix in [".txt", ".text"]:
        text = file_bytes.decode("utf-8", errors="ignore").strip()
    else:
        raise ValueError("Unsupported file type. Please upload a PDF, DOCX, or TXT file.")
        
    if not text.strip():
        raise ValueError("Resume contains no readable text.")
        
    # Analyze with Resume Agent
    agent = ResumeAgent()
    parsed_info = agent.analyze(text)
    
    # Keep the file information and raw text
    parsed_info["resume_filename"] = file_name
    parsed_info["resume_text"] = text
    
    return parsed_info
