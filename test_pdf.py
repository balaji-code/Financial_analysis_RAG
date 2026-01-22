from ingest.pdf_loader import load_pdf_text
from ingest.mda_parser import extract_mda_pages
from ingest.chunker import split_into_paragraphs

pages = load_pdf_text("data/raw/2023.pdf")
mda_pages = extract_mda_pages(pages, 78, 163)
paragraphs = split_into_paragraphs(mda_pages)

print(len(paragraphs))
print(paragraphs[0]["page_no"])
print(paragraphs[0]["paragraph"][:300])