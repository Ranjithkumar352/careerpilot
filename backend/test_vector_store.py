from vector_store import VectorStore


documents = [
    "Built React applications using JavaScript.",
    "Created REST APIs using Node.js and Express.",
    "Implemented JWT authentication for user login.",
    "Developed machine learning models using Python.",
    "Created responsive web interfaces using HTML and CSS."
]


print("\nCreating vector store...")

store = VectorStore()


print("\nGenerating document embeddings...")

store.add_documents(documents)


print("\nVector store created.")


query = "Does this candidate have authentication experience?"


print("\nSearching...")

results = store.search(
    query=query,
    top_k=3
)


print("\n==============================")
print("SEARCH RESULTS")
print("==============================")


for index, result in enumerate(results):

    print(f"\nResult {index + 1}")

    print(
        f"Similarity: "
        f"{result['similarity']}"
    )

    print(
        f"Text: "
        f"{result['text']}"
    )