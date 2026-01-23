import fitz  # PyMuPDF
import re
from pathlib import Path

# -----------------------------
# CONFIG (explicit, boring)
# -----------------------------

PDF_INPUT = Path("data/raw/2023.pdf")
OUTPUT_TEXT = Path("data/corpus/ITC_FY2023_MDA.txt")

# MD&A page range (1-based, inclusive)
MDA_START_PAGE = 78
MDA_END_PAGE = 163

HEADER_PATTERNS = [
    r"^REPORT AND ACCOUNTS.*",
    r"^ITC Limited.*",
    r"^Report of the Board of Directors.*",
    r"^Management Discussion and Analysis.*",
]

# -----------------------------
# HELPERS
# -----------------------------

def is_header_or_footer(line: str) -> bool:
    line = line.strip()

    # Page numbers
    if re.fullmatch(r"\d+", line):
        return True

    # Known headers / footers
    for pattern in HEADER_PATTERNS:
        if re.match(pattern, line):
            return True

    return False

# -----------------------------
# CORE INGESTION
# -----------------------------

def extract_mda_from_pdf(pdf_path: Path) -> str:
    doc = fitz.open(pdf_path)
    text_lines = []

    for page_idx in range(MDA_START_PAGE - 1, MDA_END_PAGE):
        page = doc.load_page(page_idx)
        page_text = page.get_text()

        for line in page_text.splitlines():
            line = line.strip()

            if not line:
                continue

            if is_header_or_footer(line):
                continue

            text_lines.append(line)

    return "\n".join(text_lines)

def deduplicate_lines(text: str) -> str:
    seen = set()
    final_lines = []

    for line in text.splitlines():
        if line in seen:
            continue
        seen.add(line)
        final_lines.append(line)

    return "\n".join(final_lines)

# -----------------------------
# ENTRY POINT
# -----------------------------

def ingest():
    print("Extracting MD&A from PDF...")
    raw_text = extract_mda_from_pdf(PDF_INPUT)

    print("Deduplicating lines...")
    canonical_text = deduplicate_lines(raw_text)

    OUTPUT_TEXT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_TEXT.write_text(canonical_text, encoding="utf-8")

    print(f"Canonical MD&A corpus written to {OUTPUT_TEXT}")

if __name__ == "__main__":
    ingest()