import streamlit as st
import uvicorn
import threading
import time
import sys
import os
import requests
from streamlit_mic_recorder import mic_recorder # <-- IMPORT THE NEW COMPONENT

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
    st.session_state.messages = [{"role": "assistant", "content": "Hello! Backend is starting. Please wait..."}]
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
        return {"error": "Backend server is not ready. Please wait."}
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
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

st.title("💼 AI Financial Assistant")

# Display Chat History
chat_container = st.container()
with chat_container:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

# Speak the latest assistant response
if st.session_state.speak_this_response:
    text_to_speak = st.session_state.speak_this_response
    st.session_state.speak_this_response = None
    time.sleep(0.1)
    with st.spinner("Preparing audio..."):
        voice_agent.speak(text_to_speak)

# --- Inputs at the bottom ---

# --- Voice Input using streamlit-mic-recorder ---
st.write("---") # A small separator
st.write("🎤 **Ask by Voice:**")
audio_data = mic_recorder(
    start_prompt="🔴 Click to Record",
    stop_prompt="⏹️ Click to Stop",
    just_once=True, # Record only once per interaction
    use_container_width=True,
    key='voice_recorder'
)

if audio_data and audio_data['bytes']:
    st.audio(audio_data['bytes'], format='audio/wav') # Optional: Play back recorded audio
    with st.spinner("Transcribing voice..."):
        # Pass the bytes and a filename to the agent
        voice_query = voice_agent.listen_and_transcribe(
            audio_bytes=audio_data['bytes'],
            audio_filename="user_recording.wav" # Filename helps API infer format
        )
        if voice_query and not voice_query.startswith("error:"):
            st.success(f"Transcribed: {voice_query}")
            process_query(voice_query)
        elif voice_query:
            st.error(voice_query)

# Text Input
if prompt := st.chat_input("Or type your question...", disabled=not st.session_state.backend_ready):
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
    if check_backend_status():
        print("Backend confirmed ready by periodic check.")
    else:
        print("Backend still initializing... Inputs disabled.")