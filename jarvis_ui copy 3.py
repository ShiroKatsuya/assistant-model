import tkinter as tk
from tkinter import ttk
import math
from PIL import Image, ImageTk, ImageDraw
import colorsys
import time
import random

# Constants for styling
DARK_BG = "#121212"
DARKER_BG = "#0A0A0A"
PANEL_BG = "#1E1E1E"
ACCENT_BLUE = "#00A8FF"
ACCENT_ORANGE = "#FF5722"
TEXT_COLOR = "#E0E0E0"
FONT_FAMILY = "Consolas"  # Monospaced font with smooth curves

# UI component references
animation_canvas = None
progress_bar = None
notification_label = None
status_label = None
root = None

def create_neumorphic_frame(parent, width, height, bg_color, light_shadow, dark_shadow):
    """Create a neumorphic frame with soft shadows"""
    frame = tk.Frame(parent, width=width, height=height, bg=bg_color, bd=0, highlightthickness=0)
    
    # Create top-left light shadow
    light = tk.Frame(frame, bg=light_shadow, bd=0, highlightthickness=0)
    light.place(x=2, y=2, width=width-4, height=height-4)
    
    # Create bottom-right dark shadow
    dark = tk.Frame(frame, bg=dark_shadow, bd=0, highlightthickness=0)
    dark.place(x=4, y=4, width=width-4, height=height-4)
    
    # Create content frame
    content = tk.Frame(frame, bg=bg_color, bd=0, highlightthickness=0)
    content.place(x=3, y=3, width=width-6, height=height-6)
    
    return content

def draw_sound_wave(canvas=None, width=None, height=None, phase=0):
    """Draw a fiery eye animation on the canvas"""
    global animation_canvas
    
    # Use provided canvas or global animation_canvas
    canvas_to_use = canvas if canvas is not None else animation_canvas
    
    if canvas_to_use is None:
        return
        
    # Use provided dimensions or get from canvas
    if width is None:
        width = canvas_to_use.winfo_width()
    if height is None:
        height = canvas_to_use.winfo_height()
    
    # Clear previous drawings
    canvas_to_use.delete("wave")
    
    # Center coordinates
    center_x = width // 2
    center_y = height // 2
    
    # Eye size parameters
    eye_radius = min(width, height) // 4
    iris_radius = eye_radius * 0.7
    pupil_radius = iris_radius * 0.5
    
    # Calculate pulsation based on time for subtle animation
    pulse = math.sin(time.time() * 2 + phase) * 0.1 + 0.9
    flare = math.sin(time.time() * 3.5 + phase * 2) * 0.3 + 0.7
    
    # Draw the outer fiery glow (multiple layers with decreasing opacity)
    for i in range(5):
        glow_radius = eye_radius * (1.2 + i*0.15) * pulse
        # Use varying shades of red and orange without alpha
        red = 255
        green = int(30 + i*20)
        blue = max(5, i*3)
        color = f"#{red:02x}{green:02x}{blue:02x}"
        canvas_to_use.create_oval(
            center_x - glow_radius, center_y - glow_radius,
            center_x + glow_radius, center_y + glow_radius,
            fill=color, outline="", tags="wave"
        )
    
    # Draw the eye white (sclera) with a reddish tint
    canvas_to_use.create_oval(
        center_x - eye_radius, center_y - eye_radius * 0.8,
        center_x + eye_radius, center_y + eye_radius * 0.8,
        fill="#FFF0E0", outline="#FF3000", width=2, tags="wave"
    )
    
    # Draw the iris with fiery gradient
    for i in range(5):
        iris_size = iris_radius * (1 - i*0.15) * pulse
        # Create reddish-orange to yellow gradient
        hue = 0.05 + (i * 0.02)  # Slight variation in hue from red-orange to orange
        sat = 1.0 - (i * 0.05)   # Very saturated
        val = 1.0 - (i * 0.1)    # Brightness decreases slightly for inner rings
        r, g, b = colorsys.hsv_to_rgb(hue, sat, val)
        color = f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"
        canvas_to_use.create_oval(
            center_x - iris_size, center_y - iris_size,
            center_x + iris_size, center_y + iris_size,
            fill=color, outline="", tags="wave"
        )
    
    # Draw the pupil (black hole in the center)
    pupil_size = pupil_radius * pulse
    canvas_to_use.create_oval(
        center_x - pupil_size, center_y - pupil_size,
        center_x + pupil_size, center_y + pupil_size,
        fill="black", outline="", tags="wave"
    )
    
    # Add light reflections/highlights - use white with no transparency
    highlight_size = pupil_size * 0.4
    highlight_offset_x = eye_radius * 0.2
    highlight_offset_y = eye_radius * 0.2
    
    # Adjust brightness of highlights based on flare
    highlight_brightness = int(200 + 55 * flare)
    highlight_color = f"#{highlight_brightness:02x}{highlight_brightness:02x}{highlight_brightness:02x}"
    
    canvas_to_use.create_oval(
        center_x - highlight_offset_x - highlight_size, 
        center_y - highlight_offset_y - highlight_size,
        center_x - highlight_offset_x + highlight_size, 
        center_y - highlight_offset_y + highlight_size,
        fill=highlight_color, outline="", tags="wave"
    )
    
    # Add small secondary highlight
    small_highlight = highlight_size * 0.6
    secondary_brightness = int(180 + 75 * flare)
    secondary_color = f"#{secondary_brightness:02x}{secondary_brightness:02x}{secondary_brightness:02x}"
    
    canvas_to_use.create_oval(
        center_x + highlight_offset_y - small_highlight, 
        center_y + highlight_offset_x - small_highlight,
        center_x + highlight_offset_y + small_highlight, 
        center_y + highlight_offset_x + small_highlight,
        fill=secondary_color, outline="", tags="wave"
    )
    
    # Add random light flares around the eye
    if random.random() < 0.2:  # 20% chance of creating a flare
        flare_angle = random.uniform(0, 2 * math.pi)
        flare_distance = eye_radius * 1.2
        flare_x = center_x + math.cos(flare_angle) * flare_distance
        flare_y = center_y + math.sin(flare_angle) * flare_distance
        flare_size = random.uniform(eye_radius * 0.1, eye_radius * 0.2)
        
        # Use bright orange-red without alpha
        flare_brightness = int(200 + 55 * random.random())
        flare_color = f"#FF{flare_brightness//2:02x}{flare_brightness//4:02x}"
        
        canvas_to_use.create_oval(
            flare_x - flare_size, flare_y - flare_size,
            flare_x + flare_size, flare_y + flare_size,
            fill=flare_color, outline="", tags="wave"
        )

