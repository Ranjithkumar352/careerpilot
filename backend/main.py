from agent import CareerPilotAgent
from memory import ConversationMemory
from follow_up import handle_follow_up


def main():

    print("\n")
    print("╔══════════════════════════════════════╗")
    print("║          🤖 CAREERPILOT              ║")
    print("║      AI Career Intelligence Agent     ║")
    print("╚══════════════════════════════════════╝")

    memory = ConversationMemory()

    agent = CareerPilotAgent()

    # ======================================================
    # RESUME READY
    # ======================================================

    print("\n📄 Resume detected.")
    print("🔍 Parsing and understanding resume...")

    agent.initialize_from_resume()

    print("\n✅ Resume parsed successfully!")

    agent.display_roles()

    # ======================================================
    # MAIN CONVERSATION
    # ======================================================

    while True:

        user_message = input(
            "\nYou:\n> "
        ).strip()

        if not user_message:
            continue

        if user_message.lower() in {
            "exit",
            "quit"
        }:

            print(
                "\n👋 Thanks for using CareerPilot!"
            )

            break

        # ==================================================
        # ROLE SELECTION
        # ==================================================

        if agent.state.phase == "waiting_for_role":

            memory.add_user_message(
                user_message
            )

            response = agent.process_role(
                user_message
            )

            if response is None:

                print(
                    "\n⚠️ I couldn't identify that role."
                )

                print(
                    "Please choose one of the suggested "
                    "roles or type another valid role."
                )

                continue

            memory.save_state(
                agent.state
            )

            memory.add_assistant_message(
                response
            )

            print("\n")
            print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            print("🤖 CAREERPILOT")
            print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

            print(response)

            continue

        # ==================================================
        # FOLLOW-UP CONVERSATION
        # ==================================================

        if agent.state.phase == "completed":

            print(
                "\n🧠 CareerPilot is using your previous "
                "career analysis..."
            )

            memory.add_user_message(
                user_message
            )

            response = handle_follow_up(
                user_message=user_message,
                state=agent.state,
                memory=memory
            )

            memory.add_assistant_message(
                response
            )

            print("\nCareerPilot:")
            print(response)

            continue


if __name__ == "__main__":
    main()