import subprocess
import threading

audio_started_intro_internet_access = threading.Event()
audio_started_process_internet_access = threading.Event()
audio_file = 'internet_access.wav'
audio_file_process_internet_access = 'process_audio_internet_access.wav'

def play_audio(audio_file):
    try:
        audio_started_intro_internet_access.set()  
        subprocess.run(
            ["ffplay", "-nodisp", "-autoexit", "-sync", "ext", audio_file],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except Exception as e:
        print(f"Error saat memutar audio: {e}")

def audio_thread_intro_internet_access():
    try:
        audio_started_intro_internet_access.set()  
        subprocess.run(
            ["ffplay", "-nodisp", "-autoexit", "-sync", "ext", audio_file],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except Exception as e:
        print(f"Error saat memutar audio: {e}")

def process_internet_access():
    try:
        audio_started_process_internet_access.set()  
        subprocess.run(
            ["ffplay", "-nodisp", "-autoexit", "-sync", "ext", audio_file_process_internet_access],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except Exception as e:
        print(f"Error saat memutar audio: {e}")

# No need to create thread objects here since they are created when needed in main.py