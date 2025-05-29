import time
import asyncio
import subprocess
import os
from openai import OpenAI
from dotenv import load_dotenv
import io # Needed to handle bytes as a file

# Load environment variables (especially OPENAI_API_KEY)
load_dotenv()

# Initialize the OpenAI client
try:
    client = OpenAI()
    print("OpenAI client initialized successfully for voice tasks.")
except Exception as e:
    print(f"Failed to initialize OpenAI client: {e}. Please ensure OPENAI_API_KEY is set.")
    client = None

# --- Text-to-Speech (TTS) using OpenAI's API (Unchanged from previous OpenAI TTS version) ---
async def _speak_openai_tts_async(text: str, voice_model: str = "alloy"):
    if not client:
        print("OpenAI client not initialized. Cannot perform TTS.")
        return
    print("🤖 Speaking with OpenAI TTS (Streaming)...")
    try:
        response = client.audio.speech.create(
            model="tts-1",
            voice=voice_model,
            input=text,
            response_format="mp3"
        )
        ffplay_process = subprocess.Popen(
            ["ffplay", "-autoexit", "-nodisp", "-loglevel", "error", "-i", "pipe:0"],
            stdin=subprocess.PIPE,
        )
        for chunk in response.iter_bytes(chunk_size=4096):
            if chunk:
                ffplay_process.stdin.write(chunk)
        if ffplay_process.stdin:
            ffplay_process.stdin.close()
        ffplay_process.wait()
    except Exception as e:
        print(f"Error during OpenAI TTS streaming: {e}")

def speak(text: str):
    if not client:
        print("OpenAI client not initialized. Cannot speak.")
        return
    try:
        asyncio.run(_speak_openai_tts_async(text))
    except Exception as e:
        print(f"Error starting asyncio speech with OpenAI TTS: {e}.")

# --- Speech-to-Text (STT) using OpenAI's Whisper API directly ---
def listen_and_transcribe(audio_bytes: bytes, audio_filename: str = "audio.wav") -> str:
    """
    Transcribes audio bytes directly using OpenAI's Whisper API.
    Args:
        audio_bytes: The raw audio data as bytes.
        audio_filename: A filename (e.g., "audio.wav") to help the API infer format.
    """
    if not client:
        return "error: OpenAI client not initialized. Cannot transcribe."
    if not audio_bytes:
        return "error: No audio bytes received for transcription."

    print("🔬 Transcribing with OpenAI Whisper API (direct)...")
    try:
        # Wrap the bytes in a file-like object
        audio_file_like_object = io.BytesIO(audio_bytes)
        # When sending bytes directly, you need to pass a tuple: (filename, file_like_object)
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=(audio_filename, audio_file_like_object)
        )
        return transcript.text
    except Exception as e:
        return f"error: Could not request results from OpenAI Whisper API; {e}"

# The __main__ block for testing (will not work directly for listen_and_transcribe without audio bytes)
if __name__ == '__main__':
    if not client:
        print("OpenAI client failed to initialize. Please check your OPENAI_API_KEY.")
    else:
        speak("Hello! Voice agent ready. Direct OpenAI STT is now active. Please use the Streamlit app to record audio.")
  