from pypdf import PdfReader

def load_pdf_text(pdf_path: str) -> list[tuple[int, str]]:
    """
    Returns list of (page_number, page_text)
    """
    reader = PdfReader(pdf_path)
    pages = []

    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        if text:
            pages.append((i + 1, text))

    return pages