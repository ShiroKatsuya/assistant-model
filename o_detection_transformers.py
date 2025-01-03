import torch
import cv2
import numpy as np
import supervision as sv
from recording import (
    resume_audio_processing, 
    pause_audio_processing, 
    record_audio, 
    process_audio,
    audio_queue
)
import threading
from transformers import (
    AutoImageProcessor, 
    AutoModelForObjectDetection
)

def objek_deteksi(stop_event):
    CHECKPOINT = "PekingU/rtdetr_r50vd_coco_o365"
    DEVICE = torch.device("cuda") 
    if DEVICE.type == "cuda":
        print(f"Using GPU: {torch.cuda.get_device_name(0)}")
    else:
        print("Using CPU")

    model = AutoModelForObjectDetection.from_pretrained(CHECKPOINT).to(DEVICE)
    processor = AutoImageProcessor.from_pretrained(CHECKPOINT)

    cap = cv2.VideoCapture(0)
    if cap.isOpened():
        print("Camera opened successfully")
        resume_audio_processing()
        
        # Start audio recording thread
        record_thread = threading.Thread(target=record_audio, daemon=True)
        record_thread.start()
        
        # Start audio processing thread 
        process_thread = threading.Thread(target=process_audio, daemon=True)
        process_thread.start()
    else:
        print("Failed to open camera")
        return

    try:
        while not stop_event.is_set():
            ret, frame = cap.read()
            if not ret:
                break

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            inputs = processor(rgb_frame, return_tensors="pt").to(DEVICE)
            
            with torch.no_grad():
                outputs = model(**inputs)
            
            h, w = frame.shape[:2]
            results = processor.post_process_object_detection(
                outputs, target_sizes=[(h, w)], threshold=0.3)

            detections = sv.Detections.from_transformers(results[0])
            labels = [
                model.config.id2label[class_id]
                for class_id
                in detections.class_id
            ]

            annotated_frame = sv.BoundingBoxAnnotator().annotate(frame, detections)
            annotated_frame = sv.LabelAnnotator().annotate(annotated_frame, detections, labels=labels)

            cv2.imshow('Object Detection', annotated_frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()
        
        # Ensure all audio data is processed before stopping
        pause_audio_processing()
        
        # Wait for any remaining audio in queue to be processed
        audio_queue.join()
        
        # Add None to queue to signal threads to stop
        audio_queue.put(None)
        
        # Wait for threads to finish
        if record_thread.is_alive():
            record_thread.join(timeout=2)
        if process_thread.is_alive():    
            process_thread.join(timeout=2)

if __name__ == "__main__":
    objek_deteksi()
