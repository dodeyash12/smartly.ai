import os
import whisper
import tempfile
import moviepy.editor as mp
import streamlit as st
from openai import OpenAI
import os
from langchain import hub
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from PyPDF2 import PdfReader

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

# Initialize OpenAI client (ensure you have the API key set up correctly in your environment variables)
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "sk-GvlZG7r2Rj8ylmTi0cBOfsWX4Lk5mJZKetaBlr2y-rT3BlbkFJk1Ep6Nchj7Sl-56iVDs3w1kbWxZCDYnaCuEwYkciEA"))

# Load Whisper model
model = whisper.load_model("base")

# Page navigation
if 'page' not in st.session_state:
    st.session_state.page = 'Transcription'

# Navigation buttons in the sidebar
st.sidebar.title("Navigation")
if st.sidebar.button('Transcription'):
    st.session_state.page = 'Transcription'
if st.sidebar.button('Calendar'):
    st.session_state.page = 'Calendar.py'
def call_openai_model(prompt):
    # This is where you call the OpenAI API or another LLM
    # Example with OpenAI GPT:
    import openai

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    return response['choices'][0]['message']['content']

def extract_audio_from_mp4(mp4_file_path):
    """Extract audio from an MP4 video and save it as a temporary WAV file."""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_audio_file:
        video = mp.VideoFileClip(mp4_file_path)
        video.audio.write_audiofile(temp_audio_file.name)
        return temp_audio_file.name

def transcribe_audio(audio_file_path):
    """Transcribe audio using the Whisper model."""
    result = model.transcribe(audio_file_path)
    return result['text']

def generate_summary_and_study_plan(conversation):
    """Generate a summary and study plan using OpenAI based on a conversation transcript."""
    prompt = (
        "You are an assistant tasked with summarizing a classroom lecture and generating a study plan."
        "Please summarize the following lecture transcript in a concise format and then provide a study plan based on the key points that were covered in the lecture.\n\n"
        f"table of contents for textbook:{chapters}tell student which chapters to review\n"
        f"Lecture Transcript:\n{conversation}\n"
        "Output Format:\n"
        "Summary:\nWrite a brief summary of the key points discussed in the lecture.\n"
        "Study Plan:\nProvide a structured study plan focusing on the important topics to review, including references to specific topics or materials mentioned during the lecture."
        "additional info:make a lesson for the student on the information talk and more about the topic\n"
    )

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant summarizing the lecture and generating a study plan."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1000,  # Adjust as needed
        temperature=0.9
    )

    generated_output = response.choices[0].message.content.strip()
    return generated_output


def main():
    st.title("MP4 Transcription and Summary Generator")
    st.write("Upload an MP4 video file, and the app will transcribe the audio and generate a summary with a study plan.")

    uploaded_file = st.file_uploader("Choose an MP4 file", type="mp4")

    if uploaded_file is not None:
        with st.spinner('Processing...'):
            # Step 1: Save the uploaded file to a temporary location
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video_file:
                temp_video_file.write(uploaded_file.getvalue())
                video_file_path = temp_video_file.name

            try:
                # Step 2: Extract audio from the uploaded MP4 video
                audio_file_path = extract_audio_from_mp4(video_file_path)

                # Step 3: Transcribe the audio using Whisper
                transcript = transcribe_audio(audio_file_path)
                st.subheader("Transcription")
                st.text_area("Transcribed Text", transcript, height=300)

                # Step 4: Generate a summary and study plan based on the transcript
                summary_and_plan = generate_summary_and_study_plan(transcript)
                st.subheader("Generated Summary and Study Plan")
                st.text_area("Summary & Study Plan", summary_and_plan, height=300)

            finally:
                # Clean up temporary files
                if os.path.exists(audio_file_path):
                    os.remove(audio_file_path)
                if os.path.exists(video_file_path):
                    os.remove(video_file_path)

if __name__ == "__main__":
    main()
