class SimpleVectorStore:
    def __init__(self):
        # Store everything in a single list for clarity
        # Each item is a dict with: vector, metadata
        self.items = []

    def add(self, vector, metadata):
        """
        Add one embedded idea unit to the store.
        vector   : list of numbers (embedding)
        metadata : dict (year, bucket, segment, etc.)
        """
        self.items.append({
            "vector": vector,
            "metadata": metadata
        })

    def search(self, query_vector, filters, top_k=3):
        """
        Retrieve the most relevant items after applying metadata filters.
        """
        results = []

        for item in self.items:
            metadata = item["metadata"]

            # 1. Apply filters FIRST
            matches = True
            for key, value in filters.items():
                if metadata.get(key) != value:
                    matches = False
                    break

            if not matches:
                continue

            # 2. Compute simple similarity score
            score = self._simple_similarity(query_vector, item["vector"])

            results.append({
                "score": score,
                "metadata": metadata,
                "vector": item["vector"]
            })

        # 3. Rank by similarity (highest first)
        results.sort(key=lambda x: x["score"], reverse=True)

        # 4. Return top-k results
        return results[:top_k]

    def _simple_similarity(self, vec1, vec2):
        """
        Very simple similarity:
        multiply corresponding numbers and sum them.
        """
        score = 0
        for a, b in zip(vec1, vec2):
            score += a * b
        return score