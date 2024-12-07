import wave
import speech_recognition as sr
import os



# Buat objek pengenalan suara
r = sr.Recognizer()

def generate_transcription(file_path):
    """
    Fungsi untuk mengubah file audio menjadi teks menggunakan SpeechRecognition.
    
    Parameters:
    file_path (str): Path ke file audio.
    
    Returns:
    str: Transkripsi teks.
    """
    try:
        with sr.AudioFile(file_path) as source:
            audio = r.record(source)
            transcription = r.recognize_google(audio, language='id-ID')
            print(f"Transkripsi: {transcription}")
            return transcription
    except sr.UnknownValueError:
        print("Google Speech Recognition tidak dapat memahami audio.")
        return None
    except sr.RequestError as e:
        print(f"Permintaan ke Google Speech Recognition gagal; {e}")
        return None
    except Exception as e:
        print(f"Terjadi kesalahan tak terduga: {e}")
        return None