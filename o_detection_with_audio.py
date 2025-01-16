import cv2
import click
import pyaudio
import wave
import time
import threading
import numpy as np
from moviepy import VideoFileClip, AudioFileClip
import os
from queue import Queue
from datetime import datetime

from recording import (
    resume_audio_processing, 
    pause_audio_processing, 
    record_audio, 
    process_audio,
    audio_queue
)

def objek_deteksi(stop_event=None):
    # Audio recording settings
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 48000
    CHUNK = 1024
    SILENCE_THRESHOLD = 4000
    SILENCE_DURATION = 2.0  # Duration of silence before stopping recording
    
    # Initialize audio recording
    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT,
                       channels=CHANNELS,
                       rate=RATE,
                       input=True,
                    #    input_device_index=device_index,
                       frames_per_buffer=CHUNK)
    
    # Initialize video capture with retries
    max_retries = 3
    retry_count = 0
    cap = None
    
    while retry_count < max_retries:
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            break
        print(f"Failed to open camera, attempt {retry_count + 1} of {max_retries}")
        retry_count += 1
        time.sleep(1)  # Wait before retrying
        
    if not cap or not cap.isOpened():
        print("Error: Could not open video source after multiple attempts.")
        if stream:
            stream.stop_stream()
            stream.close()
        audio.terminate()
        return
    
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = 30.0

    # Shared variables
    recording = False
    frames_queue = Queue()
    stop_event = threading.Event()

    def detect_sound(data):
        """Detect if there is sound in audio data."""
        audio_data = np.frombuffer(data, dtype=np.int16)
        return np.max(np.abs(audio_data)) > SILENCE_THRESHOLD

    frames = []  # For audio frames
    internal_stop_event = threading.Event() if stop_event is None else stop_event

    def save_recording(audio_frames, video_frames, start_time):
        """Save the recorded audio and video."""
        # Delete previous recording if exists
        output_filename = "recording_camp.mp4"
        if os.path.exists(output_filename):
            os.remove(output_filename)

        temp_video = "temp_video.avi"
        temp_audio = "temp_audio.wav"

        # Save video
        out = cv2.VideoWriter(temp_video, cv2.VideoWriter_fourcc(*'XVID'), fps, (frame_width, frame_height))
        for frame in video_frames:
            out.write(frame)
        out.release()

        # Save audio
        with wave.open(temp_audio, 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(audio.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(audio_frames))

        # Combine audio and video
        video_clip = VideoFileClip(temp_video)
        audio_clip = AudioFileClip(temp_audio)
        
        final_clip = video_clip.with_audio(audio_clip)
        final_clip.write_videofile(output_filename, codec='h264_nvenc')

        # Clean up
        video_clip.close()
        audio_clip.close()
        os.remove(temp_video)
        os.remove(temp_audio)
        print(f"Saved recording to {output_filename}")
    
    def record_audio():
        """Record audio and trigger video recording when sound is detected."""
        nonlocal recording
        audio_frames = []
        video_frames = []
        last_sound_time = time.time()
        
        while not internal_stop_event.is_set():
            data = stream.read(CHUNK)
            has_sound = detect_sound(data)
            
            if has_sound:
                last_sound_time = time.time()
                if not recording:
                    recording = True
                    print("Sound detected - Starting recording")
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
                    print("Silence detected - Stopping recording")
                    if audio_frames and video_frames:
                        save_recording(audio_frames, video_frames, start_time)
                    recording = False

    print("Starting camera - Press 'q' to quit")
    
    # Start audio recording thread
    audio_thread = threading.Thread(target=record_audio)
    audio_thread.start()
    
    # Main video capture loop
    while not internal_stop_event.is_set():
        ret, frame = cap.read()
        if not ret:
            print("Error reading frame from camera")
            break
            
        if recording:
            frames_queue.put(frame.copy())
            
        # Display recording status
        status = "Recording" if recording else "Waiting for sound"
        cv2.putText(frame, status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
        cv2.imshow('Camera', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            internal_stop_event.set()
            break

    # Cleanup
    stop_event.set()
    audio_thread.join()
    stream.stop_stream()
    stream.close()
    audio.terminate()
    cap.release()
    cv2.destroyAllWindows()

    # Start audio recording thread if not already running
    record_thread = threading.Thread(target=record_audio, daemon=True)
    record_thread.start()
    
    # Start audio processing thread if not already running
    process_thread = threading.Thread(target=process_audio, daemon=True)
    process_thread.start()

    # Don't stop the audio threads, just pause processing
    pause_audio_processing()

if __name__ == "__main__":
    objek_deteksi()