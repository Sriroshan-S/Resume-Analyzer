import pdfplumber


def extract_text_from_pdf(file_path):
    """Read a PDF file and return all its text as one string."""
    if not file_path.lower().endswith(".pdf"):
        raise ValueError("Only PDF files are supported.")

    text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except FileNotFoundError:
        raise FileNotFoundError("File not found: " + file_path)

    if text.strip() == "":
        raise ValueError("No text could be extracted from this PDF.")

    return text.strip()


if __name__ == "__main__":
    print(extract_text_from_pdf("sample_resume.pdf"))