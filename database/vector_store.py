"""
ChromaDB vector store wrapper for OmniAI.
Manages embeddings and similarity search for product catalog.
"""
import os
import logging
from typing import Any, Optional

import chromadb

logger = logging.getLogger(__name__)


class VectorStore:
    """Wrapper around ChromaDB PersistentClient for product vector search."""

    def __init__(self, persist_dir: str, collection_name: str):
        self.persist_dir = persist_dir
        self.collection_name = collection_name
        self.client: Optional[chromadb.PersistentClient] = None
        self.collection = None

        try:
            os.makedirs(persist_dir, exist_ok=True)
            self.client = chromadb.PersistentClient(path=persist_dir)
            self.collection = self.client.get_or_create_collection(name=collection_name)
            logger.info(f"VectorStore: Initialized collection '{collection_name}' at '{persist_dir}'")
        except Exception as e:
            logger.error(f"Error initializing VectorStore: {e}")
            self.client = None
            self.collection = None

    def add_product(self, product_id: int, text: str, metadata: Optional[dict[str, Any]] = None):
        """Add or update a product document with its embedding in ChromaDB."""
        if not self.collection:
            logger.warning("VectorStore: Collection not initialized, cannot add product.")
            return

        # Sanitize metadata (ChromaDB supports str, int, float, bool)
        clean_metadata: dict[str, Any] = {}
        if metadata:
            for k, v in metadata.items():
                if v is None:
                    continue
                if isinstance(v, (str, int, float, bool)):
                    clean_metadata[k] = v
                elif isinstance(v, (list, tuple, set)):
                    clean_metadata[k] = ", ".join(str(item) for item in v)
                else:
                    clean_metadata[k] = str(v)

        try:
            self.collection.upsert(
                ids=[str(product_id)],
                documents=[text],
                metadatas=[clean_metadata] if clean_metadata else None,
            )
        except Exception as e:
            logger.error(f"Error adding product {product_id} to VectorStore: {e}")

    def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        """Search for top_k most similar products to query text."""
        if not self.collection:
            return []

        try:
            count = self.collection.count()
            if count == 0:
                return []

            n_results = min(top_k, count)
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
            )

            docs: list[dict[str, Any]] = []
            if results and results.get("ids") and len(results["ids"]) > 0:
                ids = results["ids"][0]
                documents = results.get("documents", [[]])[0] if results.get("documents") else []
                metadatas = results.get("metadatas", [[]])[0] if results.get("metadatas") else []
                distances = results.get("distances", [[]])[0] if results.get("distances") else []

                for i, doc_id in enumerate(ids):
                    docs.append({
                        "id": doc_id,
                        "text": documents[i] if i < len(documents) else "",
                        "metadata": metadatas[i] if i < len(metadatas) and metadatas[i] else {},
                        "distance": distances[i] if i < len(distances) else 0.0,
                    })
            return docs
        except Exception as e:
            logger.error(f"Error searching VectorStore: {e}")
            return []

    def delete_product(self, product_id: int):
        """Delete a product embedding by its product ID."""
        if not self.collection:
            return
        try:
            self.collection.delete(ids=[str(product_id)])
        except Exception as e:
            logger.error(f"Error deleting product {product_id} from VectorStore: {e}")

    def get_stats(self) -> dict[str, Any]:
        """Return basic collection statistics."""
        if not self.collection:
            return {"count": 0, "name": "unknown"}
        try:
            return {
                "count": self.collection.count(),
                "name": self.collection.name,
            }
        except Exception as e:
            logger.error(f"Error getting VectorStore stats: {e}")
            return {"count": 0, "name": "unknown"}
