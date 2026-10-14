import os

from dotenv import load_dotenv
from google import genai


load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def create_embedding(text):
    response = client.models.embed_content(
        model="gemini-embedding-001",
        contents=text
    )

    return response.embeddings[0].values


if __name__ == "__main__":

    text = """
    Ranjith is a Full Stack Developer with experience
    in React.js, Node.js, Express.js, MongoDB and Python.
    """

    embedding = create_embedding(text)

    print("Text:")
    print(text)

    print("\nEmbedding dimension:")
    print(len(embedding))

    print("\nFirst 10 values:")
    print(embedding[:10])