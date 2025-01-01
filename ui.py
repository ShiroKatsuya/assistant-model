import tkinter as tk
import os
from PIL import Image, ImageTk
from tkinter import Label
import cv2
import numpy as np
import torch

# Create the main window
root = tk.Tk()
root.geometry('800x700')  # Changed to landscape dimensions

# Create a label to display the video
video_label = Label(root)
video_label.pack(expand=True, fill='both')

# Initialize video capture
cap = cv2.VideoCapture('Otakudesu.io_FSGK--01_Mkv1080p.mkv')

# Check if CUDA is available
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Function to update frames
def update_frame():
    ret, frame = cap.read()
    if ret:
        # Convert BGR to RGB
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Convert frame to tensor and move to GPU
        frame_tensor = torch.from_numpy(frame).to(device)
        
        # Resize frame using GPU
        frame_tensor = torch.nn.functional.interpolate(
            frame_tensor.permute(2, 0, 1).unsqueeze(0).float(),
            size=(700, 800),
            mode='bilinear',
            align_corners=False
        )
        
        # Convert back to numpy array
        frame = frame_tensor.squeeze(0).permute(1, 2, 0).cpu().numpy().astype(np.uint8)
        
        # Convert to PhotoImage
        image = Image.fromarray(frame)
        photo = ImageTk.PhotoImage(image=image)
        
        # Update label
        video_label.configure(image=photo)
        video_label.image = photo
    else:
        # Reset video to beginning when it ends
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    
    # Schedule next update    
    root.after(33, update_frame)  # Update roughly every 33ms (30 fps)

# Start the update loop
root.after(33, update_frame)

# Clean up function
def on_closing():
    cap.release()
    cv2.destroyAllWindows()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)

# Run the application
root.mainloop()