from langchain_core.messages import SystemMessage, HumanMessage
from langchain_google_vertexai import ChatVertexAI
from app.core.state import InterviewState
from app.core.prompts import SYSTEM_PROMPT_TEMPLATE, EVALUATOR_PROMPT, GENERATOR_INSTRUCTION
import os

# Initialize LLM (Shared Resource)
PROJECT_ID = os.getenv("GCP_PROJECT_ID")
REGION = os.getenv("GCP_REGION")
MODEL_ID = os.getenv("VERTEX_MODEL_ID")

llm = ChatVertexAI(
    model_name=MODEL_ID,
    project=PROJECT_ID,
    location=REGION,
    temperature=0.4
)

def node_evaluator(state: InterviewState):
    """
    Step 1: Analyze the user's input silently.
    """
    messages = state["messages"]
    # If this is the very first turn (only 1 message), skip evaluation
    if len(messages) <= 1:
         return {"decision": "START", "critique": "Initial greeting."}

    level = state.get("candidate_level", "Mid-Level")
    topic = state.get("current_topic", "General Architecture")
    
    # Construct Prompt
    eval_prompt = EVALUATOR_PROMPT.format(level=level, topic=topic)
    
    # We only send the last few messages to the evaluator to save context
    # System Instruction + Last AI Question + User Answer
    context_window = [SystemMessage(content=eval_prompt)] + messages[-2:]
    
    response = llm.invoke(context_window)
    content = response.content
    
    # Simple Parsing (Robust enough for MVP)
    decision = "PROBE" # Default
    critique = content
    
    if "DECISION: PASS" in content: decision = "PASS"
    elif "DECISION: FAIL" in content: decision = "FAIL"
    elif "DECISION: PROBE" in content: decision = "PROBE"
    
    # Clean up critique string logic could go here
    
    return {"decision": decision, "critique": critique}

def node_questioner(state: InterviewState):
    """
    Step 2: Generate the response based on the critique.
    """
    messages = state["messages"]
    level = state.get("candidate_level", "Mid-Level")
    topic = state.get("current_topic", "General Architecture")
    
    # Fetch the internal thoughts
    decision = state.get("decision", "START")
    critique = state.get("critique", "None")
    
    # Base System Prompt
    base_prompt = SYSTEM_PROMPT_TEMPLATE.format(level=level, topic=topic, stage="questioning")
    
    # Inject the "Manager's Note"
    if decision != "START":
        instruction = GENERATOR_INSTRUCTION.format(decision=decision, critique=critique)
        base_prompt += f"\n\nINTERNAL GUIDANCE:\n{instruction}"
    
    prompt_messages = [SystemMessage(content=base_prompt)] + messages
    
    response = llm.invoke(prompt_messages)
    
    return {
        "messages": [response],
        "question_count": state.get("question_count", 0) + 1
    }