def draw_recording_animation(canvas, width, height, phase=0):
    """Draw recording animation with rotating timer and pulsating microphone"""
    canvas.delete("recording")
    
    # Center coordinates
    center_x = width // 2
    center_y = height // 2
    
    # Draw circular timer
    radius = min(width, height) // 3
    start_angle = 90
    extent = -phase * 360
    
    # Draw outline circle
    canvas.create_arc(center_x-radius, center_y-radius, 
                     center_x+radius, center_y+radius,
                     start=start_angle, extent=360, 
                     outline=TEXT_COLOR, width=2,
                     style=tk.ARC, tags="recording")
    
    # Draw progress arc
    canvas.create_arc(center_x-radius, center_y-radius, 
                     center_x+radius, center_y+radius,
                     start=start_angle, extent=extent, 
                     outline=ACCENT_ORANGE, width=3,
                     style=tk.ARC, tags="recording")
    
    # Draw pulsating microphone
    mic_size = int(radius * 0.6 * (1 + 0.1 * math.sin(phase * 10)))
    canvas.create_oval(center_x-mic_size//3, center_y-mic_size, 
                     center_x+mic_size//3, center_y+mic_size//2,
                     fill=ACCENT_BLUE, outline="", tags="recording")
    
    # Microphone stem
    canvas.create_rectangle(center_x-mic_size//6, center_y+mic_size//2, 
                          center_x+mic_size//6, center_y+mic_size,
                          fill=ACCENT_BLUE, outline="", tags="recording")
    
    # Microphone base
    canvas.create_rectangle(center_x-mic_size//2, center_y+mic_size, 
                          center_x+mic_size//2, center_y+mic_size*1.1,
                          fill=ACCENT_BLUE, outline="", tags="recording")

def draw_complete_animation(canvas, width, height):
    """Draw recording complete animation with floating tick icon"""
    canvas.delete("complete")
    
    # Center coordinates
    center_x = width // 2
    center_y = height // 2
    
    # Draw circle
    radius = min(width, height) // 3
    canvas.create_oval(center_x-radius, center_y-radius, 
                     center_x+radius, center_y+radius,
                     fill="#4CAF50", outline="", tags="complete")
    
    # Draw tick
    tick_points = [
        center_x-radius//2, center_y,
        center_x-radius//8, center_y+radius//2,
        center_x+radius//2, center_y-radius//3
    ]
    canvas.create_line(tick_points, fill=TEXT_COLOR, width=4, 
                     smooth=True, tags="complete")

def update_animation(status):
    """Update animation based on current status"""
    global animation_canvas, progress_bar, notification_label
    
    if animation_canvas is None:
        return
        
    width = animation_canvas.winfo_width()
    height = animation_canvas.winfo_height()
    
    if width <= 1 or height <= 1:  # Not yet properly sized
        animation_canvas.after(100, lambda: update_animation(status))
        return
        
    phase = time.time() % 1  # Animation phase between 0 and 1
    
    if status == "Waiting for sound...":
        draw_sound_wave(animation_canvas, width, height, phase=phase)
        if progress_bar:
            progress_bar.config(value=0)
            
    elif status == "Recording in progress...":
        draw_recording_animation(animation_canvas, width, height, phase=phase)
        if progress_bar:
            current_value = progress_bar["value"]
            progress_bar.config(value=min(current_value + 1, 100))
            
    elif status == "Recording complete":
        draw_complete_animation(animation_canvas, width, height)
        if progress_bar:
            progress_bar.config(value=100)
        # Show notification
        if notification_label:
            notification_label.place(relx=0.5, y=10, anchor="n")
            notification_label.after(3000, lambda: notification_label.place_forget())
    
    # Continue animation
    animation_canvas.after(50, lambda: update_animation(status))

