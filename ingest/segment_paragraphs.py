import json
import re
from pathlib import Path

INPUT_TEXT = Path("data/corpus/ITC_FY2023_MDA.txt")
OUTPUT_JSON = Path("data/segments/ITC_FY2023_paragraphs.json")

YEAR = 2023


def is_section_heading(text: str) -> bool:
    return text.isupper() and len(text) <= 80


def merge_wrapped_headings(lines):
    merged = []
    i = 0
    while i < len(lines):
        curr = lines[i].strip()
        if (
            curr.isupper()
            and i + 1 < len(lines)
            and lines[i + 1].strip().isupper()
            and len(curr) + len(lines[i + 1].strip()) <= 80
        ):
            merged.append(f"{curr} {lines[i + 1].strip()}")
            i += 2
        else:
            merged.append(lines[i])
            i += 1
    return merged


def is_table_junk(text: str) -> bool:
    t = text.strip()

    if t.startswith(("STATEMENT OF", "PROFITS,", "a)", "b)", "c)", "d)")):
        return True

    if len(t.split()) <= 3 and (t.isupper() or t.startswith("FY")):
        return True

    digits = sum(c.isdigit() for c in t)
    return digits > 0 and digits / max(len(t), 1) > 0.45


def split_long_paragraph(text: str, max_sentences=6):
    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks, buf = [], []

    for s in sentences:
        buf.append(s)
        if len(buf) >= max_sentences:
            chunks.append(" ".join(buf))
            buf = []

    if buf:
        chunks.append(" ".join(buf))

    return chunks


def ends_incomplete(text: str) -> bool:
    return not re.search(r"[.!?]$", text.strip())


def starts_continuation(text: str) -> bool:
    return bool(re.match(r"^[a-z0-9%]", text.strip()))


def dedupe_spans(text: str) -> str:
    words = text.split()
    cleaned = []
    seen = set()

    for i in range(len(words)):
        span = " ".join(words[i:i+8])
        if span in seen:
            continue
        seen.add(span)
        cleaned.append(words[i])

    return " ".join(cleaned)


def segment_paragraphs(raw_text: str):
    lines = merge_wrapped_headings([l.rstrip() for l in raw_text.splitlines()])

    paragraphs = []
    buffer = []

    def flush():
        if buffer:
            paragraphs.append(" ".join(buffer).strip())
            buffer.clear()

    for line in lines:
        stripped = line.strip()

        if not stripped:
            flush()
            continue

        if is_table_junk(stripped):
            continue

        if is_section_heading(stripped):
            flush()
            paragraphs.append(stripped)
            continue

        buffer.append(stripped)

    flush()

    refined = []
    for p in paragraphs:
        if len(p.split()) > 180:
            refined.extend(split_long_paragraph(p))
        else:
            refined.append(p)

    final = []
    for p in refined:
        if final and ends_incomplete(final[-1]) and starts_continuation(p):
            final[-1] = dedupe_spans(final[-1] + " " + p)
        else:
            final.append(dedupe_spans(p))

    return final


def main():
    raw_text = INPUT_TEXT.read_text(encoding="utf-8")
    paras = segment_paragraphs(raw_text)

    records = []
    for idx, para in enumerate(paras, start=1):
        records.append({
            "para_id": f"FY{YEAR}_P{idx:04d}",
            "year": YEAR,
            "text": para
        })

    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(json.dumps(records, indent=2), encoding="utf-8")

    print(f"Final segmented paragraphs: {len(records)} → {OUTPUT_JSON}")


if __name__ == "__main__":
    main()