import os
import math

from dotenv import load_dotenv
from google import genai

from embeddings import create_embedding


load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


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


def retrieve_documents(
    query,
    documents,
    top_k=3
):

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


def generate_answer(
    question,
    context
):

    prompt = f"""
You are CareerPilot, an AI career assistant.

Answer the user's question using ONLY the
provided context.

If the context does not contain enough information,
say that the information is not available.

Context:
{context}

Question:
{question}
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt
    )

    return response.text


documents = [
    "Built React applications using JavaScript.",
    "Created REST APIs using Node.js and Express.",
    "Implemented JWT authentication for user login.",
    "Developed machine learning models using Python.",
    "Created responsive web interfaces using HTML and CSS."
]


question = (
    "Does this candidate have "
    "authentication experience?"
)


results = retrieve_documents(
    query=question,
    documents=documents,
    top_k=3
)


print("\n==============================")
print("RETRIEVED CONTEXT")
print("==============================")


for result in results:

    print(
        f"\nSimilarity: "
        f"{result['similarity']}"
    )

    print(
        f"Text: "
        f"{result['text']}"
    )


context = "\n".join(
    result["text"]
    for result in results
)


answer = generate_answer(
    question=question,
    context=context
)


print("\n==============================")
print("RAG ANSWER")
print("==============================")

print(answer)