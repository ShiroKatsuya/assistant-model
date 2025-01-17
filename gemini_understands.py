import os
import time
import google.generativeai as genai
import streamlit as st
from dotenv import load_dotenv
import cv2
import torch
import numpy as np
from PIL import Image
import io
from moviepy import VideoFileClip
import speech_recognition as sr

MEDIA_FOLDER = 'medias'

def __init__():
    if not os.path.exists(MEDIA_FOLDER):
        os.makedirs(MEDIA_FOLDER)

    load_dotenv()  ## load all the environment variables
    api_key = os.getenv("GEMINI_API_KEY")
    genai.configure(api_key=api_key)

def save_uploaded_file(uploaded_file):
    """Save the uploaded file to the media folder and return the file path."""
    file_path = os.path.join(MEDIA_FOLDER, uploaded_file.name)
    with open(file_path, 'wb') as f:
        f.write(uploaded_file.read())
    return file_path

def extract_frames(video_path, max_frames=10):
    """Extract frames from video using CUDA if available"""
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_interval = max(total_frames // max_frames, 1)
    
    frames = []
    frame_count = 0
    
    while cap.isOpened() and len(frames) < max_frames:
        ret, frame = cap.read()
        if not ret:
            break
            
        if frame_count % frame_interval == 0:
            # Convert BGR to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # Convert to PIL Image
            pil_image = Image.fromarray(frame_rgb)
            frames.append(pil_image)
            
        frame_count += 1
        
    cap.release()
    return frames

def extract_audio_text(video_path):
    """Extract and transcribe audio from the video."""
    try:
        # Load video and extract audio
        video = VideoFileClip(video_path)
        audio = video.audio
        
        # Save audio temporarily
        temp_audio_path = os.path.join(MEDIA_FOLDER, "temp_audio.wav")
        audio.write_audiofile(temp_audio_path, codec='pcm_s16le')
        
        # Initialize recognizer
        recognizer = sr.Recognizer()
        
        # Read and transcribe audio
        with sr.AudioFile(temp_audio_path) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data)
        
        # Cleanup
        os.remove(temp_audio_path)
        video.close()
        
        return text
    except Exception as e:
        st.error(f"Error processing audio: {str(e)}")
        return ""

def get_insights(video_path):
    generation_config = genai.types.GenerationConfig(
        temperature=0.2,
        top_p=0.95,
        top_k=20,
        candidate_count=1,
        max_output_tokens=50,
        stop_sequences=["STOP!"],
    )
    """Extract insights from the video using local processing and Gemini Flash."""
    st.write(f"Processing video: {video_path}")

    st.write("Extracting frames...")
    frames = extract_frames(video_path)
    st.write(f"Extracted {len(frames)} key frames")

    st.write("Extracting audio...")
    audio_text = extract_audio_text(video_path)
    if audio_text:
        st.write("Audio transcription complete!")
    
    prompt = f"""Please analyze these video frames and the audio transcription, and give short, natural responses, 
                as if we were having a casual conversation. 
                Keep your answers concise and communicative, as if you were having a conversation.
                Note : Do not use markdown or any formatting.
                Note : Do not use phrases like "Sure thing! Here are some casual responses to the video:"
                
                Audio transcription: {audio_text}
                """

    model = genai.GenerativeModel(model_name="models/gemini-1.5-flash-002")

    st.write("Analyzing video content...")
    response = model.generate_content([prompt, *frames],
                                    request_options={"timeout": 600},
                                    generation_config=generation_config)
    st.write(f'Analysis complete!')
    st.subheader("Here's what I think about the video:")
    st.write(response.text)

def app():
    st.title("Video Insights Generator")

    uploaded_file = st.file_uploader("Upload a video file", type=["mp4", "avi", "mov", "mkv"])

    if uploaded_file is not None:
        file_path = save_uploaded_file(uploaded_file)
        st.video(file_path)
        get_insights(file_path)
        if os.path.exists(file_path):  ## Optional: Removing uploaded files from the temporary location
            os.remove(file_path)

__init__()
app()