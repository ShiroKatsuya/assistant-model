from gtts import gTTS
import os
import subprocess
import time

GOOGLE_TTS_MAX_CHARS = 100  # Max characters the Google TTS API takes at a time

def voice(teks, filename="response"):
    """
    Fungsi untuk mengubah teks menjadi suara dan menyimpannya.

    Parameters:
    teks (str): Teks yang akan diubah menjadi suara.
    filename (str): Nama file output tanpa ekstensi.
    """
    print("Memproses Text-to-Speech dengan gTTS.")

    audio_file = f"output/{filename}.mp3"
    os.makedirs(os.path.dirname(audio_file), exist_ok=True)

    # Periksa jika pengguna ingin keluar
    if teks.lower() == "exit":
        print("Keluar dari program.")
        return

    # Hapus file audio sebelumnya jika ada
    if os.path.exists(audio_file):
        try:
            os.remove(audio_file)
        except Exception as e:
            print(f"Error menghapus file: {e}")

    # Proses teks menjadi suara
    try:
        tts = gTTS(text=teks, lang='id', slow=False)
        tts.save(audio_file)
    except Exception as e:
        print(f"Error saat memproses TTS: {e}")
        return

    print(f"Audio disimpan di {audio_file}")


def get_filename_from_audio_file():
    return "response"

    
#     return get_filename(audio_file)

# def get_filename(audio_file):
#     return os.path.basename(audio_file)
