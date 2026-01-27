from embeddings.vector_store import VectorStore,cosine_similarity

store = VectorStore()

CURRENT_YEAR = 2023
PAST_YEARS = [2021, 2022]

SIMILARITY_THRESHOLD = 0.75  # tuneable, conservative

current_risks = store.get_by_year_and_type(CURRENT_YEAR, "risk")

past_vectors = []
for y in PAST_YEARS:
    past_vectors.extend(store.get_by_year_and_type(y, "risk"))

emerging = []

for cur_vec, cur_meta in current_risks:
    max_sim = 0.0

    for past_vec, past_meta in past_vectors:
        sim = cosine_similarity(cur_vec, past_vec)
        max_sim = max(max_sim, sim)

    if max_sim < SIMILARITY_THRESHOLD:
        emerging.append((cur_meta, max_sim))

print("\n=== Newly Emerging Risks ===\n")

for meta, score in sorted(emerging, key=lambda x: x[1]):
    print("----")
    print("Idea ID:", meta["idea_id"])
    print("Year:", meta["year"])
    print("Section:", meta["section"])
    print("Similarity to past:", round(score, 2))
