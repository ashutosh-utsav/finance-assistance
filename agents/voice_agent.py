import speech_recognition as sr
import time
import asyncio
import subprocess
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables (especially OPENAI_API_KEY)
load_dotenv()

# Initialize the OpenAI client
# It will automatically pick up the API key from your environment variables
try:
    client = OpenAI()
    print("OpenAI client initialized successfully for voice tasks.")
except Exception as e:
    print(f"Failed to initialize OpenAI client: {e}. Please ensure OPENAI_API_KEY is set.")
    client = None

# --- Text-to-Speech (TTS) using OpenAI's API ---
async def _speak_openai_tts_async(text: str, voice_model: str = "alloy"):
    """
    The core async function to stream TTS using OpenAI's state-of-the-art TTS API.
    Requires ffmpeg (ffplay) to be installed on your system.
    """
    if not client:
        print("OpenAI client not initialized. Cannot perform TTS.")
        return

    print("🤖 Speaking with OpenAI TTS (Streaming)...")
    
    try:
        response = client.audio.speech.create(
            model="tts-1",  # "tts-1-hd" for higher quality but slightly more latency/cost
            voice=voice_model, # Voice options: alloy, echo, fable, onyx, nova, shimmer
            input=text,
            response_format="mp3"
        )

        # Use ffplay to stream audio directly from the response content without saving a file
        ffplay_process = subprocess.Popen(
            [
                "ffplay",
                "-autoexit",
                "-nodisp",
                "-loglevel", "error", # Suppress ffplay's console output
                "-i", "pipe:0"
            ],
            stdin=subprocess.PIPE,
        )
        
        # Stream the audio content to ffplay's standard input
        for chunk in response.iter_bytes(chunk_size=4096):
            if chunk:
                ffplay_process.stdin.write(chunk)
        
        if ffplay_process.stdin:
            ffplay_process.stdin.close()
        ffplay_process.wait()

    except Exception as e:
        print(f"Error during OpenAI TTS streaming: {e}")

def speak(text: str):
    """
    Public-facing function to run the async OpenAI TTS.
    """
    if not client:
        print("OpenAI client not initialized. Cannot speak.")
        return
    try:
        asyncio.run(_speak_openai_tts_async(text))
    except Exception as e:
        print(f"Error starting asyncio speech with OpenAI TTS: {e}.")


# Speech-to-Text (STT) using OpenAI's Whisper API 
def listen_and_transcribe() -> str:
    """
    Listens for audio via the microphone and transcribes it to text
    using OpenAI's Whisper API for maximum accuracy.
    """
    if not client:
        return "error: OpenAI client not initialized. Cannot transcribe."

    r = sr.Recognizer()
    r.pause_threshold = 1.0 # How long of a silence marks the end of a phrase

    with sr.Microphone() as source:
        print("🎙️  Calibrating... Please wait.")
        r.adjust_for_ambient_noise(source, duration=1.5)
        
        print("🎙️  Listening for your command...")
        try:
            audio = r.listen(source, timeout=7, phrase_time_limit=20)
        except sr.WaitTimeoutError:
            return "error: No speech detected within the timeout period."

    print("🔬 Transcribing with OpenAI Whisper API...")
    
    try:
       
        text = r.recognize_openai(audio_data=audio, model="whisper-1")
        return text
    except sr.UnknownValueError:
        return "error: OpenAI Whisper could not understand the audio."
    except sr.RequestError as e:
       
        return f"error: Could not request results from OpenAI Whisper API; {e}"
    except Exception as e:
        return f"error: An unexpected error occurred during OpenAI STT; {e}"



if __name__ == '__main__':
    if not client:
        print("OpenAI client failed to initialize. Please check your OPENAI_API_KEY.")
    else:
        speak("Hello! I am now using the OpenAI API for my voice. The brain is still powered by Google Gemini.")
        time.sleep(0.5)
        user_query = listen_and_transcribe()
        
        if user_query.startswith("error:"):
            print(f"Transcription failed. {user_query}")
            speak(f"I'm sorry, I had trouble understanding. {user_query}")
        else:
            print(f"You said (via OpenAI STT): {user_query}")
            speak(f"Thank you. I have received your query about {user_query}. I will now process this with the Gemini language model.")