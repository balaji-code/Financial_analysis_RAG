from openai import OpenAI
from embeddings.vector_store import VectorStore
from dotenv import load_dotenv
load_dotenv()
client = OpenAI()
store = VectorStore()

query = "What are the key macroeconomic risks facing ITC?"

q_embed = client.embeddings.create(
    model="text-embedding-3-small",
    input=query
).data[0].embedding

results = store.search(
    q_embed,
    top_k=5,
    filter_fn=lambda m: m["idea_type"] == "risk"
)

for score, meta in results:
    print(meta, score)