from google import genai
from dotenv import load_dotenv
import os
import json


load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def generate_final_response(state):

    prompt = f"""
You are CareerPilot, an AI career advisor.

The user asked:

{state.goal}

The target role extracted from the user's request is:

{state.target_role}

You have completed an agent workflow.

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

1. The MATCH RESULT is authoritative for the match percentage,
   matched skills, and missing skills.

2. NEVER invent additional missing skills.

3. Only list missing skills that appear inside:
   MATCH RESULT -> missing_skills

4. Only list matched skills that appear inside:
   MATCH RESULT -> matched_skills

5. Use CANDIDATE ANALYSIS to explain the evidence for matched skills.

6. Use RESUME EVIDENCE only to support claims about the candidate.

7. Do not claim the candidate has a technology unless it is
   supported by the supplied candidate analysis or resume evidence.

8. Do not add technologies such as Data Pipelines, AWS,
   Kubernetes, PyTorch, TensorFlow, MLOps, etc. unless they
   actually appear in the supplied data.

9. Do not change the calculated match percentage.

10. If the evidence is insufficient, explicitly say:
    "The resume does not provide clear evidence for this."

11. Do not make up experience.

12. Do not introduce new requirements that were not returned
    by the role analysis.


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

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt
    )

    return response.text