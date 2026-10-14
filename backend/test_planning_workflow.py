from planner import create_plan
from executor import execute_plan
from schemas import AgentState
from response_generator import generate_final_response
from role_extractor import extract_target_role


# ==========================================================
# USER GOAL
# ==========================================================

goal = """
I want to apply for an AI Engineer role.

Analyze my resume, determine my skill match,
identify missing skills, and create a learning plan.
"""


# ==========================================================
# STEP 1: EXTRACT TARGET ROLE
# ==========================================================

print("\n==============================")
print("STEP 1: EXTRACT TARGET ROLE")
print("==============================")

target_role = extract_target_role(goal)

print(f"🎯 Target Role: {target_role}")


# ==========================================================
# STEP 2: CREATE PLAN
# ==========================================================

print("\n==============================")
print("STEP 2: CREATE PLAN")
print("==============================")

plan = create_plan(goal)

print("\nPlan created:")

for step in plan["steps"]:
    print(
        f"{step['step_number']}. "
        f"{step['action']} "
        f"→ {step['tool']}"
    )


# ==========================================================
# STEP 3: CREATE STATE
# ==========================================================

print("\n==============================")
print("STEP 3: CREATE STATE")
print("==============================")

state = AgentState(
    goal=goal,
    target_role=target_role
)

print("✅ Agent state created.")


# ==========================================================
# STEP 4: EXECUTE PLAN
# ==========================================================

print("\n==============================")
print("STEP 4: EXECUTE PLAN")
print("==============================")

final_state = execute_plan(
    plan,
    state
)


# ==========================================================
# STEP 5: GENERATE FINAL RESPONSE
# ==========================================================

print("\n==============================")
print("STEP 5: GENERATE FINAL RESPONSE")
print("==============================")

final_response = generate_final_response(
    final_state
)


# ==========================================================
# FINAL RESPONSE
# ==========================================================

print("\n==============================")
print("CAREERPILOT FINAL RESPONSE")
print("==============================")

print(final_response)