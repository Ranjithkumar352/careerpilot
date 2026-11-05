
from google import genai
from google.genai.errors import ServerError
from dotenv import load_dotenv
import os
import json
import time

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def generate_final_response(state):

    prompt = f"""
You are CareerPilot, an AI career advisor.

The user asked:
{state.goal}

Target role:
{state.target_role}

ROLE REQUIREMENTS:
{json.dumps(state.role_analysis, indent=2)}

CANDIDATE ANALYSIS:
{json.dumps(state.candidate_analysis, indent=2)}

MATCH RESULT:
{json.dumps(state.match_result, indent=2)}

LEARNING PLAN:
{json.dumps(state.learning_plan, indent=2)}

RESUME EVIDENCE:
{state.resume_evidence}

IMPORTANT GROUNDING RULES:

1. MATCH RESULT is authoritative for match percentage,
   matched skills, and missing skills.
2. Never invent additional missing skills.
3. Only list skills present in MATCH RESULT.
4. Use CANDIDATE ANALYSIS to explain matched skills.
5. Use RESUME EVIDENCE to support candidate claims.
6. Do not invent experience or technologies.
7. Do not change the calculated match percentage.
8. If evidence is insufficient, say:
   "The resume does not provide clear evidence for this."
9. Do not introduce requirements absent from ROLE ANALYSIS.

Generate a concise but useful career analysis.

Use exactly this structure:

# CareerPilot Analysis

## Target Role

## Overall Match

## Skills You Already Have

## Resume Evidence

## Missing or Unsupported Skills

## What You Should Learn First

## Recommended Next Steps
"""

    primary_model = os.getenv(
        "GEMINI_MODEL", "gemini-3.5-flash-lite"
    )

    fallback_model = os.getenv(
        "GEMINI_FALLBACK_MODEL", "gemini-3.5-flash"
    )

    models = list(dict.fromkeys([primary_model, fallback_model]))
    last_error = None

    for model in models:
        for attempt in range(3):
            try:
                print(
                    f"Generating final response using {model} "
                    f"(attempt {attempt + 1}/3)"
                )

                response = client.models.generate_content(
                    model=model,
                    contents=prompt
                )

                if not response.text:
                    raise ValueError(
                        "Gemini returned an empty final response."
                    )

                return response.text

            except ServerError as error:
                last_error = error
                print(f"Gemini server error: {error}")

                if attempt < 2:
                    time.sleep(2 ** (attempt + 1))

    raise RuntimeError(
        f"Final response generation failed. "
        f"Models attempted: {models}. Last error: {last_error}"
    )
