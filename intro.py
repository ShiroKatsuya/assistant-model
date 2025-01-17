import subprocess
import threading
audio_started_intro = threading.Event()
audio_file = 'Intro2.wav'
def play_audio(audio_file):
        try:
            audio_started_intro.set()  
            subprocess.run(
                ["ffplay", "-nodisp", "-autoexit", "-sync", "ext", audio_file],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        except Exception as e:
            print(f"Error saat memutar audio: {e}")
audio_thread_intro = threading.Thread(target=play_audio, args=(audio_file,))



