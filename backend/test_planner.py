from planner import create_plan


goal = """
I want to apply for an AI Engineer role.
Analyze my resume, determine my skill match,
identify missing skills, and create a learning plan.
"""


print("\n==============================")
print("CAREERPILOT PLAN")
print("==============================")

plan = create_plan(goal)


print("\nGoal:")
print(plan["goal"])


print("\nSteps:")

for step in plan["steps"]:

    print(
        f"\nStep {step['step_number']}"
    )

    print(
        "Action:",
        step["action"]
    )

    print(
        "Tool:",
        step["tool"]
    )

    print(
        "Reason:",
        step["reason"]
    )