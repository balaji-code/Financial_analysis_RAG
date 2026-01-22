from embeddings.embedder import Embedder
from embeddings.vector_store import SimpleVectorStore

# --- FY2023 Cost, Margin & Inflation Management idea units ---
idea_units = [
    {
        "text": "Absorbed sharp input cost inflation in the first half of the year across edible oils, packaging materials, pulp, chemicals, fuel and logistics, with selective commodity price moderation emerging in the second half.",
        "metadata": {
            "company": "ITC",
            "year": 2023,
            "section": "MD&A",
            "bucket": "Cost, Margin & Inflation Management",
            "business_segment": "overall",
            "source_pages": [78, 163]
        }
    },
    {
        "text": "Implemented calibrated and judicious pricing actions across businesses to partially offset cost inflation without materially impairing demand elasticity.",
        "metadata": {
            "company": "ITC",
            "year": 2023,
            "section": "MD&A",
            "bucket": "Cost, Margin & Inflation Management",
            "business_segment": "overall",
            "source_pages": [78, 163]
        }
    },
    {
        "text": "Executed enterprise-wide cost management initiatives focused on productivity improvement, strategic sourcing and tighter control over discretionary expenditure.",
        "metadata": {
            "company": "ITC",
            "year": 2023,
            "section": "MD&A",
            "bucket": "Cost, Margin & Inflation Management",
            "business_segment": "overall",
            "source_pages": [78, 163]
        }
    },
    {
        "text": "Strengthened supply-chain agility through integration, import substitution and proactive vendor and logistics management to mitigate volatility in input availability and costs.",
        "metadata": {
            "company": "ITC",
            "year": 2023,
            "section": "MD&A",
            "bucket": "Cost, Margin & Inflation Management",
            "business_segment": "overall",
            "source_pages": [78, 163]
        }
    },
    {
        "text": "Deployed digital interventions and Industry 4.0 tools to improve manufacturing efficiency, reduce wastage and lower per-unit costs across operations.",
        "metadata": {
            "company": "ITC",
            "year": 2023,
            "section": "MD&A",
            "bucket": "Cost, Margin & Inflation Management",
            "business_segment": "overall",
            "source_pages": [78, 163]
        }
    },
    {
        "text": "Leveraged fiscal incentives including Production Linked Incentive benefits to partially offset inflationary pressures and support margin protection.",
        "metadata": {
            "company": "ITC",
            "year": 2023,
            "section": "MD&A",
            "bucket": "Cost, Margin & Inflation Management",
            "business_segment": "overall",
            "source_pages": [78, 163]
        }
    }
]

# --- FY2022 Cost, Margin & Inflation Management idea units ---
idea_units_2022 = [
    {
        "text": "Input cost inflation across edible oils, packaging materials, fuel and logistics exerted sustained margin pressure during the year.",
        "metadata": {
            "company": "ITC",
            "year": 2022,
            "section": "MD&A",
            "bucket": "Cost, Margin & Inflation Management",
            "business_segment": "overall",
            "source_pages": [70, 150]
        }
    },
    {
        "text": "Calibrated pricing actions and portfolio mix interventions were undertaken to partially mitigate the impact of rising input costs.",
        "metadata": {
            "company": "ITC",
            "year": 2022,
            "section": "MD&A",
            "bucket": "Cost, Margin & Inflation Management",
            "business_segment": "overall",
            "source_pages": [70, 150]
        }
    },
    {
        "text": "Focused cost control, productivity initiatives and supply-chain efficiencies were prioritised to protect margins amid inflationary pressures.",
        "metadata": {
            "company": "ITC",
            "year": 2022,
            "section": "MD&A",
            "bucket": "Cost, Margin & Inflation Management",
            "business_segment": "overall",
            "source_pages": [70, 150]
        }
    }
]

embedder = Embedder()
store = SimpleVectorStore()

for unit in idea_units + idea_units_2022:
    vector = embedder.get_embedding(unit["text"])
    store.add(vector, unit["metadata"])

print("Embedded records:", len(store.items))

print("\nFY2023 search results:")
results_2023 = store.search(
    query_vector=embedder.get_embedding(
        "How did ITC manage cost inflation in FY2023?"
    ),
    filters={
        "year": 2023,
        "bucket": "Cost, Margin & Inflation Management"
    },
    top_k=3
)

for i, r in enumerate(results_2023, start=1):
    print(f"FY2023 Result {i}:", r["metadata"])

print("\nFY2022 search results:")
results_2022 = store.search(
    query_vector=embedder.get_embedding(
        "How did ITC manage cost inflation in FY2022?"
    ),
    filters={
        "year": 2022,
        "bucket": "Cost, Margin & Inflation Management"
    },
    top_k=3
)

for i, r in enumerate(results_2022, start=1):
    print(f"FY2022 Result {i}:", r["metadata"])