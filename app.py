import streamlit as st
import uvicorn
import threading
import time
import sys
import os
import requests

# --- This MUST be the first Streamlit command ---
st.set_page_config(
    page_title="AI Financial Assistant",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- Add project root to Python path for imports ---
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

# --- Import FastAPI app and agent functions AFTER potentially modifying sys.path ---
from orchestrator.main import app as fastapi_app
from agents import voice_agent

# --- Configuration for API URL (used by Streamlit part) ---
API_URL = "http://127.0.0.1:8000/query"

# --- Session State Initialization ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hello! Backend is starting. Please wait a few moments..."}]
if "speak_this_response" not in st.session_state:
    st.session_state.speak_this_response = None
if "backend_ready" not in st.session_state:
    st.session_state.backend_ready = False
if "fastapi_thread_started" not in st.session_state:
    st.session_state.fastapi_thread_started = False

# --- FastAPI Server Function ---
def run_fastapi_server():
    print("Attempting to start FastAPI server on http://127.0.0.1:8000...")
    try:
        uvicorn.run(fastapi_app, host="127.0.0.1", port=8000, log_level="info")
    except Exception as e:
        print(f"Error starting FastAPI server: {e}")
        st.session_state.backend_ready = False

def check_backend_status():
    try:
        response = requests.get("http://127.0.0.1:8000/", timeout=1)
        if response.status_code == 200:
            if not st.session_state.backend_ready:
                st.session_state.backend_ready = True
                # Update initial message only if it's the default startup message
                if st.session_state.messages and "Backend is starting" in st.session_state.messages[0]["content"]:
                    st.session_state.messages = [{"role": "assistant", "content": "Hello! How can I help you?"}]
                st.rerun()
            return True
    except requests.exceptions.RequestException:
        return False
    return False

# --- Streamlit UI Helper Functions ---
def get_ai_brief(query: str):
    if not st.session_state.backend_ready:
        return {"error": "Backend server is not ready or unavailable. Please wait."}
    try:
        response = requests.post(API_URL, json={"query": query})
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"API Connection Error: {e}"}

def process_query(query_text):
    if query_text and query_text.strip():
        st.session_state.messages.append({"role": "user", "content": query_text})
        with st.spinner("Thinking..."):
            api_response = get_ai_brief(query_text)
        if "error" in api_response:
            response_text = api_response["error"]
        else:
            response_text = api_response.get("response", "Sorry, I couldn't get a response.")
        st.session_state.messages.append({"role": "assistant", "content": response_text})
        st.session_state.speak_this_response = response_text
        st.rerun()

# --- Streamlit UI Rendering ---
# Minimal CSS just to hide default Streamlit hamburger menu and footer
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

st.title("💼 AI Financial Assistant") # <-- TITLE FIXED

# Display Chat History
# This will be the main scrollable area for messages
# Add a container with a key to ensure it's treated consistently for height
chat_container = st.container()
with chat_container:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

# Speak the latest assistant response
if st.session_state.speak_this_response:
    text_to_speak = st.session_state.speak_this_response
    st.session_state.speak_this_response = None
    time.sleep(0.1) # Small delay for UI to update before sound
    with st.spinner("Preparing audio..."): # This spinner might be very brief
        voice_agent.speak(text_to_speak)
    # Consider if a rerun is needed here to clear the spinner,
    # often not necessary if `speak` is quick.

# --- Inputs at the bottom ---
# The Voice Input Button will appear directly above the text chat_input area
# due to Streamlit's top-down rendering order.
if st.button("🎙️ Ask by Voice", use_container_width=True, key="voice_input_button_bottom", disabled=not st.session_state.backend_ready):
    if st.session_state.backend_ready:
        with st.spinner("Listening..."):
            voice_query = voice_agent.listen_and_transcribe()
            if voice_query and not voice_query.startswith("error:"):
                process_query(voice_query)
            elif voice_query:
                st.error(voice_query)
    else:
        st.warning("Backend is not ready. Please wait.")

# Text Input (st.chat_input is always fixed at the bottom)
if prompt := st.chat_input("Type your question...", disabled=not st.session_state.backend_ready):
    if st.session_state.backend_ready:
        process_query(prompt)
    else:
        st.warning("Backend is not ready. Please wait.")


# --- Logic to start FastAPI and check its status ---
if not st.session_state.fastapi_thread_started:
    print("Preparing to start FastAPI server thread...")
    fastapi_thread = threading.Thread(target=run_fastapi_server, daemon=True)
    fastapi_thread.start()
    st.session_state.fastapi_thread_started = True
    time.sleep(2)

if not st.session_state.backend_ready:
    # Try to check status on each run if not ready
    # This helps update the UI once the backend is up
    if check_backend_status():
        print("Backend confirmed ready by periodic check.")
    else:
        # You can add a st.info or st.warning here if you want a persistent
        # "Backend starting..." message in the UI itself until it's ready.
        # For now, the initial message in st.session_state.messages serves this.
        print("Backend still initializing... Inputs disabled.")