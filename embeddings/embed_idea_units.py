import json
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()
client = OpenAI()

INPUT = Path("data/idea_units/ITC_FY2023_idea_units.jsonl")
OUTPUT = Path("data/embeddings/ITC_FY2023_embeddings.json")

OUTPUT.parent.mkdir(parents=True, exist_ok=True)

embeddings = []

with INPUT.open("r", encoding="utf-8") as f:
    for line in f:
        record = json.loads(line)

        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=record["idea_text"]
        )

        embeddings.append({
            "vector": response.data[0].embedding,
            "metadata": {
                "idea_id": record["idea_id"],
                "year": record["year"],
                "section": record["section"],
                "idea_type": record["idea_type"],
                "para_id": record["para_id"]
            }
        })

OUTPUT.write_text(json.dumps(embeddings), encoding="utf-8")

print(f"Embedded {len(embeddings)} idea units.")