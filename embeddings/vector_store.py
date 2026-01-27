import json
import numpy as np
from pathlib import Path

EMBEDDINGS = Path("data/embeddings/ITC_FY2023_embeddings.json")

def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

class VectorStore:
    def __init__(self, path=EMBEDDINGS):
        data = json.loads(path.read_text())
        self.vectors = [d["vector"] for d in data]
        self.meta = [d["metadata"] for d in data]

    def search(self, query_vector, top_k=5, filter_fn=None):
        scores = []
        for i, v in enumerate(self.vectors):
            if filter_fn and not filter_fn(self.meta[i]):
                continue
            sim = cosine_similarity(query_vector, v)
            scores.append((sim, self.meta[i]))

        scores.sort(reverse=True, key=lambda x: x[0])
        return scores[:top_k]