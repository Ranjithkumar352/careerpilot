from vector_store import VectorStore


vector_store = VectorStore()

print("\n📚 Loading saved resume knowledge base...")

vector_store.load()

print("\n🔎 Searching resume...")

results = vector_store.search(
    query="What experience does the candidate have with authentication?",
    top_k=3
)

for index, result in enumerate(results, start=1):

    print(f"\nResult {index}")
    print("Section:", result["section"])
    print("Similarity:", result["similarity"])
    print("Text:", result["text"])