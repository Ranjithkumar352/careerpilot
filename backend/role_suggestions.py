
import os
import json
import time

from dotenv import load_dotenv
from google import genai

from schemas import RoleSuggestionsOutput

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

PRIMARY_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.5-flash-lite"
)

FALLBACK_MODEL = os.getenv("GEMINI_FALLBACK_MODEL")


def generate_role_suggestions(model, prompt):

    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": RoleSuggestionsOutput,
        }
    )

    if not response.text:
        raise ValueError("Gemini returned an empty response.")

    result = RoleSuggestionsOutput.model_validate_json(
        response.text
    )

    return result.model_dump()


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

    last_error = None

    # Try the primary model up to 3 times.
    for attempt in range(3):
        try:
            print(
                f"🤖 Trying Gemini model: {PRIMARY_MODEL} "
                f"(Attempt {attempt + 1}/3)"
            )

            return generate_role_suggestions(
                PRIMARY_MODEL,
                prompt
            )

        except Exception as exc:
            last_error = exc
            error_message = str(exc).lower()

            is_temporary = any(
                term in error_message
                for term in [
                    "503",
                    "unavailable",
                    "high demand",
                    "429",
                    "resource_exhausted",
                    "500",
                    "internal"
                ]
            )

            if not is_temporary:
                raise

            if attempt < 2:
                wait_time = 2 ** (attempt + 1)

                print(
                    f"⚠️ Gemini temporarily unavailable. "
                    f"Retrying in {wait_time} seconds..."
                )

                time.sleep(wait_time)

    # Try the fallback model if configured.
    if FALLBACK_MODEL and FALLBACK_MODEL != PRIMARY_MODEL:

        print(f"🔄 Switching to fallback model: {FALLBACK_MODEL}")

        try:
            return generate_role_suggestions(
                FALLBACK_MODEL,
                prompt
            )

        except Exception as exc:
            last_error = exc
            print(f"❌ Fallback model also failed: {exc}")

    raise RuntimeError(
        f"Gemini role generation failed after retries: {last_error}"
    )
