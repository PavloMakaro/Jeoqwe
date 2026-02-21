import os
import unittest
from core.memory.vector_store import SimpleVectorStore

class TestVectorStore(unittest.TestCase):
    def setUp(self):
        self.test_file = "data/test_memory_unittest.json"
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
        self.store = SimpleVectorStore(file_path=self.test_file)

    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_add_and_search(self):
        self.store.add("Hello world", [0.1, 0.2, 0.3], {"id": 1})
        self.store.add("Python is great", [0.9, 0.1, 0.0], {"id": 2})
        self.store.add("AI is future", [0.8, 0.2, 0.1], {"id": 3})

        # Test Search
        results = self.store.search([0.9, 0.1, 0.0], top_k=1)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["text"], "Python is great")

        # Test Persistence
        self.store.save()
        store2 = SimpleVectorStore(file_path=self.test_file)
        self.assertEqual(len(store2.documents), 3)

if __name__ == "__main__":
    unittest.main()
