from chunker import chunk_resume
from vector_store import VectorStore


resume_text = """
Ranjith Kumar is a Full Stack Developer.

Technical Skills:
JavaScript, React.js, Node.js, Express.js,
MongoDB, Python, Git, REST APIs and JWT.

Experience:
Worked as a Full Stack Developer Intern.
Built web applications using React and Node.js.
Created REST APIs using Express.js and MongoDB.

Projects:
AI Resume Analyzer built using React, Node.js,
MongoDB and Gemini API.

AI Sign Language Recognition System built using
Python, TensorFlow, OpenCV and Flask.
"""


print("\n==============================")
print("RESUME INGESTION")
print("==============================")


# 1. Section-aware chunking

chunks = chunk_resume(resume_text)


print(
    f"\nCreated {len(chunks)} chunks."
)


for index, chunk in enumerate(chunks):

    print(f"\n--- Chunk {index + 1} ---")

    print(
        f"Section: {chunk['section']}"
    )

    print(
        f"Text: {chunk['text']}"
    )


# 2. Create vector store

vector_store = VectorStore()


# 3. Generate embeddings

print("\nGenerating embeddings...")

vector_store.add_documents(chunks)

print("Embeddings stored successfully.")


# 4. Test questions

questions = [

    "What authentication technologies does the candidate know?",

    "What backend technologies does the candidate know?",

    "What AI projects has the candidate built?",

    "What frontend technologies does the candidate know?"
]


# 5. Search

for question in questions:

    print("\n==============================")
    print("QUESTION")
    print("==============================")

    print(question)

    results = vector_store.search(
        query=question,
        top_k=2
    )

    print("\nRelevant chunks:")

    for index, result in enumerate(results):

        print(
            f"\nResult {index + 1}"
        )

        print(
            f"Section: "
            f"{result['section']}"
        )

        print(
            f"Similarity: "
            f"{result['similarity']}"
        )

        print(
            f"Text: "
            f"{result['text']}"
        )