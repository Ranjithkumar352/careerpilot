import os
import json

from dotenv import load_dotenv
from google import genai

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

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt
    )

    return response.text