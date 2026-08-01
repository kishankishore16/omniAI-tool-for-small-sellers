"""
Text embedding utility using ChromaDB's default embedding function.
"""
import chromadb.utils.embedding_functions as embedding_functions

class EmbeddingEngine:
    def __init__(self):
        # Lazy-loads ChromaDB's DefaultEmbeddingFunction (ONNX all-MiniLM-L6-v2)
        self.embedding_function = embedding_functions.DefaultEmbeddingFunction()

    def embed(self, text: str) -> list[float]:
        """Returns 384-dim embedding vector for a single string."""
        return self.embedding_function([text])[0]

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Batch embedding for multiple strings."""
        return self.embedding_function(texts)
