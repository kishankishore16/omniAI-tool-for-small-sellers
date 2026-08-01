"""
ChromaDB vector store wrapper.
"""
import chromadb

class VectorStore:
    def __init__(self, persist_dir: str, collection_name: str):
        try:
            self.client = chromadb.PersistentClient(path=persist_dir)
            self.collection = self.client.get_or_create_collection(name=collection_name)
        except Exception as e:
            print(f"Error initializing VectorStore: {e}")
            self.client = None
            self.collection = None

    def add_product(self, product_id: int, text: str, metadata: dict):
        if not self.collection:
            return
        try:
            self.collection.upsert(
                ids=[str(product_id)],
                documents=[text],
                metadatas=[metadata]
            )
        except Exception as e:
            print(f"Error adding product to VectorStore: {e}")

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        if not self.collection:
            return []
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=top_k
            )
            
            docs = []
            if results and results.get('ids') and len(results['ids']) > 0:
                for i in range(len(results['ids'][0])):
                    docs.append({
                        'id': results['ids'][0][i],
                        'text': results['documents'][0][i] if results.get('documents') else '',
                        'metadata': results['metadatas'][0][i] if results.get('metadatas') else {},
                        'distance': results['distances'][0][i] if results.get('distances') else 0.0
                    })
            return docs
        except Exception as e:
            print(f"Error searching VectorStore: {e}")
            return []

    def delete_product(self, product_id: int):
        if not self.collection:
            return
        try:
            self.collection.delete(ids=[str(product_id)])
        except Exception as e:
            print(f"Error deleting product from VectorStore: {e}")

    def get_stats(self) -> dict:
        if not self.collection:
            return {'count': 0, 'name': 'unknown'}
        try:
            return {
                'count': self.collection.count(),
                'name': self.collection.name
            }
        except Exception as e:
            print(f"Error getting VectorStore stats: {e}")
            return {'count': 0, 'name': 'unknown'}
