from schemas import AgentState


class ConversationMemory:

    def __init__(self):
        self.messages = []
        self.state: AgentState | None = None

    def add_user_message(self, message):
        self.messages.append({
            "role": "user",
            "content": message
        })

    def add_assistant_message(self, message):
        self.messages.append({
            "role": "assistant",
            "content": message
        })

    def save_state(self, state: AgentState):
        self.state = state

    def get_state(self):
        return self.state

    def get_history(self):
        return self.messages

    def clear(self):
        self.messages = []
        self.state = None