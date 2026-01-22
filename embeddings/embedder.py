import os
from dotenv import load_dotenv
from openai import OpenAI


# Load environment variables
load_dotenv()

EMBEDDING_MODEL = "text-embedding-3-large"

class Embedder:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        self.client = OpenAI(api_key=api_key)

    def get_embedding(self, text):
        """
        Generate an embedding using a locked embedding model.
        All embeddings in this system MUST use the same model.
        """
        text = text.replace("\n", " ")
        return self.client.embeddings.create(
            input=[text],
            model=EMBEDDING_MODEL
        ).data[0].embedding