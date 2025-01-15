import cv2
import click
import pyaudio
import wave
import time
import threading
import numpy as np
from moviepy import VideoFileClip, AudioFileClip, CompositeVideoClip
import os
@click.command()
@click.option('--device_index', default=1, type=int, help="Device index for recording audio")
def main(device_index, output_filename='camera_record4.mp4'):
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
                       input_device_index=device_index,
                       frames_per_buffer=CHUNK)

    frames = []  # For audio frames
    
    def record_audio():
        print("Recording audio...")
        for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK)
            frames.append(data)
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
    
    # Record for RECORD_SECONDS
    while (time.time() - start_time) < RECORD_SECONDS:
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

    # Clean up video recording
    cap.release()
    out.release()
    cv2.destroyAllWindows()

    # Clean up audio recording
    stream.stop_stream()
    stream.close()
    audio.terminate()

    # Save audio file
    with wave.open(temp_audio, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))

    # Combine audio and video
    video_clip = VideoFileClip(temp_video)
    audio_clip = AudioFileClip(temp_audio)
    final_clip = video_clip.with_audio(audio_clip)
    final_clip.write_videofile(output_filename, codec='h264_nvenc')

    # Clean up temporary files
    video_clip.close()
    audio_clip.close()
    if os.path.exists(temp_video):
        os.remove(temp_video)
    if os.path.exists(temp_audio):
        os.remove(temp_audio)

if __name__ == "__main__":
    main()