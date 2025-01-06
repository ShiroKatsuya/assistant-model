import pyaudio
import wave
import threading
import queue
import speech_recognition as sr
import numpy as np
import simpleaudio as sa
import webrtcvad
import subprocess
from intro import audio_thread_intro, audio_started_intro

# Buat objek pengenalan suara

# translator = googletrans.Translator()

from deep_translator import GoogleTranslator

r = sr.Recognizer()

# Buat antrian untuk audio
audio_queue = queue.Queue()

# Event untuk mengontrol pause dan resume
resume_event = threading.Event()
resume_event.set()  # Mulai dalam keadaan berjalan

# Event untuk mengontrol intro selesai
intro_finished = threading.Event()

chunk = 1024  # Record in chunks of 1024 samples
sample_format = pyaudio.paInt16  # 16 bits per sample
channels = 1
print(channels)
fs = 44100  # Record at 44100 samples per second
seconds = 5
filename = "output.wav"

# Event untuk mengontrol pemutaran audio
audio_playing = threading.Event()

def pause_audio_processing():
    """Menghentikan sementara pemrosesan audio dan mengosongkan antrian."""
    resume_event.clear()
    clear_audio_queue()
    print("Pemrosesan audio dihentikan sementara dan antrian audio dibersihkan.")

def resume_audio_processing():
    """Melanjutkan pemrosesan audio."""
    resume_event.set()
    print("Pemrosesan audio dilanjutkan.")

def clear_audio_queue():
    """Mengosongkan semua item dalam antrian audio."""
    cleared = 0
    while not audio_queue.empty():
        try:
            audio_queue.get_nowait()
            audio_queue.task_done()
            cleared += 1
        except queue.Empty:
            break
    print(f"Antrian audio dibersihkan, {cleared} item dihapus.")

def detect_sound(data):
    """Deteksi apakah ada suara dalam data audio."""
    audio_data = np.frombuffer(data, dtype=np.int16)
    return np.max(np.abs(audio_data)) > 4000  # Threshold untuk mendeteksi suara

def play_audio(audio_file):
    """Putar audio dalam thread terpisah."""
    if not audio_playing.is_set():  # Hanya putar jika tidak ada audio lain yang sedang diputar
        audio_playing.set()  # Set flag bahwa audio sedang diputar
        try:
            subprocess.run(
                ["ffplay", "-nodisp", "-autoexit", "-sync", "ext", audio_file],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        except Exception as e:
            print(f"Error saat memutar audio: {e}")
        finally:
            audio_playing.clear()  # Clear flag setelah selesai memutar

def wait_for_intro():
    """Tunggu hingga intro selesai diputar."""
    if not audio_started_intro.is_set():
        print("Menunggu audio intro dimulai...")
        audio_started_intro.wait()
    print("Menunggu audio intro selesai...")
    audio_thread_intro.join()
    intro_finished.set()
    print("Audio intro selesai diputar")

def record_audio():
    # Tunggu hingga audio intro selesai diputar
    wait_for_intro()
        
    print("Menunggu suara untuk memulai perekaman...")
    """Fungsi untuk merekam audio dan memasukkannya ke dalam antrian."""
    p = pyaudio.PyAudio()  # Create an interface to PortAudio

    stream = p.open(format=sample_format,
                    channels=channels,
                    rate=fs,
                    frames_per_buffer=chunk,
                    input=True)

    frames = []  # Initialize array to store frames

    try:
        while True:
            resume_event.wait()  # Tunggu hingga resume_event diset sebelum melanjutkan
            data = stream.read(chunk)

            if detect_sound(data):
                print("Suara terdeteksi, mulai merekam...")
                play_thread = threading.Thread(target=play_audio, args=('recording.wav',))
                play_thread.start()
                frames.append(data)

                chunks_recorded = 0
                silence_chunks = 0
                min_chunks = int(fs / chunk * seconds)  # Jumlah chunk untuk 10 detik



                while True:
                    data = stream.read(chunk)
                    frames.append(data)
                    chunks_recorded += 1

                    # Setelah 10 detik, mulai cek keheningan
                    if chunks_recorded >= min_chunks:
                        if detect_sound(data):
                            silence_chunks = 0  # Reset penghitung keheningan jika ada suara
                        else:
                            silence_chunks += 1
                            
                        # Hentikan jika hening selama 1 detik (fs/chunk chunks)
                        if silence_chunks >= int(fs / chunk):
                            break
                    
                audio_queue.put(b''.join(frames))
                frames = []
                print("Perekaman selesai, menunggu resume untuk melanjutkan...")
                resume_event.clear()  # Tunggu resume untuk melanjutkan
    except Exception as e:
        print(f"Terjadi kesalahan selama perekaman: {e}")
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

def process_audio():
    """Fungsi untuk memproses audio dari antrian dan melakukan transkripsi."""
    while True:
        audio_data = audio_queue.get()
        if audio_data is None:
            break
        try:
            # Simpan audio ke file WAV
            wf = wave.open(filename, 'wb')
            wf.setnchannels(channels)
            wf.setsampwidth(pyaudio.PyAudio().get_sample_size(sample_format))
            wf.setframerate(fs)
            wf.writeframes(audio_data)
            wf.close()
            print(f"Audio disimpan ke {filename}")

            # Transkripsi audio menggunakan SpeechRecognition
            with sr.AudioFile(filename) as source:
                audio = r.record(source)
                try:
                    transcription = r.recognize_google(audio, language='id-ID')
                    translate = GoogleTranslator(source='auto', target='en').translate(transcription)
                    print(f"Transkripsi: {translate}")
                    yield translate
                except sr.UnknownValueError:
                    play_thread = threading.Thread(target=play_audio, args=('not_understood.wav',))
                    play_thread.start()
                    print("Google Speech Recognition tidak dapat memahami audio.")
                    resume_audio_processing()
                except sr.RequestError as e:
                    print(f"Permintaan ke Google Speech Recognition gagal; {e}")
        except Exception as e:
            print(f"Terjadi kesalahan tak terduga: {e}")
        finally:
            audio_queue.task_done()

# Inisialisasi thread untuk merekam audio
record_thread = threading.Thread(target=record_audio, daemon=True)
record_thread.start()

# Inisialisasi thread untuk memproses audio
process_thread = threading.Thread(target=process_audio, daemon=True)
process_thread.start()