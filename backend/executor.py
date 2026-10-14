from schemas import AgentState
from tools import (
    analyze_role,
    search_resume,
    analyze_candidate_skills,
    calculate_match,
    create_learning_plan,
)


# All CareerPilot tools
TOOL_REGISTRY = {
    "analyze_role": analyze_role,
    "search_resume": search_resume,
    "analyze_candidate_skills": analyze_candidate_skills,
    "calculate_match": calculate_match,
    "create_learning_plan": create_learning_plan,
}


def execute_tool(tool_name, state):
    """
    Execute one tool based on the current AgentState.
    """

    if tool_name not in TOOL_REGISTRY:
        raise ValueError(f"Unknown tool: {tool_name}")

    # --------------------------------------------------
    # Prepare tool arguments from current state
    # --------------------------------------------------

    if tool_name == "analyze_role":

        return TOOL_REGISTRY[tool_name](
            role=state.target_role
        )

    elif tool_name == "search_resume":

        return TOOL_REGISTRY[tool_name](
            query=f"{state.target_role} skills experience projects technologies",
            top_k=5
        )

    elif tool_name == "analyze_candidate_skills":

        return TOOL_REGISTRY[tool_name](
            role=state.target_role,
            role_skills=state.role_analysis["technical_skills"],
            resume_evidence=state.resume_evidence
        )

    elif tool_name == "calculate_match":

        return TOOL_REGISTRY[tool_name](
            required_skills=state.role_analysis["technical_skills"],
            candidate_skills=state.candidate_analysis["candidate_skills"]
        )

    elif tool_name == "create_learning_plan":

        return TOOL_REGISTRY[tool_name](
            missing_skills=state.match_result["missing_skills"]
        )


def update_state(tool_name, result, state):
    """
    Store the result of a tool execution inside AgentState.
    """

    if tool_name == "analyze_role":

        state.role_analysis = result

    elif tool_name == "search_resume":

        state.resume_evidence = "\n\n".join(
            item["text"] for item in result
        )

    elif tool_name == "analyze_candidate_skills":

        state.candidate_analysis = result

    elif tool_name == "calculate_match":

        state.match_result = result

    elif tool_name == "create_learning_plan":

        state.learning_plan = result

    return state


def execute_plan(plan, state):
    """
    Execute the complete agent plan.
    """

    print("\n==============================")
    print("EXECUTING CAREERPILOT PLAN")
    print("==============================")

    for step in plan["steps"]:

        print(
            f"\n▶ Step {step['step_number']}: "
            f"{step['action']}"
        )

        tool_name = step["tool"]

        print(f"Tool: {tool_name}")

        # Execute tool
        result = execute_tool(
            tool_name,
            state
        )

        # Store result in state
        state = update_state(
            tool_name,
            result,
            state
        )

        print(
            f"✅ {tool_name} completed."
        )

    return state