from utils import extract_text_from_file, clean_text, get_lines

with open("your_resume_file.pdf", "rb") as f:
    raw = extract_text_from_file(f)
    raw = clean_text(raw)

    for i, line in enumerate(get_lines(raw)):
        print(i, repr(line))