import pyaudio
import wave
import click
import time
import pyautogui
import cv2
import numpy as np
import threading
from moviepy import VideoFileClip, AudioFileClip, CompositeVideoClip

@click.command()
@click.option('--device_index', default=2, type=int, help="Device index for recording audio")
def main(device_index, output_filename='record3.mp4'):
    # Audio recording settings
    FORMAT = pyaudio.paInt16
    CHANNELS = 2
    RATE = 48000
    CHUNK = 1024
    RECORD_SECONDS = 20

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

    # Initialize video recording
    out = cv2.VideoWriter(temp_video, codec, fps, resolution)
    cv2.namedWindow("Live", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Live", 480, 270)

    frames = []  # For audio frames
    start_time = time.time()

    def record_audio():
        print("Recording audio...")
        for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK)
            frames.append(data)
        print("Audio recording finished")

    # Start audio recording in separate thread
    audio_thread = threading.Thread(target=record_audio)
    audio_thread.start()

    print("Recording video...")
    # Record video
    while True:
        img = pyautogui.screenshot()
        frame = np.array(img)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        out.write(frame)
        cv2.imshow('Live', frame)

        if cv2.waitKey(1) == ord('q') or time.time() - start_time >= RECORD_SECONDS:
            break

    # Clean up video recording
    out.release()
    cv2.destroyAllWindows()

    # Clean up audio recording
    stream.stop_stream()
    stream.close()
    audio.terminate()

    # Save audio to temp file
    wf = wave.open(temp_audio, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(audio.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

    # Combine audio and video
    video = VideoFileClip(temp_video)
    audio = AudioFileClip(temp_audio)
    final_clip = video.with_audio(audio)
    final_clip.write_videofile(output_filename)

    print(f"Recording saved to {output_filename}")

if __name__ == "__main__":
    main()