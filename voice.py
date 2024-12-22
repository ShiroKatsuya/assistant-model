from gtts import gTTS
import os
import time
import subprocess
from deep_translator import GoogleTranslator
import sys
sys.path.insert(0, 'silero_tts')
from silero_tts import SileroTTS
from concurrent.futures import ThreadPoolExecutor
import tkinter as tk
from pydub import AudioSegment
from pydub.utils import make_chunks
import speech_recognition as sr
from concurrent.futures import ThreadPoolExecutor
import threading
import re


def voice(teks, chunk_length_ms=3800): # Increased chunk length for slower subtitles
    recognizer = sr.Recognizer()
    
    print("isis teks",teks)
    
    tts = SileroTTS(
        model_id='v3_en',
        language='en',
        speaker='en_67',  # Using a clearer speaker
        sample_rate=48000,  # Ensuring sample rate does not exceed 48000
        device='cpu',
        put_accent=True,
        put_yo=True,
        num_threads=8  # Optimized number of threads for better processing
    )
    
    """
    Fungsi untuk mengubah teks menjadi suara, memainkannya, dan menghasilkan subtitle teks.
    
    Parameters:
    teks (str): Teks yang akan diubah menjadi suara.
    chunk_length_ms (int): Panjang setiap segmen audio dalam milidetik.
    """
    print("Memproses Text-to-Speech dengan SileroTTS.")
    
    # Periksa jika pengguna ingin keluar
    if teks.lower() == "exit":
        print("Keluar dari program.")
        return

    cleaned_text = re.sub(r"\*(.*?)\*", r"\1", teks)
    translated = GoogleTranslator(source='auto', target='en').translate(cleaned_text)
    print(f"Teks yang akan diubah menjadi suara: {translated}")
    
    audio_file = "output_ai.wav"
    
    # Proses teks menjadi suara dan simpan sebagai WAV
    try:
        tts.tts(translated, audio_file)
    except Exception as e:
        print(f"Error saat memproses TTS: {e}")
        return
    
    # Bagi audio menjadi beberapa segmen
    try:
        audio = AudioSegment.from_wav(audio_file)
    except Exception as e:
        print(f"Error saat memuat file audio: {e}")
        return
    
    chunks = make_chunks(audio, chunk_length_ms)
    subtitles = []
    
    def process_chunk(i, chunk):
        # Calculate word boundaries for more natural segmentation
        words = translated.split()
        total_words = len(words)
        
        # Calculate words per chunk based on total duration
        words_per_chunk = total_words / len(chunks)
        
        # Calculate start and end word indices with small overlap
        start_word = max(0, int(i * words_per_chunk - 1))
        end_word = min(total_words, int((i + 1) * words_per_chunk + 1))
        
        # Ensure minimum content
        if start_word >= end_word:
            end_word = min(start_word + 1, total_words)
            
        # Join words for this segment
        text_segment = ' '.join(words[start_word:end_word]).strip()
        if not text_segment:
            text_segment = "..."
            
        # Translate the segment to Indonesian
        indo_segment = GoogleTranslator(source='en', target='id').translate(text_segment)
        
        # Combine English and Indonesian with newline and segment number
        combined_segment = f"[{i+1}/{len(chunks)}]\n{text_segment}\n{indo_segment}"
            
        print(f"Segmen {i}: {combined_segment}")
        return combined_segment
    
    # Pre-process all chunks before starting playback
    with ThreadPoolExecutor() as executor:
        subtitles = list(executor.map(process_chunk, range(len(chunks)), chunks))
    
    # Menyiapkan tampilan subtitle
    root = tk.Tk()
    root.title("Subtitle")
    root.attributes("-topmost", True)
    root.configure(bg='black')
    root.overrideredirect(True)
    
    window_width = 800
    window_height = 150  # Increased height to accommodate segment number
    x_pos = 100
    y_pos = 700
    
    root.geometry(f"{window_width}x{window_height}+{x_pos}+{y_pos}")
    
    label = tk.Label(root, text="", fg="white", bg="black", font=("Comic Sans MS", 16), wraplength=window_width-50, justify="center")
    label.pack(expand=True)
    
    # Event untuk sinkronisasi
    audio_started = threading.Event()
    
    # Putar audio dalam thread terpisah
    def play_audio():
        try:
            audio_started.set()  # Tandai bahwa audio mulai diputar
            subprocess.run(["ffplay", "-nodisp", "-autoexit", "-sync", "ext", audio_file], check=True)
        except Exception as e:
            print(f"Error saat memutar audio: {e}")
            root.destroy()
    
    audio_thread = threading.Thread(target=play_audio)
    
    # Fungsi untuk update subtitle dengan timing yang lebih akurat
    def update_subtitle():
        nonlocal start_time
        current_time = time.time()
        elapsed_time = (current_time - start_time) * 1000
        chunk_index = int(elapsed_time // chunk_length_ms)
        
        if 0 <= chunk_index < len(subtitles):
            label.config(text=subtitles[chunk_index])
            # Calculate precise timing for next update
            next_chunk_start = (chunk_index + 1) * chunk_length_ms
            delay = next_chunk_start - elapsed_time
            # Add small offset to ensure synchronization
            delay = max(1, min(delay, chunk_length_ms))  # Reduced minimum delay
            root.after(int(delay), update_subtitle)
        else:
            label.config(text="")
            root.after(100, root.destroy)  # Reduced delay before closing
    
    # Start everything in sync
    audio_thread.start()
    audio_started.wait()  # Tunggu hingga audio benar-benar mulai
    start_time = time.time()
    update_subtitle()  # Start subtitle immediately
    
    root.mainloop()
    
    # Cleanup
    audio_thread.join()
    try:
        os.remove(audio_file)
    except Exception as e:
        print(f"Error menghapus file audio: {e}")