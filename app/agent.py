from langgraph.graph import StateGraph, END
from app.core.state import InterviewState
from app.core.nodes import node_evaluator, node_questioner

# --- GRAPH CONSTRUCTION ---

workflow = StateGraph(InterviewState)

# 1. Add Nodes
workflow.add_node("evaluator", node_evaluator)
workflow.add_node("interviewer", node_questioner)

# 2. Define Flow
# Entry: User Input -> Evaluator (The "Brain")
workflow.set_entry_point("evaluator")

# Evaluator -> Interviewer (The "Mouth")
workflow.add_edge("evaluator", "interviewer")

# Interviewer -> End of Turn (Yield back to user)
workflow.add_edge("interviewer", END)

# 3. Compile
app = workflow.compile()