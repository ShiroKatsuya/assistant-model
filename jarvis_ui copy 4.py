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
    """Draw a mechanical red eye animation on the canvas"""
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
    outer_radius = min(width, height) // 3
    inner_radius = outer_radius * 0.85
    core_radius = outer_radius * 0.6
    
    # Calculate pulsation based on time for subtle animation
    pulse = math.sin(time.time() * 1.5 + phase) * 0.05 + 0.95
    spin = (time.time() * 0.2 + phase) % (2 * math.pi)
    
    # Draw outer metallic ring (dark gray with light edge)
    canvas_to_use.create_oval(
        center_x - outer_radius, center_y - outer_radius,
        center_x + outer_radius, center_y + outer_radius,
        fill="#2A2A2A", outline="#808080", width=2, tags="wave"
    )
    
    # Draw inner dark circle
    canvas_to_use.create_oval(
        center_x - inner_radius, center_y - inner_radius,
        center_x + inner_radius, center_y + inner_radius,
        fill="#101010", outline="#404040", width=1, tags="wave"
    )
    
    # Draw core red glowing circle
    canvas_to_use.create_oval(
        center_x - core_radius * pulse, center_y - core_radius * pulse,
        center_x + core_radius * pulse, center_y + core_radius * pulse,
        fill="#FF1800", outline="#FF3000", width=1, tags="wave"
    )
    
    # Draw concentric scanner rings (multiple red circles of decreasing size)
    for i in range(5):
        ring_size = core_radius * (0.9 - i * 0.15) * pulse
        ring_color = f"#{255:02x}{30+i*15:02x}{10+i*5:02x}"
        canvas_to_use.create_oval(
            center_x - ring_size, center_y - ring_size,
            center_x + ring_size, center_y + ring_size,
            fill=ring_color, outline="#FF4000", width=1, tags="wave"
        )
    
    # Add scanner lines radiating from center
    num_lines = 36
    line_length_outer = core_radius * 0.9
    line_length_inner = core_radius * 0.4
    for i in range(num_lines):
        angle = 2 * math.pi * i / num_lines
        # Draw longer lines at certain intervals
        if i % 3 == 0:
            length = line_length_outer
            width = 2
        else:
            length = line_length_inner
            width = 1
            
        inner_x = center_x + math.cos(angle) * core_radius * 0.3
        inner_y = center_y + math.sin(angle) * core_radius * 0.3
        outer_x = center_x + math.cos(angle) * length
        outer_y = center_y + math.sin(angle) * length
        
        canvas_to_use.create_line(
            inner_x, inner_y, outer_x, outer_y,
            fill="#FF3000", width=width, tags="wave"
        )
    
    # Add rotating scanner element
    scan_length = core_radius * 0.9
    for i in range(3):
        scan_angle = spin + (2 * math.pi / 3) * i
        scan_x = center_x + math.cos(scan_angle) * scan_length
        scan_y = center_y + math.sin(scan_angle) * scan_length
        
        # Draw scanning line
        canvas_to_use.create_line(
            center_x, center_y, scan_x, scan_y,
            fill="#FFFFFF", width=2, tags="wave"
        )
        
        # Draw dot at end of scanning line
        scan_dot_size = outer_radius * 0.04
        canvas_to_use.create_oval(
            scan_x - scan_dot_size, scan_y - scan_dot_size,
            scan_x + scan_dot_size, scan_y + scan_dot_size,
            fill="#FFFFFF", outline="", tags="wave"
        )
    
    # Add metallic segments around the outside (gray tabs)
    num_segments = 8
    segment_size = outer_radius * 0.15
    for i in range(num_segments):
        segment_angle = 2 * math.pi * i / num_segments
        segment_x = center_x + math.cos(segment_angle) * (outer_radius + segment_size * 0.6)
        segment_y = center_y + math.sin(segment_angle) * (outer_radius + segment_size * 0.6)
        
        canvas_to_use.create_rectangle(
            segment_x - segment_size, segment_y - segment_size * 0.6,
            segment_x + segment_size, segment_y + segment_size * 0.6,
            fill="#404040", outline="#606060", width=1, tags="wave"
        )
    
    # Add central bright core
    core_size = core_radius * 0.25 * pulse
    canvas_to_use.create_oval(
        center_x - core_size, center_y - core_size,
        center_x + core_size, center_y + core_size,
        fill="#FFFFFF", outline="#FFCCCC", width=1, tags="wave"
    )
    
    # Add lens flare effect
    flare_size = core_size * 0.8
    canvas_to_use.create_line(
        center_x - flare_size * 2, center_y - flare_size * 2,
        center_x + flare_size * 2, center_y + flare_size * 2,
        fill="#FFCCCC", width=1, tags="wave"
    )
    canvas_to_use.create_line(
        center_x - flare_size * 2, center_y + flare_size * 2,
        center_x + flare_size * 2, center_y - flare_size * 2,
        fill="#FFCCCC", width=1, tags="wave"
    )

