import torch
import google.generativeai as genai
import cv2
import numpy as np
import supervision as sv
import os
import speech_recognition as sr
import subprocess
from transformers import (
    AutoImageProcessor, 
    AutoModelForObjectDetection
)

def cleanup_files(*file_paths):
    for file_path in file_paths:
        try:
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"Error cleaning up file {file_path}: {e}")

def analyze_video(video_path):
    # Validate video file exists
    if not os.path.exists(video_path):
        print(f"Error: Video file {video_path} not found")
        return

    # Open the video file
    CHECKPOINT = "PekingU/rtdetr_r50vd_coco_o365"
    DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if DEVICE.type == "cuda":
        print(f"Using GPU: {torch.cuda.get_device_name(0)}")
    else:
        print("Using CPU")

    try:
        object_detection_model = AutoModelForObjectDetection.from_pretrained(CHECKPOINT).to(DEVICE)
        processor = AutoImageProcessor.from_pretrained(CHECKPOINT)
    except Exception as e:
        print(f"Error loading models: {e}")
        return

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Error: Could not open video file")
        return

    # Initialize speech recognizer
    recognizer = sr.Recognizer()

    # Extract audio from video
    audio_path = video_path.replace('.mp4', '.wav')
    try:
        subprocess.run(['ffmpeg', '-i', video_path, '-vn', '-acodec', 'pcm_s16le', '-ar', '16000', '-ac', '1', audio_path], 
                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error extracting audio: {e}")
        return
    
    # Transcribe audio using Google Speech Recognition
    speech_text = ""
    try:
        with sr.AudioFile(audio_path) as source:
            audio = recognizer.record(source)
            try:
                speech_text = recognizer.recognize_google(audio)
            except sr.UnknownValueError:
                print("Google Speech Recognition could not understand audio")
            except sr.RequestError as e:
                print(f"Could not request results from Google Speech Recognition service; {e}")
    except Exception as e:
        print(f"Error processing audio file: {e}")
        cleanup_files(audio_path)
        return

    detected_objects = []
    frame_count = 0
    try:
        # Get total frames for progress tracking
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Increase frame skip rate
        FRAME_SKIP = 10  # Process every 10th frame instead of every 3rd
        
        # Pre-calculate target size
        ret, frame = cap.read()
        if ret:
            target_height = 480  # Reduced height for faster processing
            aspect_ratio = frame.shape[1] / frame.shape[0]
            target_width = int(target_height * aspect_ratio)
            target_size = (target_width, target_height)
            
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Reset to start
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1
            if frame_count % FRAME_SKIP != 0:  # Process fewer frames
                continue

            # Resize frame for faster processing
            frame = cv2.resize(frame, target_size)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            try:
                inputs = processor(rgb_frame, return_tensors="pt").to(DEVICE)
                
                with torch.no_grad():
                    outputs = object_detection_model(**inputs)
                
                h, w = frame.shape[:2]
                results = processor.post_process_object_detection(
                    outputs, target_sizes=[(h, w)], threshold=0.3)

                detections = sv.Detections.from_transformers(results[0])
                labels = [
                    object_detection_model.config.id2label[class_id]
                    for class_id
                    in detections.class_id
                ]
                detected_objects.extend(labels)

                # Only show frame if explicitly needed
                if False:  # Disable real-time display by default
                    annotated_frame = sv.BoxAnnotator().annotate(frame, detections)
                    annotated_frame = sv.LabelAnnotator().annotate(annotated_frame, detections, labels=labels)
                    cv2.imshow('Object Detection', annotated_frame)
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord('q'):
                        break

                # Print progress
                if frame_count % 30 == 0:
                    progress = (frame_count / total_frames) * 100
                    print(f"Processing: {progress:.1f}%", end='\r')

            except Exception as e:
                print(f"Error processing frame {frame_count}: {e}")
                continue

    except Exception as e:
        print(f"Error during video processing: {e}")
    finally:
        # Pastikan semua resources dilepaskan dengan benar
        cv2.destroyAllWindows()  # Tutup semua window terlebih dahulu
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Reset posisi frame
        cap.release()  # Kemudian release capture

    try:
        # Configure Gemini
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        if not os.getenv("GEMINI_API_KEY"):
            raise ValueError("GEMINI_API_KEY environment variable not set")
            
        generative_model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Generate analysis of speech first
        prompt = f"""
        Analisis Video:

        Transkrip ucapan dalam video:
        {speech_text}

        Please watch this video and give me a brief, natural response as if we were having a casual conversation. 
        Keep your response concise and conversational, like you're chatting with a friend about what you just watched.
        
        Note: Objek yang terdeteksi dalam video telah disimpan dan akan dibahas setelah mendapat konfirmasi dari pengguna.
        Ketik 'discuss objects' untuk melihat dan membahas objek yang terdeteksi dalam video.
        """

        response = generative_model.generate_content([prompt])
        print(response.text)

        # Wait for user confirmation
        user_input = input("\nKetik 'discuss objects' untuk melihat objek yang terdeteksi: ")
        
        if user_input.lower() == "discuss objects":
            object_prompt = f"""
            Objek yang terdeteksi dalam video:
            {', '.join(set(detected_objects))}
            
            Berikan analisis tentang objek-objek yang terdeteksi dalam video.
            """
            object_response = generative_model.generate_content([object_prompt])
            print(object_response.text)

    except Exception as e:
        print(f"Error generating analysis: {e}")
    finally:
        # Cleanup
        cleanup_files(audio_path)

if __name__ == "__main__":
    video_path = "sample_voice.mp4"
    analyze_video(video_path)