import pyaudio
import wave
import click
import time
import pyautogui
import cv2
import numpy as np
import threading
from moviepy import VideoFileClip, AudioFileClip, CompositeVideoClip
from queue import Queue
import os
import tkinter as tk
from tkinter import ttk

@click.command()
@click.option('--device_index', default=1, type=int, help="Device index for recording audio")
def main(device_index, output_filename='record421.mp4'):
    # Audio recording settings
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 48000
    CHUNK = 1024
    SILENCE_DURATION = 2.0  # Duration of silence before stopping recording
    SILENCE_THRESHOLD = 4000

    # Video recording settings 
    resolution = (1920, 1080)
    codec = cv2.VideoWriter_fourcc(*"XVID")
    temp_video = "temp_video.avi"
    temp_audio = "temp_audio.wav"
    fps = 60.0

    # Initialize audio recording
    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT,
                       channels=CHANNELS,
                       rate=RATE,
                       input=True,
                       input_device_index=device_index,
                       frames_per_buffer=CHUNK)

    frames = []  # For audio frames
    start_time = time.time()
    recording = False  # Initialize recording state
    frames_queue = Queue()  # Initialize frames queue
    stop_event = threading.Event()  # Initialize stop event

    # Create Tkinter window
    root = tk.Tk()
    root.title("Screen Recorder")
    root.geometry("300x100")
    
    # Create label for status
    status_label = ttk.Label(root, text="Recording video...", font=("Arial", 12))
    status_label.pack(pady=20)

    # Create quit button
    quit_button = ttk.Button(root, text="Quit", command=lambda: stop_event.set())
    quit_button.pack()

    def detect_sound(data):
        """Detect if there is sound in audio data."""
        audio_data = np.frombuffer(data, dtype=np.int16)
        return np.max(np.abs(audio_data)) > SILENCE_THRESHOLD

    def save_recording(audio_frames, video_frames, start_time):
        """Save the recorded audio and video."""
        nonlocal audio  # Access the audio object from outer scope
        
        # Save audio to temp file
        with wave.open(temp_audio, 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(audio.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(audio_frames))

        # Save video to temp file
        out = cv2.VideoWriter(temp_video, codec, fps, resolution)
        for frame in video_frames:
            out.write(frame)
        out.release()

        # Combine audio and video
        video = VideoFileClip(temp_video)
        audio_clip = AudioFileClip(temp_audio)
        final_clip = video.with_audio(audio_clip)
        
        # Overwrite the output file if it exists
        if os.path.exists(output_filename):
            os.remove(output_filename)
        
        final_clip.write_videofile(output_filename, codec="h264_nvenc")

    def record_audio():
        """Record audio and trigger video recording when sound is detected."""
        nonlocal recording
        audio_frames = []
        video_frames = []
        last_sound_time = time.time()
        
        while not stop_event.is_set():
            data = stream.read(CHUNK)
            has_sound = detect_sound(data)
            
            if has_sound:
                last_sound_time = time.time()
                if not recording:
                    recording = True
                    status_label.config(text="Sound detected - Starting recording")
                    audio_frames = []
                    video_frames = []
                    start_time = time.time()
                
                audio_frames.append(data)
                # Get accumulated video frames
                while not frames_queue.empty():
                    video_frames.append(frames_queue.get())
                
            elif recording:
                audio_frames.append(data)
                while not frames_queue.empty():
                    video_frames.append(frames_queue.get())
                
                # Check if silence duration exceeded
                if time.time() - last_sound_time > SILENCE_DURATION:
                    status_label.config(text="Recording video...")
                    if audio_frames and video_frames:
                        save_recording(audio_frames, video_frames, start_time)
                    recording = False
                    video_frames = []  # Clear video frames when stopping

    # Start audio recording in separate thread
    audio_thread = threading.Thread(target=record_audio)
    audio_thread.start()

    def update_frame():
        if not stop_event.is_set():
            img = pyautogui.screenshot()
            frame = np.array(img)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, resolution)
            
            if recording:  # Only queue frames when recording
                frames_queue.put(frame)
            
            root.after(1000 // int(fps), update_frame)
        else:
            root.quit()

    print("Recording video...")
    update_frame()
    root.mainloop()

    # Clean up
    stop_event.set()
    audio_thread.join()
    stream.stop_stream()
    stream.close()
    audio.terminate()

    print(f"Recording saved to {output_filename}")

if __name__ == "__main__":
    main()