import json
import math
import os

from embeddings import create_embedding


DEFAULT_STORE_PATH = "data/resume_index.json"


def cosine_similarity(vector_a, vector_b):

    dot_product = sum(
        a * b for a, b in zip(vector_a, vector_b)
    )

    magnitude_a = math.sqrt(
        sum(a * a for a in vector_a)
    )

    magnitude_b = math.sqrt(
        sum(b * b for b in vector_b)
    )

    if magnitude_a == 0 or magnitude_b == 0:
        return 0

    return dot_product / (
        magnitude_a * magnitude_b
    )


class VectorStore:

    def __init__(self, store_path=DEFAULT_STORE_PATH):

        self.store_path = store_path
        self.documents = []

    def add_documents(self, documents):

        for document in documents:

            embedding = create_embedding(
                document["text"]
            )

            self.documents.append({
                "text": document["text"],
                "section": document["section"],
                "embedding": embedding
            })

    def save(self):

        directory = os.path.dirname(self.store_path)

        if directory:
            os.makedirs(directory, exist_ok=True)

        with open(
            self.store_path,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                self.documents,
                file,
                ensure_ascii=False
            )

        print(
            f"💾 Vector store saved to: {self.store_path}"
        )

    def load(self):

        if not os.path.exists(self.store_path):

            raise FileNotFoundError(
                f"Vector store not found: {self.store_path}"
            )

        with open(
            self.store_path,
            "r",
            encoding="utf-8"
        ) as file:

            self.documents = json.load(file)

        print(
            f"📚 Loaded {len(self.documents)} documents "
            f"from vector store."
        )

    def search(self, query, top_k=3):

        if not self.documents:

            raise ValueError(
                "Vector store is empty. "
                "Add or load documents first."
            )

        query_embedding = create_embedding(query)

        results = []

        for document in self.documents:

            similarity = cosine_similarity(
                query_embedding,
                document["embedding"]
            )

            results.append({
                "text": document["text"],
                "section": document["section"],
                "similarity": similarity
            })

        results.sort(
            key=lambda item: item["similarity"],
            reverse=True
        )

        return results[:top_k]