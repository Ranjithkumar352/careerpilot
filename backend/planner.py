import os

from dotenv import load_dotenv
from google import genai

from schemas import AgentPlan


load_dotenv()


client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def create_plan(user_goal):

    prompt = f"""
You are the planning component of CareerPilot.

User goal:

{user_goal}

Create a practical sequence of steps required
to accomplish this goal.

Available tools:

- analyze_role
- search_resume
- analyze_candidate_skills
- calculate_match
- create_learning_plan

Rules:

- Use only the available tools.
- Do not invent tools.
- Do not execute the tools.
- Only create the plan.
- Steps should be logically ordered.
- A later step may depend on information produced
  by an earlier step.
- Do not include unnecessary steps.
- The target role can be any job role.
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": AgentPlan,
        }
    )

    plan = AgentPlan.model_validate_json(
        response.text
    )

    return plan.model_dump()