import re
from pathlib import Path
from collections import Counter

STOP_PHRASE = "The Directors of your Company are pleased to recommend"

CONNECTOR_WORDS = {
    "however", "therefore", "while", "although", "despite",
    "further", "moreover", "accordingly", "against", "in spite"
}

def tokenize(text):
    return re.findall(r"\w+|₹|%|`", text.lower())

def is_section_heading(paragraph):
    return (
        paragraph.isupper()
        and len(paragraph.split()) <= 6
        and paragraph.replace(" ", "").isalpha()
    )

def is_numeric_dominant(paragraph):
    tokens = tokenize(paragraph)
    if not tokens:
        return True

    numeric_tokens = [t for t in tokens if t.isdigit() or t in {"₹", "%", "`"}]
    return len(numeric_tokens) / len(tokens) > 0.30

def contains_connectors(paragraph):
    words = set(tokenize(paragraph))
    return bool(words & CONNECTOR_WORDS)

def clean_mda_text_v3(raw_text: str) -> str:
    # Split into paragraphs
    paragraphs = [
        p.strip()
        for p in raw_text.split("\n\n")
        if p.strip()
    ]

    # Hard stop at dividend section
    scoped = []
    for p in paragraphs:
        if STOP_PHRASE in p:
            break
        scoped.append(p)

    # Count paragraph frequency (for pull-quotes)
    para_counts = Counter(scoped)

    final_paragraphs = []

    for p in scoped:
        # Always keep section headings
        if is_section_heading(p):
            final_paragraphs.append(p)
            continue

        # Drop numeric-heavy paragraphs
        if is_numeric_dominant(p):
            continue

        # Drop pull-quote duplicates
        if para_counts[p] > 1 and not contains_connectors(p):
            continue

        final_paragraphs.append(p)

    return "\n\n".join(final_paragraphs)


if __name__ == "__main__":
    input_file = Path("data/raw_text/ITC_FY2023_MDA_FINAL.txt")
    output_file = Path("data/raw_text/ITC_FY2023_MDA_CANONICAL.txt")

    raw_text = input_file.read_text(encoding="utf-8")
    canonical_text = clean_mda_text_v3(raw_text)

    output_file.write_text(canonical_text, encoding="utf-8")

    print(f"Canonical MD&A text written to {output_file}")