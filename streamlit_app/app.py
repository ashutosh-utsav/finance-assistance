import streamlit as st
import requests
import sys
import os
import time

# --- Add project root to the Python path ---
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# --- Import the voice agent ---
from agents import voice_agent

# --- Configuration ---
API_URL = "http://127.0.0.1:8000/query"

# --- Page Configuration ---
st.set_page_config(
    page_title="AI Financial Assistant",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CUSTOM CSS FOR INPUT BAR AND MINIMAL STYLING ---
st.markdown("""
<style>
    /* Main background and text colors - respect Streamlit's theme */
    /* body, .stApp {
        background-color: #1E1E1E; /* Example dark theme */
        color: #E0E0E0;       /* Example light text */
    } */

    /* Hide Streamlit's default hamburger menu, header, and footer */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Fixed Input Bar Container at the Bottom */
    .fixed-input-bar-container {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        padding: 10px 20px; /* Adjust padding as needed */
        background-color: #262730; /* Streamlit's default dark input background */
        border-top: 1px solid #303338; /* Streamlit's default dark border */
        z-index: 1000;
    }

    /* Ensure columns inside the bar are vertically aligned */
    .fixed-input-bar-container [data-testid="stHorizontalBlock"] {
        align-items: center;
    }

    /* Style the voice button */
    .fixed-input-bar-container div[data-testid="stButton"] button {
        background-color: #00A9FF; /* Accent color */
        color: white;
        border: none;
        border-radius: 0.375rem; /* Matches Streamlit's input border-radius */
        height: 3rem; /* Standard height */
        width: 100%;
        font-size: 1.5rem; /* Icon size */
    }
    .fixed-input-bar-container div[data-testid="stButton"] button:hover {
        background-color: #0087CC;
    }

    /* Ensure the main chat display area has padding at the bottom
       so the fixed input bar doesn't overlap the last message.
       70px is an estimate, adjust if needed. */
    .main-chat-area-padding {
        padding-bottom: 90px; 
    }

</style>
""", unsafe_allow_html=True)

# --- Helper Function to call backend ---
def get_ai_brief(query: str):
    try:
        response = requests.post(API_URL, json={"query": query})
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"API Connection Error: {e}"}

# --- Main App Logic ---
st.title("💼 AI Financial Assistant")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hello! How can I help you?"}]
if "speak_this_response" not in st.session_state:
    st.session_state.speak_this_response = None
if "user_text_input" not in st.session_state: # For text_input's state
    st.session_state.user_text_input = ""


# --- Function to process queries and handle responses ---
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
        st.session_state.user_text_input = "" # Clear the input field after processing
        st.rerun()

# --- Display Chat History ---
# Add a div with a class for bottom padding to the main content area
st.markdown('<div class="main-chat-area-padding">', unsafe_allow_html=True)
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])
st.markdown('</div>', unsafe_allow_html=True)


# --- Speak the latest assistant response if flagged ---
if st.session_state.speak_this_response:
    text_to_speak = st.session_state.speak_this_response
    st.session_state.speak_this_response = None
    time.sleep(0.1)
    with st.spinner("Preparing audio..."):
        voice_agent.speak(text_to_speak)
    # If spinner gets stuck, a rerun might be needed here
    # st.rerun()


# --- Fixed Input Bar at the Bottom ---
st.markdown('<div class="fixed-input-bar-container">', unsafe_allow_html=True)
col1, col2 = st.columns([5, 1]) # Text input gets more space

with col1:
    # Capture text input. The actual submission is handled by the form or a button.
    user_text = st.text_input("Type your question...", 
                              key="chat_text_area", # Unique key
                              label_visibility="collapsed",
                              value=st.session_state.user_text_input,
                              on_change=lambda: process_query(st.session_state.chat_text_area) # Process on enter/submit
                              )
    # Update session state if text_input changes. This is for the on_change to work.
    st.session_state.user_text_input = user_text 

with col2:
    if st.button("🎙️", help="Ask by voice", key="voice_button_bottom"):
        with st.spinner("Listening..."):
            voice_query = voice_agent.listen_and_transcribe()
            if voice_query and not voice_query.startswith("error:"):
                # Update the text input field with the voice query to give visual feedback
                # and then process it.
                st.session_state.user_text_input = voice_query
                process_query(voice_query)
            elif voice_query:
                st.error(voice_query)

st.markdown('</div>', unsafe_allow_html=True) # Close fixed-input-bar-container