def draw_recording_animation(canvas, width, height, phase=0):
    """Draw futuristic recording animation with holographic elements"""
    canvas.delete("recording")
    
    # Center coordinates
    center_x = width // 2
    center_y = height // 2
    
    # Size parameters
    outer_radius = min(width, height) // 3
    inner_radius = outer_radius * 0.7
    
    # Animation parameters
    pulse = math.sin(time.time() * 2) * 0.1 + 0.9
    rotation = (time.time() * 0.5 + phase) % (2 * math.pi)
    
    # Draw outer hexagonal frame
    hex_points = []
    for i in range(6):
        angle = math.pi/6 + i * math.pi/3 + rotation * 0.1
        hex_x = center_x + math.cos(angle) * outer_radius * 1.1
        hex_y = center_y + math.sin(angle) * outer_radius * 1.1
        hex_points.extend([hex_x, hex_y])
    
    canvas.create_polygon(
        hex_points, 
        fill="", 
        outline=ACCENT_BLUE, 
        width=2, 
        tags="recording"
    )
    
    # Draw inner hexagonal frame
    inner_hex_points = []
    for i in range(6):
        angle = math.pi/6 + i * math.pi/3 - rotation * 0.2
        hex_x = center_x + math.cos(angle) * outer_radius * 0.8
        hex_y = center_y + math.sin(angle) * outer_radius * 0.8
        inner_hex_points.extend([hex_x, hex_y])
    
    canvas.create_polygon(
        inner_hex_points, 
        fill="", 
        outline=ACCENT_ORANGE, 
        width=2, 
        tags="recording"
    )
    
    # Draw circular progress indicator
    start_angle = 90
    extent = -phase * 360
    
    # Draw base circle
    canvas.create_arc(
        center_x - inner_radius, center_y - inner_radius,
        center_x + inner_radius, center_y + inner_radius,
        start=start_angle, extent=360,
        outline="#303030", width=3,
        style=tk.ARC, tags="recording"
    )
    
    # Draw progress arc
    canvas.create_arc(
        center_x - inner_radius, center_y - inner_radius,
        center_x + inner_radius, center_y + inner_radius,
        start=start_angle, extent=extent,
        outline=ACCENT_BLUE, width=4,
        style=tk.ARC, tags="recording"
    )
    
    # Draw holographic tech circles
    for i in range(3):
        orbit_radius = inner_radius * (0.4 + i * 0.15)
        orbit_phase = rotation + i * (2 * math.pi / 3)
        orbit_x = center_x + math.cos(orbit_phase) * orbit_radius
        orbit_y = center_y + math.sin(orbit_phase) * orbit_radius
        
        # Draw orbiting element
        orbit_size = outer_radius * 0.08 * pulse
        canvas.create_oval(
            orbit_x - orbit_size, orbit_y - orbit_size,
            orbit_x + orbit_size, orbit_y + orbit_size,
            fill=ACCENT_ORANGE, outline="", tags="recording"
        )
        
        # Draw connecting line to center
        canvas.create_line(
            center_x, center_y, orbit_x, orbit_y,
            fill=ACCENT_ORANGE, width=1, tags="recording"
        )
    
    # Draw central recording indicator
    # Pulsating inner circle
    inner_size = inner_radius * 0.25 * pulse
    canvas.create_oval(
        center_x - inner_size, center_y - inner_size,
        center_x + inner_size, center_y + inner_size,
        fill="#FF3000", outline=ACCENT_ORANGE, width=2, tags="recording"
    )
    
    # Add tech details - digital particles
    for i in range(8):
        particle_angle = 2 * math.pi * i / 8 + rotation
        particle_distance = inner_radius * 0.5 + math.sin(time.time() * 3 + i) * inner_radius * 0.1
        particle_x = center_x + math.cos(particle_angle) * particle_distance
        particle_y = center_y + math.sin(particle_angle) * particle_distance
        
        particle_size = outer_radius * 0.02 * (1 + math.sin(time.time() * 5 + i) * 0.5)
        canvas.create_rectangle(
            particle_x - particle_size, particle_y - particle_size,
            particle_x + particle_size, particle_y + particle_size,
            fill=ACCENT_BLUE, outline="", tags="recording"
        )
    
    # Add digital scan lines
    for i in range(10):
        y_pos = center_y - inner_radius + inner_radius * 2 * i / 10
        opacity = int(100 * math.sin(y_pos / 10 + time.time() * 3) ** 2)
        if opacity > 10:  # Only draw visible lines
            line_width = 1 + int(opacity / 50)
            canvas.create_line(
                center_x - inner_radius, y_pos,
                center_x + inner_radius, y_pos,
                fill=ACCENT_BLUE, width=line_width, tags="recording"
            )

