from pytube import YouTube
import google.generativeai as genai
import sys
sys.path.insert(0, 'silero_tts')
from silero_tts import SileroTTS
import requests

def youtube2audio(url: str):
    try:
        # Add headers to mimic a browser request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
        }
        
        # Create a session with the headers
        session = requests.Session()
        session.headers.update(headers)
        
        # Initialize YouTube with the session
        yt = YouTube(url, use_oauth=True, allow_oauth_cache=True)
        yt.bypass_age_gate()
        
        # Get the audio stream with highest quality
        video = yt.streams.filter(only_audio=True, file_extension='mp4').order_by('abr').desc().first()
        if not video:
            raise Exception("No audio stream found")
            
        # Download the audio
        return video.download()
        
    except Exception as e:
        print(f"Error downloading video: {str(e)}")
        return None

# Initialize TTS engine
tts = SileroTTS(
    model_id='v3_en',
    language='en',
    speaker='en_67',  # Using a clearer speaker
    sample_rate=48000,  # Ensuring sample rate does not exceed 48000
    device='cuda',
    put_accent=True,
    put_yo=True,
    num_threads=8  # Optimized number of threads for better processing
)

# Initialize Gemini model
model = genai.GenerativeModel('gemini-1.5-flash')

print(model)

file_path = youtube2audio("https://www.youtube.com/watch?v=h5id4erwD4s")

if file_path is None:
    print("Failed to download video")
else:
    # Transcribe audio using Silero TTS
    text = tts.transcribe(file_path)

    # Generate summary using Gemini
    response = model.generate_content(f"Please provide a concise summary of this transcript: {text}")
    summary = response.text

    print("###############################################")
    print(summary)
    print("###############################################")
