import sys
import os
import threading
import tkinter as tk
sys.path.insert(0, 'silero_tts')
from silero_tts import SileroTTS
import simpleaudio as sa  # Untuk memainkan audio WAV

# Fungsi untuk menampilkan subtitle
def show_subtitle(text):
    root = tk.Tk()
    root.title("Subtitle")
    root.attributes("-topmost", True)  # Selalu di atas
    root.configure(bg='black')

    # Menyesuaikan ukuran jendela
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    window_width = 800
    window_height = 200
    x_pos = (screen_width - window_width) // 2
    y_pos = screen_height - window_height - 40  # 50 piksel dari bawah

    root.geometry(f"{window_width}x{window_height}+{x_pos}+{y_pos}")

    # Label untuk menampilkan teks
    label = tk.Label(root, text=text, fg="white", bg="black", font=("Helvetica", 16), wraplength=window_width-20, justify="center")
    label.pack(expand=True)

    # Menggunakan tombol untuk menutup jendela
    close_button = tk.Button(root, text="Close", command=root.destroy, bg="red", fg="white")
    close_button.pack(pady=10)

    root.mainloop()

# Fungsi untuk memainkan audio
def play_audio(file_path):
    wave_obj = sa.WaveObject.from_wave_file(file_path)
    play_obj = wave_obj.play()
    play_obj.wait_done()

# Teks yang akan diubah menjadi suara dan ditampilkan sebagai subtitle
text = (
    "The end of everything in the universe is a concept that has fascinated scientists and philosophers for centuries. "
   
)

tts = SileroTTS(
    model_id='v3_en',
    language='en',
    speaker='en_67',  # Menggunakan speaker yang lebih jelas
    sample_rate=48000,  # Memastikan sample rate tidak melebihi 48000
    device='cpu',
    num_threads=8  # Jumlah thread yang dioptimalkan untuk pemrosesan yang lebih baik
)

# Menghasilkan file audio
tts.tts(text, 'check.wav')
print(tts)

# Membuat thread untuk memainkan audio
audio_thread = threading.Thread(target=play_audio, args=('check.wav',))

# Membuat thread untuk menampilkan subtitle
subtitle_thread = threading.Thread(target=show_subtitle, args=(text,))

# Memulai kedua thread
audio_thread.start()
subtitle_thread.start()

# Menunggu kedua thread selesai
audio_thread.join()
subtitle_thread.join()