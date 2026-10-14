from chunker import chunk_text


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


chunks = chunk_text(
    resume_text,
    max_words=40,
    overlap_words=10
)


print("\n==============================")
print("RESUME CHUNKS")
print("==============================")


for index, chunk in enumerate(chunks):

    print(f"\n--- Chunk {index + 1} ---")
    print(chunk)

    print(
        f"\nWord count: "
        f"{len(chunk.split())}"
    )