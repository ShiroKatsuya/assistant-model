import tkinter as tk
from tkinter import ttk
import math
from PIL import Image, ImageTk, ImageDraw
import colorsys
import time

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

def draw_sound_wave(canvas, width, height, amplitude=10, frequency=0.05, phase=0):
    """Draw sound wave animation on canvas with futuristic neon effects"""
    canvas.delete("wave")
    mid_y = height // 2
    
    # Create gradient background effect
    for y in range(height):
        # Calculate distance from center
        distance = abs(y - mid_y) / (height / 2)
        # Create a subtle glow effect
        intensity = max(0, 1 - distance * 1.5)
        if intensity > 0:
            color = "#{:02x}{:02x}{:02x}".format(
                int(0 * intensity), 
                int(40 * intensity), 
                int(80 * intensity)
            )
            canvas.create_line(0, y, width, y, fill=color, tags="wave")
    
    # Draw multiple layered sound waves with glow effect
    wave_colors = [
        "#00E5FF",  # Bright cyan
        "#0091EA",  # Medium blue
        "#2979FF",  # Bright blue
    ]
    
    for layer, color in enumerate(wave_colors):
        layer_amp = amplitude * (0.7 + layer * 0.3)
        layer_freq = frequency * (1 + layer * 0.2)
        layer_phase = phase * (1 - layer * 0.1)
        layer_width = 3 - layer * 0.5
        
        # Draw the main wave
        points = []
        for x in range(0, width, 1):
            y = mid_y + int(layer_amp * math.sin(layer_freq * x + layer_phase))
            points.extend([x, y])
        
        if points:
            # Create glow effect with multiple lines of decreasing opacity
            for glow in range(3):
                glow_width = layer_width + glow * 2
                # Use separate RGB components instead of hex with alpha
                r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
                glow_alpha = 150 - glow * 50  # Decreasing alpha for glow effect
                # Apply alpha by adjusting the RGB values
                adjusted_r = int(r * glow_alpha / 255)
                adjusted_g = int(g * glow_alpha / 255)
                adjusted_b = int(b * glow_alpha / 255)
                glow_color = "#{:02x}{:02x}{:02x}".format(adjusted_r, adjusted_g, adjusted_b)
                canvas.create_line(points, fill=glow_color, width=glow_width, 
                                 smooth=True, tags="wave")
    
    # Draw dynamic particles with trails
    particle_colors = ["#00E5FF", "#64FFDA", "#EEFF41", "#FF3D00"]
    for i in range(20):
        # Varied particle movement patterns
        if i % 4 == 0:  # Floating particles
            particle_x = (phase * 150 + i * width/20) % width
            particle_y = mid_y + int(amplitude * 0.8 * math.sin(frequency * 2 * particle_x + phase * 3))
        elif i % 4 == 1:  # Orbiting particles
            angle = phase * 2 + i * 0.3
            radius = 20 + i % 5 * 5
            particle_x = (width/2 + math.cos(angle) * radius + phase * 20) % width
            particle_y = mid_y + math.sin(angle) * radius
        elif i % 4 == 2:  # Wave-following particles
            particle_x = (phase * 100 + i * 30) % width
            particle_y = mid_y + int(amplitude * 1.2 * math.sin(frequency * particle_x + phase))
        else:  # Random movement particles
            particle_x = (phase * 80 + i * 50) % width
            particle_y = mid_y + int(10 * math.cos(i + phase * 3))
        
        # Particle size based on position and time
        size = 2 + math.sin(phase * 5 + i * 0.5) * 1.5
        color = particle_colors[i % len(particle_colors)]
        
        # Draw particle with glow effect
        for glow in range(3):
            glow_size = size + glow * 1.5
            alpha = 255 - glow * 80
            # Parse the color and apply alpha by adjusting RGB values
            r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
            adjusted_r = int(r * alpha / 255)
            adjusted_g = int(g * alpha / 255)
            adjusted_b = int(b * alpha / 255)
            glow_color = "#{:02x}{:02x}{:02x}".format(adjusted_r, adjusted_g, adjusted_b)
            canvas.create_oval(
                particle_x-glow_size, particle_y-glow_size,
                particle_x+glow_size, particle_y+glow_size,
                fill=glow_color, outline="", tags="wave"
            )
        
        # Draw particle trail
        trail_length = int(3 + i % 3)
        for t in range(trail_length):
            trail_x = (particle_x - (t+1) * 3 * math.cos(phase * 2)) % width
            trail_y = particle_y - (t+1) * 1.5 * math.sin(phase * 2)
            trail_size = size * (trail_length - t) / trail_length * 0.8
            trail_alpha = 200 * (trail_length - t) / trail_length
            # Parse the color and apply alpha by adjusting RGB values
            r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
            adjusted_r = int(r * trail_alpha / 255)
            adjusted_g = int(g * trail_alpha / 255)
            adjusted_b = int(b * trail_alpha / 255)
            trail_color = "#{:02x}{:02x}{:02x}".format(adjusted_r, adjusted_g, adjusted_b)
            canvas.create_oval(
                trail_x-trail_size, trail_y-trail_size,
                trail_x+trail_size, trail_y+trail_size,
                fill=trail_color, outline="", tags="wave"
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