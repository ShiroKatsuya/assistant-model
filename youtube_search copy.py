import os
import sys
import subprocess
from pytubefix import YouTube
import google.generativeai as genai
import whisper
import torch
from youtubesearchpython import VideosSearch
from deep_translator import GoogleTranslator
from typing import Tuple
from recording import process_audio, pause_audio_processing, resume_audio_processing, record_audio
import logging as log
import json
from voice import voice
import threading
import tkinter

# Global tkinter root instance that will be initialized in the main thread.
tk_root = None

class CommandFailedError(Exception):
    """Exception raised when a command execution fails."""
    pass

def get_youtube_proxy_configuration(use_proxy_default):
    """
    Returns the proxy configuration for YouTube.
    Currently a placeholder that returns None.
    """
    return None

use_proxy_default = False

def cmd(command, check=True, shell=True, capture_output=True, text=True):
    """
    Runs a command in a shell and raises an exception if the return code is non-zero.
    :param command: The shell command to execute.
    :return: The CompletedProcess instance.
    """
    log.info(f" + {command}")
    try:
        return subprocess.run(command, check=check, shell=shell, capture_output=capture_output, text=text)
    except subprocess.CalledProcessError as error:
        raise CommandFailedError(
            msg=f"\"{command}\" returned exit code: {error.returncode}",
            stdout=error.stdout,
            stderr=error.stderr
        )

def search_youtube(query, *args, **kwargs):
    videos_search = VideosSearch(query, limit=1)
    result = videos_search.result()
    if 'result' in result and len(result['result']) > 0:
        video_info = result['result'][0]
        return video_info.get('link', '')
    return None

def generate_youtube_token() -> dict:
    log.info("Generating YouTube token")
    result = cmd("node scripts/youtube-token-generator.js")
    data = json.loads(result.stdout)
    log.info(f"Result: {data}")
    return data

def po_token_verifier() -> Tuple[str, str]:
    token_object = generate_youtube_token()
    return token_object["visitorData"], token_object["poToken"]

def download_youtube_audio(url):
    if not url:
        print("No valid YouTube URL found")
        return None

    try:
        # Using hardcoded visitor_data and po_token to bypass bot detection as recommended.
        yt = YouTube(url,
                     proxies=get_youtube_proxy_configuration(use_proxy_default),
                     use_po_token=True,
                     po_token_verifier=po_token_verifier)
        print(f"Found video: {yt.title}")
        audio_stream = yt.streams.filter(only_audio=True).first()
        if not audio_stream:
            raise Exception("No audio stream found")
        filename = f"{yt.title}.mp3"
        return audio_stream.download(filename=filename)
    except Exception as e:
        print(f"Error downloading YouTube audio: {e}")
        return None

def convert_mp3_to_wav(mp3_path):
    wav_path = "output_ai.wav"
    try:
        # Save combined audio as 'output_ai.wav'
        subprocess.run(
            ["ffmpeg", "-i", mp3_path, wav_path],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except subprocess.CalledProcessError as e:
        print(f"Error converting MP3 to WAV: {e}")
        resume_audio_processing()  # Resume processing only after ffmpeg has completed (even on error)
        return None

    resume_audio_processing()  # Resume processing after ffmpeg has successfully finished
    return wav_path

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
                if os.path.basename(file_path) == "output_ai.wav":
                    print("File audio 'output_ai.wav' telah dihapus.")
        except Exception as e:
            print(f"Error cleaning up file {file_path}: {e}")

def safe_voice(message):
    """
    Safely calls the voice function in the main thread to avoid
    "Tcl_AsyncDelete: async handler deleted by the wrong thread" errors.
    """
    if threading.current_thread() != threading.main_thread():
        try:
            global tk_root
            if tk_root is not None:
                tk_root.after(0, voice, message)
            else:
                # Fallback if the main-thread tkinter root is not available
                voice(message)
        except Exception as e:
            print(f"Error scheduling safe_voice: {e}")
            voice(message)
    else:
        voice(message)

def main(*args, **kwargs):
    import time
    # Initialize the global tkinter root in the main thread
    global tk_root
    try:
        tk_root = tkinter.Tk()
        tk_root.withdraw()
    except Exception as e:
        print(f"Error initializing tkinter root: {e}")
        tk_root = None

    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel('gemini-1.5-flash')
    audio_processor = process_audio()
    resume_audio_processing()

    print("Getting started with YouTube.")
    time.sleep(1.55)

    try:
        while True:
            try:
                translate = next(audio_processor)
                if translate:
                    pause_audio_processing()

                    if any(keyword in translate.lower() for keyword in ["stop youtube", "hentikan youtube", "matikan youtube"]):
                        print("Menghentikan pencarian youtube...")
                        resume_audio_processing()
                        return None

                    query = translate
                    youtube_url = search_youtube(query)
                    if not youtube_url:
                        print(f"No YouTube results found for query: {query}")
                        resume_audio_processing()
                        continue

                    print(f"Found video URL: {youtube_url}")

                    audio_file = download_youtube_audio(youtube_url)
                    if not audio_file:
                        print("Failed to download audio")
                        resume_audio_processing()
                        continue

                    wav_file = convert_mp3_to_wav(audio_file)
                    if not wav_file:
                        cleanup_files(audio_file)
                        print("Failed to convert audio to WAV")
                        resume_audio_processing()
                        continue

                    transcript = audio_to_text(wav_file)
                    if not transcript or transcript.strip() == "":
                        print("Transcript is empty, skipping Gemini processing.")
                        cleanup_files(audio_file, wav_file)
                        resume_audio_processing()
                        continue

                    print("Processing transcript with Gemini...")
                    response = model.generate_content(
                        f"Take all the key points from the video so that the main information can be conveyed in a clearer and more organized way: {transcript}"
                    )
                    safe_voice(f"Response: {response.text.replace('*', '').replace('\n\n', '\n')}")
                    
                    print(f"Response: {response.text.replace('*', '').replace('\n\n', '\n')}")
                    cleanup_files(audio_file, wav_file)
                    # Stop further audio processing after safe_voice is processed.
                    return None
            except Exception as e:
                print(f"Error in processing loop: {e}")
                resume_audio_processing()
                continue
    except Exception as e:
        print(e)

if __name__ == "__main__":
    main()
