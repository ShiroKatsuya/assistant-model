import torch
import cv2
import supervision as sv
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

    try:
        while not stop_event.is_set():
            ret, frame = cap.read()
            if not ret:
                print("Failed to read frame from camera.")
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

            annotated_frame = sv.BoxAnnotator().annotate(frame, detections)
            annotated_frame = sv.LabelAnnotator().annotate(annotated_frame, detections, labels=labels)

            cv2.imshow('Object Detection', annotated_frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("Quit signal received. Stopping camera.")
                break
    except Exception as e:
        print(f"An error occurred during object detection: {e}")
    finally:
        cap.release()
        cv2.destroyAllWindows()
        print("Camera has been released and windows closed.")

def listen_for_commands(stop_event):
    """Listen for the 'stop camera' command to stop the camera."""
    while True:
        command = input("Enter command: ").strip().lower()
        if command == "stop camera":
            print("Stop camera command received.")
            stop_event.set()
            break
        else:
            print(f"Unknown command: {command}. Type 'stop camera' to stop the camera.")

if __name__ == "__main__":
    stop_event = threading.Event()

    camera_thread = threading.Thread(target=objek_deteksi, args=(stop_event,))
    camera_thread.start()

    command_thread = threading.Thread(target=listen_for_commands, args=(stop_event,))
    command_thread.start()

    # Wait for the camera thread to finish
    camera_thread.join()
    # Optionally, wait for the command thread to finish
    command_thread.join()

    print("Camera has been stopped. Program continues running.")
    # You can add additional code here to keep the program running or perform other tasks
