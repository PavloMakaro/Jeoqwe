import os
import json
import math
from typing import List, Dict, Any

class SimpleVectorStore:
    def __init__(self, file_path="data/memory.json", embedding_dim=1536):
        self.file_path = file_path
        self.embedding_dim = embedding_dim
        self.documents = [] # List of {'text': str, 'metadata': dict, 'embedding': list}
        self.load()

    def load(self):
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.documents = data
            except Exception as e:
                print(f"Error loading memory: {e}")
                self.documents = []

    def save(self):
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(self.documents, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving memory: {e}")

    def add(self, text: str, embedding: List[float], metadata: Dict[str, Any] = None):
        if not embedding:
             print("Warning: Attempted to add document without embedding.")
             return

        doc = {
            "text": text,
            "embedding": embedding,
            "metadata": metadata or {}
        }
        self.documents.append(doc)
        self.save()

    def _cosine_similarity(self, v1: List[float], v2: List[float]) -> float:
        """Calculate cosine similarity between two vectors using pure Python."""
        if len(v1) != len(v2):
            return 0.0

        dot_product = sum(a * b for a, b in zip(v1, v2))
        magnitude_v1 = math.sqrt(sum(a * a for a in v1))
        magnitude_v2 = math.sqrt(sum(b * b for b in v2))

        if magnitude_v1 == 0 or magnitude_v2 == 0:
            return 0.0

        return dot_product / (magnitude_v1 * magnitude_v2)

    def search(self, query_embedding: List[float], top_k=3, threshold=0.0) -> List[Dict]:
        if not self.documents:
            return []

        if not query_embedding:
            return []

        results = []
        for doc in self.documents:
            embedding = doc.get("embedding")
            if not embedding or len(embedding) != len(query_embedding):
                continue

            score = self._cosine_similarity(query_embedding, embedding)
            if score >= threshold:
                results.append({
                    "text": doc["text"],
                    "metadata": doc.get("metadata", {}),
                    "score": score
                })

        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)

        return results[:top_k]
