
import os
import json
import time

from dotenv import load_dotenv
from google import genai
from google.genai.errors import ServerError

from schemas import AgentState

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def handle_follow_up(
    user_message: str,
    state: AgentState,
    memory
):

    prompt = f"""
You are CareerPilot, an AI career agent.

The user previously asked for career analysis.

Previous target role:
{state.target_role}

Previous role analysis:
{json.dumps(state.role_analysis, indent=2)}

Previous candidate analysis:
{json.dumps(state.candidate_analysis, indent=2)}

Previous match result:
{json.dumps(state.match_result, indent=2)}

Previous learning plan:
{json.dumps(state.learning_plan, indent=2)}

Previous resume evidence:
{state.resume_evidence}

Conversation history:
{json.dumps(memory.get_history(), indent=2)}

The user now says:
{user_message}

Your task is to answer the user's follow-up question
using the previous CareerPilot state.

IMPORTANT:

1. Do not restart the previous analysis unnecessarily.
2. Do not invent candidate information.
3. Use the previous state as the source of truth.
4. If the user asks about missing skills, use match_result.
5. If the user asks what to learn, use learning_plan.
6. If the user asks about their resume, use resume_evidence.
7. If the user asks for a project, recommend one based on
   their existing skills and missing skills.
8. If the user asks something unrelated to the career analysis,
   answer normally if possible.
9. Keep the response practical and concise.
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
                    f"Follow-up chat using {model} "
                    f"(attempt {attempt + 1}/3)"
                )

                response = client.models.generate_content(
                    model=model,
                    contents=prompt
                )

                if not response.text:
                    raise ValueError(
                        "Gemini returned an empty follow-up response."
                    )

                return response.text.strip()

            except ServerError as error:
                last_error = error
                print(f"Gemini server error: {error}")

                if attempt < 2:
                    time.sleep(2 ** (attempt + 1))

    raise RuntimeError(
        f"Follow-up response failed. "
        f"Models attempted: {models}. Last error: {last_error}"
    )