def show_notification(message):
    """Show a temporary notification"""
    global notification_label, root
    
    if notification_label:
        notification_label.config(text=message)
        notification_label.place(relx=0.5, y=10, anchor="n")
        notification_label.after(3000, lambda: notification_label.place_forget())

def create_button(parent, text, command, is_primary=True):
    """Create a neumorphic button"""
    button_frame = tk.Frame(parent, bg=PANEL_BG, bd=0, highlightthickness=0)
    
    # Create inner button
    button = tk.Button(
        button_frame,
        text=text,
        font=(FONT_FAMILY, 10),
        bg=PANEL_BG,
        fg=ACCENT_ORANGE if is_primary else ACCENT_BLUE,
        activebackground=PANEL_BG,
        activeforeground=ACCENT_ORANGE if is_primary else ACCENT_BLUE,
        relief="flat",
        bd=0,
        highlightthickness=0,
        command=command,
    )
    button.pack(padx=15, pady=10)
    
    # Add ARIA properties for accessibility
    button.config(takefocus=1)  # Make it keyboard-focusable
    
    return button_frame

def setup_jarvis_ui(root_window, pause_func, resume_func):
    """Setup the JARVIS UI components"""
    global root, status_label, animation_canvas, progress_bar, notification_label
    
    root = root_window
    root.title("J.A.R.V.I.S. Screen Recorder")
    root.geometry("500x400")
    root.attributes('-topmost', True)
    root.configure(bg=DARK_BG)
    
    # Set application icon
    try:
        root.iconbitmap('icon.ico')  # You'll need to create this icon
    except:
        pass  # Icon not available, continue without it
    
    # Main container
    main_frame = tk.Frame(root, bg=DARK_BG, bd=0)
    main_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    # Title
    title_label = tk.Label(
        main_frame,
        text="J.A.R.V.I.S. AUDIO RECORDER",
        font=(FONT_FAMILY, 16, "bold"),
        bg=DARK_BG,
        fg=TEXT_COLOR
    )
    title_label.pack(pady=(0, 20))
    
    # Animation area - neumorphic panel
    animation_frame = tk.Frame(main_frame, bg=PANEL_BG, bd=0, highlightthickness=0)
    animation_frame.pack(fill="both", expand=True, pady=10)
    
    light_shadow = "#2A2A2A"  # Lighter shadow for neumorphism
    dark_shadow = "#0E0E0E"   # Darker shadow for neumorphism
    
    animation_canvas = tk.Canvas(
        animation_frame,
        bg=PANEL_BG,
        bd=0,
        highlightthickness=0,
        height=150
    )
    animation_canvas.pack(fill="both", expand=True, padx=3, pady=3)
    
    # Status frame
    status_frame = tk.Frame(main_frame, bg=DARK_BG, height=30)
    status_frame.pack(fill="x", pady=(10, 5))
    
    status_label = tk.Label(
        status_frame,
        text="Waiting for sound...",
        font=(FONT_FAMILY, 12),
        bg=DARK_BG,
        fg=TEXT_COLOR
    )
    status_label.pack(pady=5)
    status_label.config(anchor="center")
    
    # Progress bar
    progress_style = ttk.Style()
    progress_style.theme_use('alt')
    progress_style.configure(
        "TProgressbar", 
        thickness=6, 
        background=ACCENT_BLUE,
        troughcolor=DARKER_BG,
        borderwidth=0,
        lightcolor=ACCENT_BLUE,
        darkcolor=ACCENT_BLUE
    )
    
    progress_bar = ttk.Progressbar(
        main_frame,
        style="TProgressbar",
        orient="horizontal",
        length=460,
        mode="determinate"
    )
    progress_bar.pack(fill="x", pady=(5, 15))
    
    # Buttons frame
    buttons_frame = tk.Frame(main_frame, bg=DARK_BG)
    buttons_frame.pack(pady=10)
    
    # Start/Resume button
    start_button = create_button(
        buttons_frame, 
        "START RECORDING", 
        resume_func,
        True
    )
    start_button.pack(side="left", padx=10)
    
    # Stop button
    stop_button = create_button(
        buttons_frame, 
        "STOP RECORDING", 
        pause_func,
        False
    )
    stop_button.pack(side="left", padx=10)
    
    # Notification label (hidden initially)
    notification_label = tk.Label(
        root,
        text="Recording saved successfully",
        font=(FONT_FAMILY, 10),
        bg=PANEL_BG,
        fg=TEXT_COLOR,
        padx=10,
        pady=5
    )
    
    # Start animation
    update_animation("Waiting for sound...")
    
    # Key bindings for accessibility
    root.bind('<space>', lambda e: resume_func())
    root.bind('<Escape>', lambda e: pause_func())
    
    return status_label  # Return the status label for the main script to update

def update_status(status_text):
    """Update the status label text"""
    global status_label
    if status_label:
        status_label.config(text=status_text)
        update_animation(status_text) 