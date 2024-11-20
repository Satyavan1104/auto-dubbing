import streamlit as st
import cohere
import speech_recognition as sr
from moviepy import VideoFileClip, AudioFileClip
from gtts import gTTS
import os

# Initialize Cohere client
co = cohere.Client("YOUR_COHERE_API_KEY")

# Function to extract audio from video
def extract_audio_from_video(video_file):
    video = VideoFileClip(video_file)
    audio = video.audio
    audio_file = "audio.wav"
    audio.write_audiofile(audio_file)
    return audio_file

# Function to transcribe audio to text
def transcribe_audio(audio_file):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio = recognizer.record(source)
    try:
        text = recognizer.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        return "Audio could not be understood."
    except sr.RequestError as e:
        return f"Could not request results; {e}"

# Function to translate text using Cohere
def translate_text(text, target_language='es'):  # Default is Spanish
    response = co.translate(text, target_lang=target_language)
    return response.text

# Function to convert text to speech using gTTS
def text_to_speech(text, lang='es'):
    tts = gTTS(text=text, lang=lang, slow=False)
    audio_file = "dubbed_audio.mp3"
    tts.save(audio_file)
    return audio_file

# Function to replace audio in video
def replace_audio_in_video(video_file, dubbed_audio_file):
    video = VideoFileClip(video_file)
    new_audio = AudioFileClip(dubbed_audio_file)
    video = video.set_audio(new_audio)
    output_video_file = "dubbed_video.mp4"
    video.write_videofile(output_video_file, codec='libx264')
    return output_video_file

# Streamlit UI
st.title("Auto Dubbing Service")
st.markdown("Upload a video file, and we will automatically dub it into your selected language!")

video_file = st.file_uploader("Choose a video file", type=["mp4", "mov", "avi"])

if video_file:
    # Save uploaded file
    video_path = os.path.join("temp_video.mp4")
    with open(video_path, "wb") as f:
        f.write(video_file.getbuffer())

    # Extract audio from video
    audio_file = extract_audio_from_video(video_path)
    
    # Transcribe audio to text
    transcribed_text = transcribe_audio(audio_file)
    st.subheader("Transcribed Text")
    st.write(transcribed_text)

    # Get target language from user
    target_language = st.selectbox("Select target language", ["es", "fr", "de", "it", "pt"])

    # Translate text
    translated_text = translate_text(transcribed_text, target_language)
    st.subheader("Translated Text")
    st.write(translated_text)

    # Convert translated text to speech
    dubbed_audio_file = text_to_speech(translated_text, lang=target_language)
    
    # Replace the original audio in the video with dubbed audio
    output_video_file = replace_audio_in_video(video_path, dubbed_audio_file)
    
    # Provide download link for the dubbed video
    st.subheader("Download Dubbed Video")
    with open(output_video_file, "rb") as video_file:
        st.download_button(label="Download Video", data=video_file, file_name="dubbed_video.mp4", mime="video/mp4")

    # Clean up temporary files
    os.remove(video_path)
    os.remove(audio_file)
    os.remove(dubbed_audio_file)
    os.remove(output_video_file)
