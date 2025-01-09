import os
import sys
import subprocess
from pytubefix import YouTube
import google.generativeai as genai
import whisper
import torch
from youtubesearchpython import VideosSearch
from deep_translator import GoogleTranslator


def search_youtube(query):
    videos_search = VideosSearch(query, limit=1)
    result = videos_search.result()
    if 'result' in result and len(result['result']) > 0:
        video_info = result['result'][0]
        return video_info.get('link', '')
    return None  

def download_youtube_audio(url):
    if not url:  
        print("No valid YouTube URL found")
        return None
        
    try:
        yt = YouTube(url)
        print(f"Found video: {yt.title}")
        audio_stream = yt.streams.filter(only_audio=True).first()
        if not audio_stream:
            raise Exception("No audio stream found")
        filename = f"{yt.title}.mp3"
        
 
        if os.path.exists(filename):
            os.remove(filename)
            print(f"Deleted existing file: {filename}")
            
        return audio_stream.download(filename=filename)
    except Exception as e:
        print(f"Error downloading YouTube audio: {e}")
        return None

def convert_mp3_to_wav(mp3_path):
    try:
        wav_path = mp3_path.replace('.mp3', '.wav')

        if os.path.exists(wav_path):
            os.remove(wav_path)
            print(f"Deleted existing WAV file: {wav_path}")
            
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


try:
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    print(f"Error configuring Gemini API: {e}")
    sys.exit(1)


query = "How RAG Turns AI Chatbots Into Something"
youtube_url = search_youtube(query)
if not youtube_url:
    sys.exit(f"No YouTube results found for query: {query}")

print(f"Found video URL: {youtube_url}")

audio_file = download_youtube_audio(youtube_url)
if not audio_file:
    sys.exit("Failed to download audio")

wav_file = convert_mp3_to_wav(audio_file)
if not wav_file:
    cleanup_files(audio_file)
    sys.exit("Failed to convert audio to WAV")

transcript = audio_to_text(wav_file)
# translate = GoogleTranslator(source='auto', target='en').translate(transcript)
print(f"Transcript: {transcript}")

if transcript:
    try:
        response = model.generate_content(f"Take all the key points from the video so that the main information can be conveyed in a clearer and more organized way : {transcript}")
        print(f"Response: {response.text.replace('*', '').replace('\n\n', '\n')}")
    except Exception as e:
        print(f"Error generating summary: {e}")
else:
    print("Could not generate transcript from audio")


cleanup_files(audio_file, wav_file)