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


texts = [
    "I am a React and Node.js developer.",
    "I build web applications using JavaScript and React.",
    "I enjoy cooking biryani and trying new recipes."
]


print("\nGenerating embeddings...")

embeddings = [
    create_embedding(text)
    for text in texts
]


print("\nEmbedding dimensions:")

for i, embedding in enumerate(embeddings):
    print(f"Text {i + 1}: {len(embedding)}")


similarity_1 = cosine_similarity(
    embeddings[0],
    embeddings[1]
)

similarity_2 = cosine_similarity(
    embeddings[0],
    embeddings[2]
)


print("\n==============================")
print("SEMANTIC SIMILARITY")
print("==============================")

print("\nText 1:")
print(texts[0])

print("\nText 2:")
print(texts[1])

print("\nSimilarity:")
print(similarity_1)


print("\n------------------------------")

print("\nText 1:")
print(texts[0])

print("\nText 3:")
print(texts[2])

print("\nSimilarity:")
print(similarity_2)