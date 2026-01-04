from dotenv import load_dotenv
load_dotenv()

from langchain_core.messages import HumanMessage
from app.agent import app as agent_app

print("🤖 SYSTEM DESIGN INTERVIEWER (CLI MODE)")
print("Type 'quit' to exit.")

# Initial State
state = {
    "messages": [HumanMessage(content="Hi, I'm ready for the interview.")],
    "candidate_level": "Senior Engineer",
    "current_topic": "Load Balancers",
    "interview_stage": "questioning",
    "question_count": 0,
    "feedback_log": []
}

while True:
    # Run the Agent
    # The agent processes the history and generates a response
    for event in agent_app.stream(state):
        for key, value in event.items():
            if "messages" in value:
                last_msg = value["messages"][-1]
                print(f"\nAI: {last_msg.content}")
                
                # Update our local state simulation with the AI's response
                state["messages"].append(last_msg)
                state["question_count"] = value.get("question_count", state["question_count"])

    # Get User Input
    user_input = input("\nYou: ")
    if user_input.lower() in ["quit", "exit"]:
        break
    
    # Update State with User Input
    state["messages"].append(HumanMessage(content=user_input))

    