def draw_complete_animation(canvas, width, height):
    """Draw futuristic completion animation with holographic elements"""
    canvas.delete("complete")
    
    # Center coordinates
    center_x = width // 2
    center_y = height // 2
    
    # Size parameters
    outer_radius = min(width, height) // 3
    inner_radius = outer_radius * 0.85
    
    # Animation timing parameters
    current_time = time.time()
    pulse = math.sin(current_time * 2) * 0.1 + 0.9
    fast_pulse = math.sin(current_time * 5) * 0.5 + 0.5
    
    # Draw outer hexagonal frame - success color
    success_color = "#4CAF50"  # Green color
    hex_points = []
    for i in range(6):
        angle = math.pi/6 + i * math.pi/3 + current_time * 0.1
        hex_x = center_x + math.cos(angle) * outer_radius * 1.1
        hex_y = center_y + math.sin(angle) * outer_radius * 1.1
        hex_points.extend([hex_x, hex_y])
    
    canvas.create_polygon(
        hex_points, 
        fill="", 
        outline=success_color, 
        width=2, 
        tags="complete"
    )
    
    # Draw pulsing completed circle
    canvas.create_oval(
        center_x - inner_radius * pulse, center_y - inner_radius * pulse,
        center_x + inner_radius * pulse, center_y + inner_radius * pulse,
        fill="#103010", outline=success_color, width=3,
        tags="complete"
    )
    
    # Draw smaller inner circle with different pulse rate
    inner_pulse = math.sin(current_time * 3) * 0.1 + 0.9
    canvas.create_oval(
        center_x - inner_radius * 0.7 * inner_pulse, center_y - inner_radius * 0.7 * inner_pulse,
        center_x + inner_radius * 0.7 * inner_pulse, center_y + inner_radius * 0.7 * inner_pulse,
        fill="#205020", outline="#60C060", width=2,
        tags="complete"
    )
    
    # Draw tech circle segments
    for i in range(8):
        start_angle = i * 45
        canvas.create_arc(
            center_x - inner_radius * 0.8, center_y - inner_radius * 0.8,
            center_x + inner_radius * 0.8, center_y + inner_radius * 0.8,
            start=start_angle, extent=30,
            style=tk.ARC, outline="#60FF60", width=2 if i % 2 == 0 else 1,
            tags="complete"
        )
    
    # Draw a sleek check mark using Bezier curve effect
    # Main diagonal line
    check_size = inner_radius * 0.6
    canvas.create_line(
        center_x - check_size * 0.5, center_y,
        center_x - check_size * 0.1, center_y + check_size * 0.5,
        center_x + check_size * 0.6, center_y - check_size * 0.4,
        fill="#FFFFFF", width=4, smooth=True, tags="complete"
    )
    
    # Add tech details - digital particles
    for i in range(12):
        particle_angle = 2 * math.pi * i / 12 + current_time * 0.2
        particle_distance = inner_radius * (0.5 + fast_pulse * 0.2)
        particle_x = center_x + math.cos(particle_angle) * particle_distance
        particle_y = center_y + math.sin(particle_angle) * particle_distance
        
        # Alternate between squares and circles
        particle_size = outer_radius * 0.03 * (1 + math.sin(current_time * 3 + i) * 0.3)
        if i % 2 == 0:
            canvas.create_rectangle(
                particle_x - particle_size, particle_y - particle_size,
                particle_x + particle_size, particle_y + particle_size,
                fill="#80FF80", outline="", tags="complete"
            )
        else:
            canvas.create_oval(
                particle_x - particle_size, particle_y - particle_size,
                particle_x + particle_size, particle_y + particle_size,
                fill="#40B040", outline="", tags="complete"
            )
    
    # Add central glow
    glow_size = check_size * 0.3 * pulse
    canvas.create_oval(
        center_x - glow_size, center_y - glow_size,
        center_x + glow_size, center_y + glow_size,
        fill="#FFFFFF", outline="#80FF80", width=2, tags="complete"
    )
    
    # Add digital scan line effect
    num_scan_lines = 5
    for i in range(num_scan_lines):
        scan_y = center_y - inner_radius + inner_radius * 2 * ((current_time * 0.5 + i/num_scan_lines) % 1)
        canvas.create_line(
            center_x - inner_radius, scan_y,
            center_x + inner_radius, scan_y,
            fill="#80FF80", width=1, tags="complete"
        )

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