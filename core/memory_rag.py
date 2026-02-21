import os
import traceback
from core.memory.vector_store import SimpleVectorStore
from core.llm import LLMService

class VectorMemory:
    def __init__(self, collection_name="user_facts", persist_path="data/memory.json"):
        self.enabled = True
        self.store = SimpleVectorStore(file_path=persist_path)
        self.llm = LLMService() # We need this for embeddings

    async def add(self, text, metadata=None):
        try:
            # Generate embedding
            embedding = await self.llm.get_embedding(text)
            if not embedding:
                return "Failed to generate embedding."

            # Add to store
            self.store.add(text, embedding, metadata)
            return "Fact stored in vector memory."
        except Exception as e:
            return f"Error adding to vector memory: {e}"

    async def search(self, query, n_results=3):
        try:
            # Generate embedding for query
            embedding = await self.llm.get_embedding(query)
            if not embedding:
                return []

            # Search
            results = self.store.search(embedding, top_k=n_results, threshold=0.4)

            # Format results for the caller (just return text list for now to match old interface roughly)
            return [r["text"] for r in results]
        except Exception as e:
            print(f"Error searching vector memory: {e}")
            return []

# Singleton instance
memory_instance = VectorMemory()
