import json
from pathlib import Path
import re

INPUT_JSON = Path("data/segments/ITC_FY2023_paragraphs.json")
OUTPUT_JSON = Path("data/segments/ITC_FY2023_paragraphs_tagged.json")

SECTION_HEADINGS = [
    "SOCIO-ECONOMIC ENVIRONMENT",
    "FINANCIAL PERFORMANCE",
    "VALUE-ADDED AND CONTRIBUTION TO EXCHEQUER",
    "FOREIGN EXCHANGE EARNINGS",
    "PROFITS, DIVIDENDS AND RETAINED EARNINGS",
    "FMCG CIGARETTES",
    "FMCG – OTHERS",
    "BRANDED PACKAGED FOODS",
    "PERSONAL CARE PRODUCTS",
    "EDUCATION AND STATIONERY PRODUCTS",
    "INCENSE STICKS (AGARBATTIS) AND SAFETY MATCHES",
    "TRADE MARKETING & DISTRIBUTION",
    "HOTELS",
    "PAPERBOARDS, PAPER AND PACKAGING",
    "AGRI BUSINESS",
    "RISK MANAGEMENT",
    "INTERNAL FINANCIAL CONTROLS",
    "SUSTAINABILITY",
    "CORPORATE SOCIAL RESPONSIBILITY (CSR)",
    "R&D, QUALITY AND PRODUCT DEVELOPMENT",
    "TREASURY OPERATIONS",
    "RELATED PARTY TRANSACTIONS",
    "FORWARD-LOOKING STATEMENTS"
]

def normalize(text: str) -> str:
    t = text.upper()
    t = t.replace("–", "-")  # normalize dash
    t = re.sub(r"[^A-Z0-9& ]+", "", t)  # drop punctuation except &
    t = re.sub(r"\s+", " ", t).strip()
    return t

def main():
    normalized_headings = {
        normalize(h): h for h in SECTION_HEADINGS
    }

    records = json.loads(INPUT_JSON.read_text(encoding="utf-8"))

    current_section = "UNCLASSIFIED"
    tagged = []

    for r in records:
        text = r["text"].strip()

        norm_text = normalize(text)
        if norm_text in normalized_headings:
            current_section = normalized_headings[norm_text]

        tagged.append({
            "para_id": r["para_id"],
            "year": r["year"],
            "section": current_section,
            "text": r["text"]
        })

    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(json.dumps(tagged, indent=2), encoding="utf-8")

    print(f"Tagged {len(tagged)} paragraphs → {OUTPUT_JSON}")

if __name__ == "__main__":
    main()