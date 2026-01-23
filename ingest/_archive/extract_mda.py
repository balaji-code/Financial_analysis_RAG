import fitz  # PyMuPDF
from pathlib import Path

def extract_mda_text(pdf_path, start_page, end_page):
    """
    Extract raw text from a PDF between page numbers (1-based, inclusive).
    """
    doc = fitz.open(pdf_path)
    text_chunks = []

    for page_num in range(start_page - 1, end_page):
        page = doc.load_page(page_num)
        text = page.get_text()
        text_chunks.append(text)

    return "\n".join(text_chunks)


if __name__ == "__main__":
    pdf_file = "data/raw/2023.pdf"
    output_file = "data/raw_text/ITC_FY2023_MDA.txt"

    # You already identified this earlier
    MDA_START_PAGE = 78
    MDA_END_PAGE = 163

    mda_text = extract_mda_text(
        pdf_file,
        MDA_START_PAGE,
        MDA_END_PAGE
    )

    Path(output_file).write_text(mda_text, encoding="utf-8")

    print(f"MD&A text extracted to {output_file}")