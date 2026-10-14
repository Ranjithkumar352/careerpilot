
from typing import TypedDict, Any

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph, START, END

from tools import (
    analyze_role,
    search_resume,
    analyze_candidate_skills,
    calculate_match,
    create_learning_plan,
)


# 1. Shared state passed between graph nodes
class CareerPilotGraphState(TypedDict, total=False):
    role: str
    resume_store_path: str
    role_analysis: dict[str, Any]
    resume_evidence: str
    candidate_analysis: dict[str, Any]
    match_result: dict[str, Any]
    learning_plan: dict[str, Any]
    error: str


# 2. Analyze the selected job role
def role_analysis_node(state: CareerPilotGraphState):
    print("\n🔍 Analyzing role requirements...")

    result = analyze_role(state["role"])

    return {"role_analysis": result}


# 3. Retrieve evidence from the correct resume index
def resume_search_node(state: CareerPilotGraphState):
    print("\n📄 Searching resume evidence...")

    results = search_resume(
        query=(
            f"{state['role']} skills experience "
            "projects technologies"
        ),
        top_k=8,
        store_path=state.get("resume_store_path"),
    )

    evidence = "\n\n".join(
        item.get("text", "")
        for item in results
        if item.get("text")
    ).strip()

    if not evidence:
        print("⚠️ No resume evidence found.")

        return {
            "resume_evidence": "",
            "error": (
                "No relevant resume evidence was found. "
                "Please upload and process a resume first."
            ),
        }

    print("✅ Resume evidence found.")

    return {
        "resume_evidence": evidence,
        "error": "",
    }


# 4. Decide whether to continue
def route_after_resume_search(state: CareerPilotGraphState):
    if (
        state.get("error")
        or not state.get("resume_evidence", "").strip()
    ):
        return "stop"

    return "continue"


# 5. Identify candidate skills
def candidate_analysis_node(state: CareerPilotGraphState):
    print("\n🧠 Analyzing candidate skills...")

    role_skills = state["role_analysis"].get(
        "technical_skills", []
    )

    result = analyze_candidate_skills(
        role=state["role"],
        role_skills=role_skills,
        resume_evidence=state["resume_evidence"],
    )

    return {"candidate_analysis": result}


# 6. Calculate the skill match
def match_node(state: CareerPilotGraphState):
    print("\n📊 Calculating skill match...")

    required_skills = state["role_analysis"].get(
        "technical_skills", []
    )

    candidate_skills = state["candidate_analysis"].get(
        "candidate_skills", []
    )

    result = calculate_match(
        required_skills=required_skills,
        candidate_skills=candidate_skills,
    )

    return {"match_result": result}


# 7. Generate a learning plan
def learning_plan_node(state: CareerPilotGraphState):
    print("\n📝 Creating learning plan...")

    missing_skills = state["match_result"].get(
        "missing_skills", []
    )

    if not missing_skills:
        return {
            "learning_plan": {"learning_plan": []}
        }

    result = create_learning_plan(
        missing_skills=missing_skills
    )

    return {"learning_plan": result}


# 8. Build the LangGraph workflow
def build_careerpilot_graph():
    graph = StateGraph(CareerPilotGraphState)

    graph.add_node("role_analysis", role_analysis_node)
    graph.add_node("resume_search", resume_search_node)
    graph.add_node("candidate_analysis", candidate_analysis_node)
    graph.add_node("match", match_node)
    graph.add_node("learning_plan", learning_plan_node)

    graph.add_edge(START, "role_analysis")
    graph.add_edge("role_analysis", "resume_search")

    graph.add_conditional_edges(
        "resume_search",
        route_after_resume_search,
        {
            "continue": "candidate_analysis",
            "stop": END,
        },
    )

    graph.add_edge("candidate_analysis", "match")
    graph.add_edge("match", "learning_plan")
    graph.add_edge("learning_plan", END)

    checkpointer = InMemorySaver()

    return graph.compile(checkpointer=checkpointer)


careerpilot_graph = build_careerpilot_graph()


# 9. Test the graph independently
if __name__ == "__main__":
    thread_id = "careerpilot-session"

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    result = careerpilot_graph.invoke(
        {
            "role": "AI Engineer",
            # Omit resume_store_path to use the default index.
        },
        config=config,
    )

    print("\n" + "=" * 40)
    print("CAREERPILOT LANGGRAPH RESULTS")
    print("=" * 40)

    if result.get("error"):
        print("\n⚠️", result["error"])
    else:
        print("\nTarget role:", result["role"])
        print("\nMatch result:")
        print(result["match_result"])

        print("\nLearning plan:")
        print(result["learning_plan"])

    saved_state = careerpilot_graph.get_state(config)

    print("\n" + "=" * 40)
    print("LANGGRAPH CHECKPOINT")
    print("=" * 40)
    print("Thread ID:", thread_id)
    print("Saved role:", saved_state.values.get("role"))
    print("Checkpoint exists:", bool(saved_state.config))
