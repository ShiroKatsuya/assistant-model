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
# from voice import voice
# import threading

# audio_started_intro = threading.Event()
# try:
#     audio_started_intro.set()
#     intro_text = "My Name Is Calista, a virtual assistant developed by Rizky Sulaeman, a developer and owner of a private company called CALISTA INDUSTRY. I am designed to assist users in completing various daily tasks. My duties include answering questions, providing information, completing tasks, automation, and much more."
#     audio_thread_intro = threading.Thread(target=voice, args=(intro_text,), daemon=True)
#     # audio_thread_intro.start()  # Start the thread after creating it
# except Exception as e:
#     print(f"Error saat memutar audio: {e}")




