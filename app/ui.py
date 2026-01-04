import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from app.agent import app as agent_app

# --- PAGE CONFIG ---
st.set_page_config(page_title="System Design Interviewer", page_icon="🤖")

st.title("🤖 System Design Interviewer")
st.markdown("""
**Role:** Principal Software Architect (Google)  
**Goal:** Assess your ability to design scalable systems.
""")

# --- INITIALIZE SESSION STATE ---
if "messages" not in st.session_state:
    # Initial Trigger: The user "sits down" for the interview
    # We silently seed this so the AI starts the conversation
    st.session_state.messages = []
    st.session_state.started = False
    st.session_state.critique = None
    st.session_state.decision = None

# --- SIDEBAR ---
with st.sidebar:
    st.header("Interviewer Brain")
    if st.session_state.critique:
        st.info(f"**Critique:** {st.session_state.critique}")
        st.success(f"**Decision:** {st.session_state.decision}")
    else:
        st.markdown("*Waiting for input...*")
        
    st.divider()
    st.caption("Powered by LangGraph & Gemini 2.5 Pro")

# --- START LOGIC ---
# If the interview hasn't started, kick it off
if not st.session_state.started:
    with st.spinner("Reviewing your resume..."):
        # We invoke the agent with a dummy start signal to get the greeting
        initial_state = {
            "messages": [HumanMessage(content="Hi, I am ready for the interview.")],
            "candidate_level": "Senior Engineer",
            "current_topic": "Distributed Systems",
            "question_count": 0
        }
        
        # Run the Graph
        final_state = agent_app.invoke(initial_state)
        
        # Capture the AI's opening line
        ai_msg = final_state["messages"][-1]
        st.session_state.messages.append(ai_msg)
        st.session_state.started = True
        st.rerun()

# --- DISPLAY CHAT HISTORY ---
for msg in st.session_state.messages:
    # Skip the hidden "Hi, I am ready" trigger message if you want, 
    # but showing it establishes context. Let's filter purely SystemMessages.
    if isinstance(msg, SystemMessage):
        continue
        
    role = "user" if isinstance(msg, HumanMessage) else "assistant"
    with st.chat_message(role):
        st.markdown(msg.content)

# --- CHAT INPUT ---
if user_input := st.chat_input("Your answer..."):
    # 1. Display User Message
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append(HumanMessage(content=user_input))

    # 2. Run Agent Logic
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            # Construct the state payload
            # We pass the full history to keep context
            current_state = {
                "messages": st.session_state.messages,
                "candidate_level": "Senior Engineer",
                "current_topic": "Distributed Systems",
                "question_count": len(st.session_state.messages) # Approx metric
            }
            
            # INVOKE THE GRAPH
            # The graph runs Evaluator -> Interviewer -> End
            result = agent_app.invoke(current_state)
            
            # Extract Response
            ai_msg = result["messages"][-1]
            st.markdown(ai_msg.content)
            
            # Extract "Thought Bubble" Data
            st.session_state.critique = result.get("critique", "No critique")
            st.session_state.decision = result.get("decision", "PASS")
            
            # Update History
            st.session_state.messages.append(ai_msg)
            
            # Force a rerun to update the Sidebar immediately
            st.rerun()

