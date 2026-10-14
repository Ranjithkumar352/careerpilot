
from schemas import AgentState

from langgraph_agent import build_careerpilot_graph
from response_generator import generate_final_response
from resume_ready import prepare_resume_for_careerpilot
from role_selection import select_role


class CareerPilotAgent:

    def __init__(
        self,
        resume_store_path=None,
        thread_id="careerpilot-session"
    ):
        self.state = AgentState(phase="resume_ready")

        # Resume index created from the uploaded PDF
        self.resume_store_path = resume_store_path

        # Separate conversation checkpoint for each session
        self.thread_id = thread_id

        # Build the LangGraph workflow
        self.graph = build_careerpilot_graph()

    # ======================================================
    # RESUME STAGE
    # ======================================================

    def initialize_from_resume(self):

        print("\n🤖 CareerPilot is understanding your resume...")

        resume_data = prepare_resume_for_careerpilot(
            store_path=self.resume_store_path
        )

        self.state.resume_evidence = resume_data["resume_evidence"]
        self.state.suggested_roles = resume_data["suggested_roles"]
        self.state.phase = "waiting_for_role"

        return self.state

    # ======================================================
    # ROLE SUGGESTIONS
    # ======================================================

    def display_roles(self):

        print("\n")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("🎯  ROLES THAT MATCH YOUR PROFILE")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        for index, role in enumerate(
            self.state.suggested_roles,
            start=1
        ):
            print(f"\n{index}. {role['role']}")
            print(f"   {role['reason']}")

        print("\n💬 Which role would you like to apply for?")

    # ======================================================
    # ROLE SELECTION
    # ======================================================

    def choose_role(self, user_message):

        selected_role = select_role(
            user_message,
            self.state.suggested_roles
        )

        if not selected_role:
            return False

        self.state.target_role = selected_role
        self.state.phase = "planning"

        return True

    # ======================================================
    # LANGGRAPH ANALYSIS
    # ======================================================

    def analyze_role(self):

        goal = f"""
I want to apply for the {self.state.target_role} role.

Analyze my resume against this role.
Determine my existing skills, missing skills, match percentage,
resume evidence, and recommended learning priorities.
"""

        self.state.goal = goal

        print("\n")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("🧠  CAREERPILOT IS WORKING")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        print(f"\n🎯 Target Role: {self.state.target_role}")
        print("\n🚀 Running the LangGraph workflow...\n")

        self.state.phase = "executing"

        config = {
            "configurable": {
                "thread_id": self.thread_id
            }
        }

        # Pass the uploaded resume index into LangGraph
        result = self.graph.invoke(
            {
                "role": self.state.target_role,
                "resume_store_path": self.resume_store_path,
            },
            config=config
        )

        # Handle missing resume evidence
        if result.get("error"):
            self.state.phase = "error"
            print(f"\n⚠️ {result['error']}")
            return self.state

        # Transfer LangGraph results into AgentState
        self.state.role_analysis = result.get("role_analysis")
        self.state.resume_evidence = result.get("resume_evidence")
        self.state.candidate_analysis = result.get("candidate_analysis")
        self.state.match_result = result.get("match_result")
        self.state.learning_plan = result.get("learning_plan")

        self.state.phase = "completed"

        print("\n✅ LangGraph analysis completed!")

        return self.state

    # ======================================================
    # FINAL RESPONSE
    # ======================================================

    def generate_response(self):

        if self.state.phase == "error":
            return (
                "I couldn't complete the analysis because resume "
                "evidence was unavailable. Please check your resume "
                "index and try again."
            )

        print("\n📝 Preparing CareerPilot recommendations...")

        response = generate_final_response(self.state)

        return response

    # ======================================================
    # COMPLETE ROLE WORKFLOW
    # ======================================================

    def process_role(self, user_message):

        if not self.choose_role(user_message):
            return None

        print(f"\n🎯 Selected Role: {self.state.target_role}")

        self.analyze_role()

        response = self.generate_response()

        return response
