import threading

import openai
import whisper
import streamlit as st
import sounddevice as sd
import numpy as np
import wavio
from pydub import AudioSegment
from pydub.playback import play
from pathlib import Path
import os
# Set your OpenAI API key
openai.api_key = os.environ.get("OPENAI_API_KEY", "sk-GvlZG7r2Rj8ylmTi0cBOfsWX4Lk5mJZKetaBlr2y-rT3BlbkFJk1Ep6Nchj7Sl-56iVDs3w1kbWxZCDYnaCuEwYkciEA")

model = whisper.load_model("base")  # "tiny", "base", "small", "medium", or "large"

chapters = {
    1: "Becoming Human",
    2: "Rivers, Cities, and First States, 4000-2000 BCE",
    3: "Nomads, Territorial States, and Microsocieties, 2000-1200 BCE",
    4: "First Empires and Common Cultures in Afro-Eurasia, 1200-350 BCE",
    5: "Worlds Turned Inside Out, 1000-350 BCE",
    6: "Shrinking the Afro-Eurasian World, 350 BCE-250 CE",
    7: "Han Dynasty China and Imperial Rome, 300 BCE-300 CE",
    8: "The Rise of Universal Religions, 300-600 CE",
    9: "New Empires and Common Cultures, 600-1000 CE",
    10: "Becoming 'The World,' 1000-1300 CE",
    11: "Crises and Recovery in Afro-Eurasia, 1300s-1500s",
    12: "Contact, Commerce, and Colonization, 1450s-1600",
    13: "Worlds Entangled, 1600-1750",
    14: "Cultures of Splendor and Power, 1500-1780",
    15: "Reordering the World, 1750-1850",
    16: "Alternative Visions of the Nineteenth Century",
    17: "Nations and Empires, 1850-1914",
    18: "An Unsettled World, 1890-1914",
    19: "Of Masses and Visions of the Modern, 1910-1939",
    20: "The Three-World Order, 1940-1975",
    21: "Globalization, 1970-2000"
}

# Function to record audio and save as WAV
def record_audio(duration=10, fs=44100):
    st.write("Recording...")
    audio_data = sd.rec(int(duration * fs), samplerate=fs, channels=1)
    sd.wait()  # Wait until recording is finished
    wavio.write("output.wav", audio_data, fs, sampwidth=2)  # Save as WAV file
    return "output.wav"


# Function to transcribe audio using Whisper
def transcribe_audio(audio_file):
    result = model.transcribe(audio_file)
    return result["text"]


# Function to get response from GPT-4
def generate_summary_and_study_plan(prompt):
    """Generate a summary and study plan using OpenAI based on a conversation transcript."""
    prompt = prompt+ f"{chapters}tell students what chapter in the textbook to find this information if applicable"

    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant helping tutor a student."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=10000,  # Adjust as needed
        temperature=0.9
    )

    generated_output = response.choices[0].message.content.strip()
    return generated_output


# Function to convert text to speech using OpenAI
def text_to_speech(text, file_path="response.mp3"):
    speech_file_path = Path(file_path)

    response = openai.audio.speech.create(
        model="tts-1",
        voice="alloy",  # Specify the voice model
        input=text
    )

    # Save the audio file
    response.stream_to_file(speech_file_path)
    return speech_file_path


# Function to play the audio file
def play_audio(file_path):
    global is_speaking, playback_thread
    is_speaking = True

    def play_func():
        audio = AudioSegment.from_file(file_path, format="mp3")
        if is_speaking:
            play(audio)

    playback_thread = threading.Thread(target=play_func)
    playback_thread.start()


def stop_speaking():
    global is_speaking
    is_speaking = False
    if playback_thread and playback_thread.is_alive():
        playback_thread.join()  # Ensure the thread is finished
    st.write("Speaking stopped.")



# Streamlit UI
st.title("Speech-to-Text Tutor Bot with Whisper and TTS")
st.write("Press the button to start speaking and get tutoring assistance.")

# Dropdown for subject selection
subject = st.selectbox('Choose a subject:', ['Math', 'Science', 'History', 'English'])
if st.button('stop playing'):
    stop_speaking()

# Button to start recording audio
if st.button('Start Talking'):
    audio_file = record_audio()  # Record audio and save as WAV
    user_input = transcribe_audio(audio_file)  # Transcribe using Whisper

    if user_input:
        st.write("You said: " + user_input)

        # Add subject to the prompt and get GPT-4 response
        prompt = f"You are a {subject} tutor. {user_input}"
        tutor_response = generate_summary_and_study_plan(prompt)  # Get GPT-4 response
        st.write("Tutor Bot: " + tutor_response)

        # Convert GPT-4 response to speech
        speech_file_path = text_to_speech(tutor_response, "tutor_response.mp3")

        # Play the generated speech
        play_audio(speech_file_path)


