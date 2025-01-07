import os
import sys
import subprocess
from pytubefix import YouTube
import google.generativeai as genai
import whisper
import torch

def download_youtube_audio(url):
    try:
        yt = YouTube(url)
        audio_stream = yt.streams.filter(only_audio=True).first()
        if not audio_stream:
            raise Exception("No audio stream found")
        filename = f"{yt.title}.mp3"
        return audio_stream.download(filename=filename)
    except Exception as e:
        print(f"Error downloading YouTube audio: {e}")
        return None

def convert_mp3_to_wav(mp3_path):
    try:
        wav_path = mp3_path.replace('.mp3', '.wav')
        subprocess.run(
            ["ffmpeg", "-i", mp3_path, wav_path],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return wav_path
    except subprocess.CalledProcessError as e:
        print(f"Error converting MP3 to WAV: {e}")
        return None

def audio_to_text(audio_path):
    if not audio_path:
        return None
    
    try:

        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {device}")
        model = whisper.load_model("base").to(device)
        

        result = model.transcribe(audio_path)
        transcript = result["text"]
        
        print(f"Complete Transcript: {transcript}")
        return transcript
        
    except Exception as e:
        print(f"Error processing audio file: {e}")
        return None

def cleanup_files(*file_paths):
    for file_path in file_paths:
        try:
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"Error cleaning up file {file_path}: {e}")

# Configure Gemini API
try:
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    print(f"Error configuring Gemini API: {e}")
    sys.exit(1)

# Main Workflow
# audio_file = download_youtube_audio("https://www.youtube.com/watch?v=r94vuvwUSkY")
audio_file = download_youtube_audio("https://www.youtube.com/watch?v=bdICz_sBI34")
if not audio_file:
    sys.exit("Failed to download audio")

wav_file = convert_mp3_to_wav(audio_file)
if not wav_file:
    cleanup_files(audio_file)
    sys.exit("Failed to convert audio to WAV")

transcript = audio_to_text(wav_file)
if transcript:
    try:
        response = model.generate_content(f"Please provide a concise summary of video :{transcript}")
        print(f"Summary: {response.text}")
    except Exception as e:
        print(f"Error generating summary: {e}")
else:
    print("Could not generate transcript from audio")

# Cleanup
cleanup_files(audio_file, wav_file)