import os
import time
from google import genai
from dotenv import load_dotenv
import cv2
import torch
import numpy as np
from PIL import Image
import io
from moviepy import VideoFileClip
import speech_recognition as sr
from deep_translator import GoogleTranslator
from voice import voice
from google.genai.types import (GenerateContentConfig
)

MEDIA_FOLDER = 'medias'
client = genai.Client(api_key="AIzaSyC3mPmd3ps_fGEXMwCjXOUPw7jMpXIeAoE")
model_id = "gemini-2.0-flash-exp"

def initialize():
    """Initialize environment and API key only when needed"""
    if not os.path.exists(MEDIA_FOLDER):
        os.makedirs(MEDIA_FOLDER)
  
    load_dotenv()

def save_uploaded_file(uploaded_file):
    """Save the uploaded file to the media folder and return the file path."""
    file_path = os.path.join(MEDIA_FOLDER, uploaded_file)
    # Since uploaded_file is a string path, we open and read the file in binary mode
    with open(uploaded_file, 'rb') as source_file:
        with open(file_path, 'wb') as dest_file:
            dest_file.write(source_file.read())
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
    try:
        video = VideoFileClip(video_path)
        if video.audio is None:
            video.close()
            return None
            
        audio = video.audio
        temp_audio_path = os.path.join(MEDIA_FOLDER, "temp_audio.wav")
        audio.write_audiofile(temp_audio_path, codec='pcm_s16le')

        recognizer = sr.Recognizer()

        with sr.AudioFile(temp_audio_path) as source:
            audio_data = recognizer.record(source)
            
            try:
                text_indonesian = recognizer.recognize_google(audio_data, language='id-ID')
                print("Indonesian text:", text_indonesian)
                
                text_english = GoogleTranslator(source='id', target='en').translate(text_indonesian)
                print("English translation:", text_english)
            except sr.UnknownValueError:
                print("Sorry, I don't understand that sentence.")
                text_english = None
            except sr.RequestError:
                print("Sorry, I don't understand that sentence.")
                text_english = None

        os.remove(temp_audio_path)
        video.close()
        
        return text_english
    except Exception as e:
        print(f"Error processing audio: {str(e)}")
        return None
def get_insights(video_path):
    # generation_config = GenerateContentConfig(
    #     temperature=0.2,
    #     top_p=0.95,
    #     top_k=20,
    #     candidate_count=1,
    #     max_output_tokens=100,
    #     stop_sequences=["STOP!"],
    # )
    """Extract insights from the video using local processing and Gemini Flash."""
    print(f"Processing video: {video_path}")

    print("Extracting frames...")
    frames = extract_frames(video_path)
    print(f"Extracted {len(frames)} key frames")

    print("Extracting audio...")
    audio_text = extract_audio_text(video_path)
    if audio_text is None:
        voice("No audio found in video. Skipping analysis.")
        return
        
    print("Audio transcription and translation complete!")
    
    prompt = f"""You are an assistant specializing in screen-sharing support. Your role is to:
                Answer Only Focus on the Topic Discussed
    

                Important: Ignore and do not comment on any unrelated windows or messages, such as "Screen Recorder" notifications or similar prompts.
        
                             
                                        

                Audio transcription (English): {audio_text}
                """



    print("Analyzing video content...")
    response = client.models.generate_content(model=model_id,
                                    contents=[prompt, *frames],
                                    )
    print(f'Analysis complete!')
    voice(response.text)
    print(response.text)

def app():
    """Main function that only runs when explicitly called"""
    initialize()  # Only initialize when app() is called
    print("Video Insights Generator")

    uploaded_file = "desktop_recording.mp4"
    if uploaded_file is not None:
        file_path = save_uploaded_file(uploaded_file)
        print(file_path)
        get_insights(file_path)
        if os.path.exists(file_path):  
            os.remove(file_path)

# Remove automatic execution
# __init__()
# app()