import re
from pathlib import Path

NOISE_PATTERNS = [
    r"^REPORT AND ACCOUNTS.*$",
    r"^ITC Limited.*$",
    r"^Report of the Board of Directors.*$",
    r"^Management Discussion and Analysis.*$",
    r"^For the Financial Year Ended.*$"
]

def is_noise_line(line: str) -> bool:
    line = line.strip()

    # Empty lines
    if not line:
        return True

    # Page numbers (e.g., "38", "  42 ")
    if re.fullmatch(r"\d+", line):
        return True

    # Known boilerplate headers
    for pattern in NOISE_PATTERNS:
        if re.match(pattern, line):
            return True

    return False


def clean_mda_text(raw_text: str) -> str:
    cleaned_lines = []
    seen_lines = set()

    for raw_line in raw_text.splitlines():
        line = raw_line.strip()

        if is_noise_line(line):
            continue

        # Remove exact duplicate lines
        if line in seen_lines:
            continue

        seen_lines.add(line)
        cleaned_lines.append(line)

    return "\n".join(cleaned_lines)


if __name__ == "__main__":
    input_file = Path("data/raw_text/ITC_FY2023_MDA.txt")
    output_file = Path("data/raw_text/ITC_FY2023_MDA_CLEAN.txt")

    raw_text = input_file.read_text(encoding="utf-8")
    cleaned_text = clean_mda_text(raw_text)

    output_file.write_text(cleaned_text, encoding="utf-8")

    print(f"Cleaned MD&A text written to {output_file}")