import pyttsx3
import speech_recognition as sr
import time

def speak(text: str):
    """
    Converts text to speech using the pyttsx3 library.
    """
    # 1. Initialize the TTS engine
    engine = pyttsx3.init()
    
    # Optional: Adjust voice properties
    # voices = engine.getProperty('voices')
    # engine.setProperty('voice', voices[1].id) # Change index for different voices
    # engine.setProperty('rate', 150) # Speed of speech

    print("🤖 Speaking...")
    
    # 2. Queue the text to be spoken
    engine.say(text)
    
    # 3. Process the queue and wait for speech to complete
    engine.runAndWait()

def listen_and_transcribe() -> str:
    """
    Listens for audio via the microphone and transcribes it to text using Whisper.
    """
    # 1. Initialize the recognizer
    r = sr.Recognizer()
    
    # 2. Use the default microphone as the audio source
    with sr.Microphone() as source:
        print("🎙️  Listening... (Please speak clearly)")
        
        # Adjust for ambient noise to improve accuracy
        r.adjust_for_ambient_noise(source)
        
        # Listen for the user's input
        try:
            # The timeout and phrase_time_limit can be adjusted.
            # timeout=5 means it will wait up to 5 seconds for a phrase to start.
            audio = r.listen(source, timeout=5, phrase_time_limit=15)
        except sr.WaitTimeoutError:
            return "error: No speech detected within the timeout period."

    print("🔬 Transcribing...")
    
    # 3. Transcribe the audio using Whisper
    try:
        # This uses the local Whisper model. The first time you run this,
        # it will download the 'base' model.
        text = r.recognize_whisper(audio, language="english")
        return text
    except sr.UnknownValueError:
        return "error: Whisper could not understand the audio."
    except sr.RequestError as e:
        return f"error: Could not request results from Whisper; {e}"

# This part demonstrates the full audio I/O loop
if __name__ == '__main__':
    # --- Test the TTS functionality ---
    speak("Hello! I am your AI financial assistant. Please ask me a question about your portfolio.")
    
    # Add a small delay for a more natural conversation flow
    time.sleep(0.5)

    # --- Test the STT functionality ---
    user_query = listen_and_transcribe()
    
    # --- Process the result ---
    if user_query.startswith("error:"):
        print(f"Transcription failed. {user_query}")
        speak("I'm sorry, I had trouble understanding. Please try again.")
    else:
        print(f"✅ You said: {user_query}")
        
        # --- Simulate getting a response from the LLM agent ---
        # In the full application, you would pass 'user_query' to your other agents.
        mock_llm_response = f"Certainly. Processing your request regarding '{user_query}'. Here is the summary you asked for."
        
        # --- Speak the final response ---
        speak(mock_llm_response)