
import tkinter as tk
import simpleaudio as sa
import threading
import speech_recognition as sr
from pydub import AudioSegment
from pydub.utils import make_chunks
import time
import os
from deep_translator import GoogleTranslator

def show_subtitle_from_audio(file_path, chunk_length_ms=5000):
    """
    Menampilkan subtitle yang disinkronkan dengan audio.
    
    Args:
        file_path (str): Path ke file audio.
        chunk_length_ms (int): Panjang setiap segmen audio dalam milidetik.
    """

    recognizer = sr.Recognizer()

    # Membagi audio menjadi beberapa segmen
    audio = AudioSegment.from_wav(file_path)
    chunks = make_chunks(audio, chunk_length_ms)  # Membagi audio setiap 5 detik

    subtitles = []

    from concurrent.futures import ThreadPoolExecutor

    def process_chunk(i, chunk):
        chunk_filename = f"chunk{i}.wav"
        chunk.export(chunk_filename, format="wav")
        with sr.AudioFile(chunk_filename) as source:
            audio_data = recognizer.record(source)
            try:
                text = recognizer.recognize_google(audio_data)
                # Terjemahkan teks ke bahasa Indonesia
                translated_text = GoogleTranslator(source='auto', target='id').translate(text)
            except sr.UnknownValueError:
                translated_text = ""
            except sr.RequestError:
                translated_text = "Error: Tidak dapat menghubungi layanan pengenalan suara."
        # Menghapus file chunk setelah diproses
        os.remove(chunk_filename)
        return translated_text

    def extract_text_from_chunks():
        with ThreadPoolExecutor() as executor:
            results = executor.map(process_chunk, range(len(chunks)), chunks)
            subtitles.extend(results)

    extract_text_from_chunks()

    def play_audio():
        wave_obj = sa.WaveObject.from_wave_file(file_path)
        play_obj = wave_obj.play()
        play_obj.wait_done()

    # Memulai pemutaran audio dalam thread terpisah
    audio_thread = threading.Thread(target=play_audio)
    audio_thread.start()

    root = tk.Tk()
    root.title("Subtitle")
    root.attributes("-topmost", True)  # Selalu di atas
    root.configure(bg='black')
    root.overrideredirect(True)
    root.attributes("-alpha", 0.6)
    
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    window_width = 800
    window_height = 100
    x_pos = 100  # Set x_pos to 0 to position the window on the left side of the screen
    y_pos = 700

    root.geometry(f"{window_width}x{window_height}+{x_pos}+{y_pos}")

    label = tk.Label(root, text="", fg="white", bg="black", font=("Comic Sans MS", 16), wraplength=window_width-50, justify="center")
    label.pack(expand=True)

    start_time = time.time()

    def update_subtitle():
        elapsed_time = (time.time() - start_time) * 1000  # dalam milidetik
        chunk_index = int(elapsed_time // chunk_length_ms)
        if chunk_index < len(subtitles):
            label.config(text=subtitles[chunk_index])
        else:
            label.config(text="")
        root.after(500, update_subtitle)  # Memperbarui setiap 500 ms

    update_subtitle()
    root.mainloop()

# Contoh penggunaan
show_subtitle_from_audio("en11.wav")