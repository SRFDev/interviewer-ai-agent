import os
import sys
from dotenv import load_dotenv

# Load env vars
load_dotenv()

project_id = os.getenv("GCP_PROJECT_ID")
region = os.getenv("GCP_REGION")
model_id = os.getenv("VERTEX_MODEL_ID")

print(f"📡 Testing Connectivity for Project: {project_id} [{region}]...")

try:
    # --- TEST 1: VERTEX AI (The Brain) ---
    print("\n🧠 1. Testing Vertex AI (Gemini)...")
    from langchain_google_vertexai import ChatVertexAI

    llm = ChatVertexAI(
        model_name=model_id,
        project=project_id,
        location=region,
        temperature=0
    )
    
    response = llm.invoke("Hello! Are you online? Reply with 'System Online'.")
    print(f"   ✅ Vertex Response: {response.content}")

    # --- TEST 2: FIRESTORE (The Memory) ---
    print("\n💾 2. Testing Firestore (Memory)...")
    from google.cloud import firestore
    from langchain_google_firestore import FirestoreChatMessageHistory

    # Initialize Client
    client = firestore.Client(project=project_id, database="(default)")
    
    # Create a test session
    session_id = "test_session_v1"
    history = FirestoreChatMessageHistory(
        session_id=session_id,
        collection="chat_history",
        client=client
    )

    # Write
    history.add_user_message("Test Message")
    history.add_ai_message("Test Response")
    print(f"   ✅ Wrote to Firestore collection 'chat_history' session '{session_id}'")

    # Read
    stored_messages = history.messages
    print(f"   ✅ Read {len(stored_messages)} messages from Firestore.")
    
    # Cleanup (Optional)
    history.clear()
    print("   ✅ Test data cleared.")

    print("\n🎉 INFRASTRUCTURE VERIFIED. Ready to build the Agent.")

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    print("Tip: Did you enable the Vertex AI and Firestore APIs in the Console?")
    sys.exit(1)
    