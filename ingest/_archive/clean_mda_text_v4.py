import re
from pathlib import Path
from collections import Counter

DIVIDEND_KEYWORDS = {
    "dividend", "cash outflow", "recommend",
    "interim dividend", "final dividend"
}

FINANCIAL_METRIC_KEYWORDS = {
    "revenue", "ebitda", "profit", "eps",
    "earnings per share", "pat", "pbt"
}

CONNECTOR_WORDS = {
    "however", "therefore", "while", "although",
    "despite", "further", "moreover", "accordingly",
    "against", "in spite", "as a result"
}

def tokenize(text):
    return re.findall(r"\w+|₹|%|`", text.lower())

def contains_any(text, keywords):
    text = text.lower()
    return any(k in text for k in keywords)

def is_numeric_dense(paragraph):
    tokens = tokenize(paragraph)
    if not tokens:
        return False

    # Do not treat long narrative paragraphs as numeric-dense
    if len(tokens) > 120:
        return False

    numeric = [t for t in tokens if t.isdigit() or t in {"₹", "%", "`"}]
    return len(numeric) / len(tokens) > 0.40

def is_section_heading(paragraph):
    return (
        paragraph.isupper()
        and len(paragraph) <= 80
    )

def has_connectors(paragraph):
    words = set(tokenize(paragraph))
    return bool(words & CONNECTOR_WORDS)

def final_prune(paragraphs):
    cleaned = []

    # Count paragraph frequency for pull-quote detection
    para_counts = Counter(paragraphs)
    seen_paragraphs = set()

    for p in paragraphs:
        p_norm = p.strip()

        # Always keep section headings
        if is_section_heading(p_norm):
            cleaned.append(p_norm)
            continue

        # Drop dividend / board recommendation content
        if contains_any(p_norm, DIVIDEND_KEYWORDS):
            continue

        # Drop financial-statement summary paragraphs
        if (
            contains_any(p_norm, FINANCIAL_METRIC_KEYWORDS)
            and is_numeric_dense(p_norm)
        ):
            continue

        # Drop standalone pull-quote duplicates ONLY after first occurrence
        if para_counts[p_norm] > 1 and not has_connectors(p_norm):
            if p_norm in seen_paragraphs:
                continue

        cleaned.append(p_norm)
        seen_paragraphs.add(p_norm)

    if len(cleaned) < max(3, int(0.1 * len(paragraphs))):
        # Safety fallback: cleaning was too aggressive
        return "\n\n".join(paragraphs)

    return "\n\n".join(cleaned)


if __name__ == "__main__":
    input_file = Path("data/raw_text/ITC_FY2023_MDA_CANONICAL.txt")
    output_file = Path("data/raw_text/ITC_FY2023_MDA_FINAL_ANALYTICAL.txt")

    raw_text = input_file.read_text(encoding="utf-8")
    paragraphs = [p.strip() for p in raw_text.split("\n\n") if p.strip()]

    final_text = final_prune(paragraphs)
    output_file.write_text(final_text, encoding="utf-8")

    print(f"Final analytical MD&A written to {output_file}")