from ingest.pdf_loader import load_pdf_text
from ingest.mda_parser import extract_mda_pages
from ingest.chunker import split_into_paragraphs

pages = load_pdf_text("data/raw/2023.pdf")
mda_pages = extract_mda_pages(pages, 78, 163)
paragraphs = split_into_paragraphs(mda_pages)

macro_candidates = [
    p for p in paragraphs
    if any(k in p["paragraph"].lower() for k in [
        "global", "india", "economy", "inflation",
        "geopolitical", "gdp", "macro", "socio"
    ])
]

print(len(macro_candidates))
print(macro_candidates[0]["paragraph"][:400])