import cv2
import click
import pyaudio
import wave
import time
import threading
import numpy as np
from moviepy import VideoFileClip, AudioFileClip, CompositeVideoClip
import os

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
    RECORD_SECONDS = 10
    
    # Video recording settings
    temp_video = "temp_video.avi"
    temp_audio = "temp_audio.wav"
    
    # Initialize audio recording
    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT,
                       channels=CHANNELS,
                       rate=RATE,
                       input=True,
                       input_device_index=1,
                       frames_per_buffer=CHUNK)

    frames = []  # For audio frames
    internal_stop_event = threading.Event() if stop_event is None else stop_event
    
    def record_audio():
        print("Recording audio...")
        for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            if internal_stop_event.is_set():
                break
            try:
                data = stream.read(CHUNK)
                frames.append(data)
            except Exception as e:
                print(f"Error recording audio: {e}")
                break
        print("Audio recording finished")

    # Initialize video capture
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open video source.")
        return

    # Get video properties
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = 30.0

    # Create video writer
    out = cv2.VideoWriter(temp_video, cv2.VideoWriter_fourcc(*'XVID'), fps, (frame_width, frame_height))

    # Start audio recording in separate thread
    audio_thread = threading.Thread(target=record_audio)
    audio_thread.start()

    print("Recording video...")
    start_time = time.time()
    
    try:
        # Record for RECORD_SECONDS
        while (time.time() - start_time) < RECORD_SECONDS and not internal_stop_event.is_set():
            ret, frame = cap.read()
            if not ret:
                print("Failed to grab frame")
                break
                
            # Write frame
            out.write(frame)
            
            # Display frame
            cv2.imshow('Recording', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    finally:
        # Clean up video recording
        cap.release()
        out.release()
        cv2.destroyAllWindows()

        # Clean up audio recording
        stream.stop_stream()
        stream.close()
        audio.terminate()

        # Wait for audio thread to complete
        audio_thread.join()

        # Save audio file if we have frames
        if frames:
            with wave.open(temp_audio, 'wb') as wf:
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(audio.get_sample_size(FORMAT))
                wf.setframerate(RATE)
                wf.writeframes(b''.join(frames))

            try:
                # Combine audio and video
                video_clip = VideoFileClip(temp_video)
                audio_clip = AudioFileClip(temp_audio)
                final_clip = video_clip.with_audio(audio_clip)
                final_clip.write_videofile('camera_record4.mp4', codec='h264_nvenc')

                # Clean up clips
                video_clip.close()
                audio_clip.close()
            except Exception as e:
                print(f"Error combining audio and video: {e}")
            finally:
                # Clean up temporary files
                if os.path.exists(temp_video):
                    os.remove(temp_video)
                if os.path.exists(temp_audio):
                    os.remove(temp_audio)

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