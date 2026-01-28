# tools.py
# This file defines tools the agent can use.
# A tool is just a function the agent is allowed to call.

from embeddings.vector_store import VectorStore
from openai import OpenAI

client = OpenAI()
store = VectorStore()

def search_risks(query, top_k=3):
    """
    Tool: Search risk-related idea units using semantic similarity.
    """
    q_embed = client.embeddings.create(
        model="text-embedding-3-small",
        input=query
    ).data[0].embedding

    results = store.search(
        q_embed,
        top_k=top_k,
        filter_fn=lambda m: m["idea_type"] == "risk"
    )

    return results