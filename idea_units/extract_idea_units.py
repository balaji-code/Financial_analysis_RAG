import json
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

PROMPT_TEMPLATE = """
You are a senior equity research analyst.

Your task is to extract atomic idea units from a Management Discussion & Analysis paragraph.

Rules:
1. Extract ONLY substantive analytical ideas (drivers, risks, strategies, outcomes).
2. Ignore tables, numeric listings, boilerplate, slogans, awards, and repetitions.
3. Each idea unit must express ONE clear idea.
4. Do NOT copy sentences verbatim. Paraphrase into analytical language.
5. If the paragraph contains no analytical content, return an empty list.
6. Do NOT invent information not present in the paragraph.
7. Extract AT MOST 3 idea units per paragraph.
8. If multiple sentences support the same idea, combine them into a single analytical idea unit.
9. Do NOT extract standalone facts, statistics, or observations unless they are used to support a broader analytical claim.
10. Each idea unit must explain why the point matters for business performance, risk, or long-term competitiveness.
11. Prefer causal, interpretive statements over descriptive summaries of events or data.
12. If multiple sentences in the paragraph support the same underlying idea, merge them into a single idea unit with analytical framing.
Context:
- Company: ITC
- Year: 2023
- Section: {section}

Paragraph:
{paragraph_text}

Output format (JSON only):
[
  {{
    "idea_text": "...",
    "idea_type": "macro_driver | business_driver | risk | strategy | outcome | capital_allocation | sustainability"
  }}
]
"""

client = OpenAI()

INPUT = Path("data/segments/ITC_FY2023_paragraphs_tagged.json")
OUTPUT = Path("data/idea_units/ITC_FY2023_idea_units.jsonl")

OUTPUT.parent.mkdir(parents=True, exist_ok=True)

def main():
    records = json.loads(INPUT.read_text(encoding="utf-8"))

    with OUTPUT.open("w", encoding="utf-8") as f:
        for r in records[:10]:
            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {"role": "system", "content": "You are a senior equity research analyst."},
                    {"role": "user", "content": PROMPT_TEMPLATE.format(
                        section=r["section"],
                        paragraph_text=r["text"]
                    )}
                ],
                temperature=0.2
            )

            content = response.choices[0].message.content.strip()

            try:
                ideas = json.loads(content)
            except json.JSONDecodeError:
                continue

            for i, idea in enumerate(ideas, start=1):
                idea_record = {
                    "idea_id": f"{r['para_id']}_I{i:02d}",
                    "para_id": r["para_id"],
                    "year": r["year"],
                    "section": r["section"],
                    **idea
                }
                f.write(json.dumps(idea_record) + "\n")


if __name__ == "__main__":
    main()