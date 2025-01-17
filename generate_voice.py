import sys
import os
import threading
import tkinter as tk
sys.path.insert(0, 'silero_tts')
from silero_tts import SileroTTS


def generate_voice(text):
    tts = SileroTTS(
        model_id='v3_en',
        language='en',
        speaker='en_67',
        sample_rate=48000,
        device='cuda',
        num_threads=8
    )

    tts.tts(text, 'countdown.wav')
    print("Suara berhasil dihasilkan dan disimpan sebagai 'countdown.wav'")

if __name__ == "__main__":
    text = (
        "Hello, I'm a voice assistant. How can I help you today?"
        
        
    )
    generate_voice(text)
