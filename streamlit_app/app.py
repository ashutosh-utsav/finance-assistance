import streamlit as st
import requests
import sys
import os
import time

# --- Add project root to the Python path ---
# This allows us to import from the 'agents' directory.
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# --- Import the voice agent for its TTS and STT capabilities ---
from agents import voice_agent

# --- Configuration ---
# The URL of your running FastAPI orchestrator
API_URL = "http://127.0.0.1:8000/query"

# --- Helper Function to call the backend ---
def get_ai_brief(query: str):
    """Sends a query to the FastAPI backend and returns the response."""
    try:
        response = requests.post(API_URL, json={"query": query})
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Could not connect to the backend API. Please ensure it is running. Error: {e}")
        return None

# --- Streamlit Page Configuration ---
st.set_page_config(page_title="AI Financial Assistant", layout="wide")

st.title("🤖 AI Financial Assistant")
st.caption("Your personal market analysis and voice-interactive financial brief generator.")

# --- Initialize session state to hold the response ---
if "response_data" not in st.session_state:
    st.session_state.response_data = None

# --- Main UI Layout ---
# Create two columns for text and voice input
col1, col2 = st.columns([2, 1])

with col1:
    # --- Text Input ---
    st.subheader("Ask a Question via Text")
    user_text_query = st.text_input("Enter your financial query here:", "")
    if st.button("Get Text Brief"):
        if user_text_query:
            with st.spinner('Thinking... The agents are at work!'):
                st.session_state.response_data = get_ai_brief(user_text_query)
        else:
            st.warning("Please enter a question.")

with col2:
    # --- Voice Input ---
    st.subheader("Ask a Question via Voice")
    if st.button("Record Voice Brief", use_container_width=True):
        with st.spinner('Listening...'):
            # Use the voice agent we built earlier to listen and transcribe
            user_voice_query = voice_agent.listen_and_transcribe()
        
        if user_voice_query and not user_voice_query.startswith("error:"):
            st.info(f"Transcribed query: \"{user_voice_query}\"")
            with st.spinner('Thinking... The agents are at work!'):
                st.session_state.response_data = get_ai_brief(user_voice_query)
        else:
            st.error(f"Could not process voice input. Details: {user_voice_query}")


# --- Display the response if it exists in the session state ---
st.divider()

if st.session_state.response_data:
    st.subheader("Generated Market Brief")
    
    response_text = st.session_state.response_data.get("response", "No response text found.")
    st.write(response_text)

    # Add a button to play the audio of the response
    if st.button("Play Audio Brief"):
        with st.spinner("Generating audio..."):
            voice_agent.speak(response_text)

    # Optionally display the context used for debugging or transparency
    with st.expander("Show Context Used by the AI"):
        st.json(st.session_state.response_data.get("context_used", {}))