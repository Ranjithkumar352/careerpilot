import os

from dotenv import load_dotenv
from google import genai

from schemas import TargetRoleOutput


load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def extract_target_role(goal: str) -> str:

    prompt = f"""
Extract the target job role from the user's request.

User request:
{goal}

Return the role the user wants to apply for.

Examples:

"I want to apply for an AI Engineer role"
→ AI Engineer

"I want to become a frontend developer"
→ Frontend Developer

"I am looking for backend developer jobs"
→ Backend Developer

"I want to apply for data scientist positions"
→ Data Scientist

Rules:

1. Return only the target job role.
2. Do not include explanations.
3. Do not invent a role that is not supported by the request.
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": TargetRoleOutput,
        }
    )

    result = TargetRoleOutput.model_validate_json(
        response.text
    )

    return result.role