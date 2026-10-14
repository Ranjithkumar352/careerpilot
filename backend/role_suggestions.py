import os
import json

from dotenv import load_dotenv
from google import genai

from schemas import RoleSuggestionsOutput


load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def suggest_roles(resume_evidence: str):

    prompt = f"""
You are CareerPilot, an AI career advisor.

Analyze the candidate's resume and suggest the most suitable
job roles for this candidate.

RESUME EVIDENCE:

{resume_evidence}


Suggest 4 realistic roles based ONLY on the resume.

Possible roles may include:
- Frontend Developer
- Backend Developer
- Full Stack Developer
- AI Engineer
- Machine Learning Engineer
- Data Scientist
- Software Engineer
- GenAI Engineer

But do not force these roles.

Choose roles that are actually supported by the resume.

For every role provide:
1. Role name
2. Short reason explaining why the resume supports that role

IMPORTANT:

- Do not invent technologies.
- Do not assume experience that is not present.
- Base suggestions on actual resume evidence.
- Prefer realistic roles for the candidate's current experience level.
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": RoleSuggestionsOutput,
        }
    )

    result = RoleSuggestionsOutput.model_validate_json(
        response.text
    )

    return result.model_dump()