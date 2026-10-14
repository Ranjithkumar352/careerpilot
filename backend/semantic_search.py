import math

from embeddings import create_embedding


def cosine_similarity(vector_a, vector_b):

    dot_product = sum(
        a * b
        for a, b in zip(vector_a, vector_b)
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


def semantic_search(query, documents, top_k=3):

    query_embedding = create_embedding(query)

    results = []

    for document in documents:

        document_embedding = create_embedding(
            document
        )

        similarity = cosine_similarity(
            query_embedding,
            document_embedding
        )

        results.append({
            "text": document,
            "similarity": similarity
        })

    results.sort(
        key=lambda item: item["similarity"],
        reverse=True
    )

    return results[:top_k]


documents = [
    "Built React applications using JavaScript.",
    "Created REST APIs using Node.js and Express.",
    "Implemented JWT authentication for user login.",
    "Developed machine learning models using Python.",
    "Created responsive web interfaces using HTML and CSS."
]


query = "Does this candidate have authentication experience?"


results = semantic_search(
    query=query,
    documents=documents,
    top_k=3
)


print("\n==============================")
print("SEMANTIC SEARCH RESULTS")
print("==============================")


for index, result in enumerate(results):

    print(f"\nResult {index + 1}")

    print("Similarity:")
    print(result["similarity"])

    print("Text:")
    print(result["text"])