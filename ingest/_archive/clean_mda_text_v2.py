import re
from pathlib import Path
from collections import Counter

STOP_SECTION_PATTERN = r"^VALUE-ADDED AND CONTRIBUTION"

def is_numeric_heavy(line: str) -> bool:
    words = re.findall(r"[A-Za-z]+", line)
    numbers = re.findall(r"\d+", line)
    return len(numbers) > len(words)

def clean_mda_text_v2(raw_text: str) -> str:
    lines = [l.strip() for l in raw_text.splitlines() if l.strip()]

    # Stop at non-MD&A section
    cleaned_scope = []
    for line in lines:
        if re.match(STOP_SECTION_PATTERN, line):
            break
        cleaned_scope.append(line)

    # Count line frequency (for pull-quotes)
    line_counts = Counter(cleaned_scope)

    final_lines = []
    seen_pullquotes = set()

    for line in cleaned_scope:
        # Remove numeric-heavy lines (tables, charts)
        if is_numeric_heavy(line):
            continue

        # Handle pull-quote duplicates
        if line_counts[line] > 1 and len(line.split()) <= 25:
            if line in seen_pullquotes:
                continue
            seen_pullquotes.add(line)

        final_lines.append(line)

    return "\n".join(final_lines)


if __name__ == "__main__":
    input_file = Path("data/raw_text/ITC_FY2023_MDA_CLEAN.txt")
    output_file = Path("data/raw_text/ITC_FY2023_MDA_FINAL.txt")

    raw_text = input_file.read_text(encoding="utf-8")
    final_text = clean_mda_text_v2(raw_text)

    output_file.write_text(final_text, encoding="utf-8")

    print(f"Final MD&A text written to {output_file}")