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







def voice(teks, chunk_length_ms=3000):
    recognizer = sr.Recognizer()
    
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
    
    # Terjemahkan teks ke bahasa Inggris
    translated = GoogleTranslator(source='auto', target='en').translate(teks)
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
    
    chunks = make_chunks(audio, chunk_length_ms)  # Membagi audio setiap 3 detik untuk akurasi lebih baik
    subtitles = []
    
    def process_chunk(i, chunk):
        chunk_filename = f"chunk{i}.wav"
        chunk.export(chunk_filename, format="wav")
        with sr.AudioFile(chunk_filename) as source:
            audio_data = recognizer.record(source)
            try:
                # Menggunakan bahasa Inggris untuk pengenalan suara
                text = recognizer.recognize_google(audio_data, language='en')
                # Terjemahkan teks ke bahasa Indonesia untuk subtitle
                translated_text = GoogleTranslator(source='en', target='id').translate(text)
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
            for result in results:
                subtitles.append(result)
    
    extract_text_from_chunks()
    
    # Menyiapkan tampilan subtitle
    root = tk.Tk()
    root.title("Subtitle")
    root.attributes("-topmost", True)  # Selalu di atas
    root.configure(bg='black')
    root.overrideredirect(True)
    root.attributes("-alpha", 0.6)
    
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    window_width = 800
    window_height = 80
    x_pos = 100  # Set x_pos to 0 to position the window on the left side of the screen
    y_pos = 700
    
    root.geometry(f"{window_width}x{window_height}+{x_pos}+{y_pos}")
    
    label = tk.Label(root, text="", fg="white", bg="black", font=("Comic Sans MS", 16), wraplength=window_width-50, justify="center")
    label.pack(expand=True)
    
    start_time = time.time()
    
    def update_subtitle():
        elapsed_time = (time.time() - start_time) * 1000  # dalam milidetik
        chunk_index = int(elapsed_time // chunk_length_ms)
        if 0 <= chunk_index < len(subtitles):
            label.config(text=subtitles[chunk_index])
        else:
            label.config(text="")
            root.destroy()  # Hentikan program setelah subtitle selesai
        root.after(300, update_subtitle)  # Memperbarui setiap 300 ms untuk akurasi lebih baik
    
    # Periksa jika pengguna ingin keluar
    if teks.lower() == "exit":
        print("Keluar dari program.")
        root.destroy()
        return
    
    # Putar audio dalam thread terpisah agar tidak menghalangi tampilan subtitle
    def play_audio():
        try:
            subprocess.run(["ffplay", "-nodisp", "-autoexit", audio_file], check=True)
        except Exception as e:
            print(f"Error saat memutar audio: {e}")
    
    audio_thread = threading.Thread(target=play_audio)
    audio_thread.start()
    
    # Memulai pembaruan subtitle
    update_subtitle()
    root.mainloop()
    
    # Tunggu audio selesai diputar
    audio_thread.join()
    
    # Hapus file audio setelah diputar
    try:
        os.remove(audio_file)
    except Exception as e:
        print(f"Error menghapus file audio: {e}")
    
    # Hentikan program setelah audio dan subtitle selesai
    # sys.exit(0)