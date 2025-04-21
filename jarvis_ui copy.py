import tkinter as tk
from tkinter import ttk
import math
from PIL import Image, ImageTk, ImageDraw
import colorsys
import time
import random

# Constants for futuristic styling
DARK_BG = "#080C12"  # Darker background for contrast
DARKER_BG = "#050709"  # Even darker for depth
PANEL_BG = "#0E1621"  # Slightly blue-tinted dark panels
GLASS_BG = "#101D2A"  # Semi-transparent look (without actual transparency)

# Accent colors (more vibrant)
ACCENT_BLUE = "#00E5FF"  # Brighter, more holographic blue
ACCENT_GREEN = "#00F2A9"  # Teal-green for secondary accent
ACCENT_ORANGE = "#FF3D00"  # Brighter orange for warnings/attention
TEXT_COLOR = "#E0F7FF"  # Slightly blue-tinted white for better contrast
TEXT_COLOR_DIM = "#90A4AE"  # Dimmed text for secondary information

# Fonts
FONT_FAMILY = "Consolas"  # Base monospaced font
ALT_FONT = "Courier New"  # Alternative monospaced font

# UI component references
animation_canvas = None
progress_bar = None
notification_label = None
status_label = None
root = None
particle_system = []  # For holographic particle effects

class Particle:
    """Particle class for holographic effects"""
    def __init__(self, canvas, x, y, color=ACCENT_BLUE):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.size = random.uniform(1, 3)
        self.color = color
        self.speed = random.uniform(0.5, 2)
        self.alpha = random.uniform(0.3, 0.9)
        self.id = None
        
    def update(self):
        self.y -= self.speed
        self.alpha -= 0.01
        if self.alpha <= 0:
            self.alpha = random.uniform(0.3, 0.9)
            self.y += random.uniform(10, 30)
        
        # Instead of using alpha, just adjust the brightness
        r, g, b = int(self.color[1:3], 16), int(self.color[3:5], 16), int(self.color[5:7], 16)
        # Scale the brightness based on alpha value
        r = int(r * self.alpha)
        g = int(g * self.alpha)
        b = int(b * self.alpha)
        color = f"#{r:02x}{g:02x}{b:02x}"
        
        return self.x, self.y, self.size, color

def create_glassmorphic_frame(parent, width, height, bg_color=GLASS_BG, border_color=ACCENT_BLUE, border_width=1, corner_radius=10):
    """Create a glassmorphic frame with translucent background and subtle glow"""
    frame = tk.Frame(parent, width=width, height=height, bg=DARKER_BG, bd=0, highlightthickness=border_width, highlightbackground=border_color)
    
    # Add subtle inner glow (we'll fake this with another frame)
    inner_glow = tk.Frame(frame, bg=DARKER_BG, bd=0)
    inner_glow.place(relx=0.5, rely=0.5, width=width-8, height=height-8, anchor="center")
    
    # Create content frame
    content = tk.Frame(inner_glow, bg=bg_color, bd=0)
    content.place(relx=0.5, rely=0.5, width=width-12, height=height-12, anchor="center")
    
    return content

def draw_holographic_border(canvas, x, y, width, height, color=ACCENT_BLUE, pulse_speed=0.05):
    """Draw a pulsating holographic border"""
    # Delete previous border
    canvas.delete("holo_border")
    
    # Calculate pulse effect (0.0 to 1.0)
    pulse = (math.sin(time.time() * pulse_speed * 10) + 1) / 2
    
    # Instead of alpha, vary brightness based on pulse
    r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
    # Adjust brightness based on pulse (avoiding alpha)
    r = min(255, int(r * (0.6 + 0.4 * pulse)))
    g = min(255, int(g * (0.6 + 0.4 * pulse)))
    b = min(255, int(b * (0.6 + 0.4 * pulse)))
    border_color = f"#{r:02x}{g:02x}{b:02x}"
    
    # Draw the border with rounded corners
    canvas.create_rectangle(x, y, x+width, y+height, outline=border_color, width=2, 
                           tags="holo_border")

def draw_sound_wave(canvas, width, height, amplitude=15, frequency=0.05, phase=0):
    """Draw advanced sound wave animation with particles on canvas"""
    canvas.delete("wave")
    mid_y = height // 2
    
    # Create wave layers (multiple waves with different phases and colors)
    wave_colors = [ACCENT_BLUE, ACCENT_GREEN]
    wave_alphas = [0.8, 0.4]  # Different transparency levels
    
    for layer, (color, alpha) in enumerate(zip(wave_colors, wave_alphas)):
        layer_phase = phase + layer * 0.5
        layer_amp = amplitude * (0.8 if layer == 0 else 0.6)
        points = []
        
        # Create smooth wave using multiple points
        for x in range(0, width, 2):
            y = mid_y + int(layer_amp * math.sin(frequency * x + layer_phase))
            points.extend([x, y])
            
        if points:
            # Convert color to a dimmer version instead of using alpha
            r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
            # Scale RGB values by alpha to simulate transparency
            r = int(r * alpha)
            g = int(g * alpha)
            b = int(b * alpha)
            wave_color = f"#{r:02x}{g:02x}{b:02x}"
            
            # Draw smooth curve
            canvas.create_line(points, fill=wave_color, width=2, smooth=True, tags="wave")
    
    # Draw holographic particles that move along the wave
    for i in range(5):
        particle_x = (phase * 300 + i * 90) % width
        particle_y = mid_y + int(amplitude * 0.8 * math.sin(frequency * particle_x + phase))
        size = 3 if i % 2 == 0 else 2
        
        # Gradient from green to blue based on position
        blend = (math.sin(particle_x * 0.01) + 1) / 2
        r = int(0)
        g = int(blend * 229 + (1-blend) * 242)
        b = int(blend * 255 + (1-blend) * 169)
        particle_color = f"#{r:02x}{g:02x}{b:02x}"
        
        canvas.create_oval(particle_x-size, particle_y-size, 
                         particle_x+size, particle_y+size, 
                         fill=particle_color, tags="wave", outline="")

def draw_recording_animation(canvas, width, height, phase=0):
    """Draw advanced recording animation with rotating timer and pulsating microphone"""
    canvas.delete("recording")
    
    # Center coordinates
    center_x = width // 2
    center_y = height // 2
    
    # Draw circular timer with holographic effect
    radius = min(width, height) // 3
    for i in range(3):  # Multiple layers for depth
        layer_radius = radius - i * 2
        start_angle = 90
        extent = -phase * 360
        
        # Gradient color based on layer
        blend = 1 - (i / 3)
        r, g, b = 0, int(240 * blend), int(255 * blend)
        arc_color = f"#{r:02x}{g:02x}{b:02x}"
        
        # Draw progress arc
        canvas.create_arc(center_x-layer_radius, center_y-layer_radius, 
                         center_x+layer_radius, center_y+layer_radius,
                         start=start_angle, extent=extent, 
                         outline=arc_color, width=2 if i == 0 else 1,
                         style=tk.ARC, tags="recording")
    
    # Draw background glow
    glow_size = int(radius * 1.1 * (1 + 0.05 * math.sin(phase * 8)))
    canvas.create_oval(center_x-glow_size, center_y-glow_size, 
                     center_x+glow_size, center_y+glow_size,
                     fill="", outline=ACCENT_BLUE, width=1, tags="recording")
    
    # Draw pulsating microphone with holographic effect
    mic_size = int(radius * 0.6 * (1 + 0.07 * math.sin(phase * 10)))
    
    # Microphone head
    canvas.create_oval(center_x-mic_size//3, center_y-mic_size, 
                     center_x+mic_size//3, center_y+mic_size//2,
                     fill=ACCENT_BLUE, outline=ACCENT_GREEN, width=1, tags="recording")
    
    # Microphone stem with glow
    canvas.create_rectangle(center_x-mic_size//6, center_y+mic_size//2, 
                          center_x+mic_size//6, center_y+mic_size,
                          fill=ACCENT_BLUE, outline="", tags="recording")
    
    # Microphone base with layered effect
    canvas.create_rectangle(center_x-mic_size//2, center_y+mic_size, 
                          center_x+mic_size//2, center_y+mic_size*1.1,
                          fill=ACCENT_BLUE, outline=ACCENT_GREEN, width=1, tags="recording")
    
    # Add sound wave visualization around the microphone
    wave_radius = mic_size * 1.2
    wave_points = []
    for angle in range(0, 360, 10):
        # Vary the wave radius with phase
        r = wave_radius * (1 + 0.1 * math.sin(math.radians(angle) * 3 + phase * 10))
        x = center_x + r * math.cos(math.radians(angle))
        y = center_y + r * math.sin(math.radians(angle))
        wave_points.append(x)
        wave_points.append(y)
    
    canvas.create_line(wave_points, smooth=True, fill=ACCENT_GREEN, width=1, 
                     tags="recording")

def draw_complete_animation(canvas, width, height):
    """Draw enhanced recording complete animation with floating tick icon and particles"""
    canvas.delete("complete")
    
    # Center coordinates
    center_x = width // 2
    center_y = height // 2
    
    # Draw circle with glow effect
    radius = min(width, height) // 3
    canvas.create_oval(center_x-radius, center_y-radius, 
                     center_x+radius, center_y+radius,
                     fill=ACCENT_GREEN, outline=ACCENT_BLUE, width=2, tags="complete")
    
    # Draw outer glow
    glow_radius = radius * 1.15
    canvas.create_oval(center_x-glow_radius, center_y-glow_radius, 
                     center_x+glow_radius, center_y+glow_radius,
                     fill="", outline=ACCENT_GREEN, width=1, tags="complete")
    
    # Draw tick with enhanced style
    tick_points = [
        center_x-radius//2, center_y,
        center_x-radius//8, center_y+radius//2,
        center_x+radius//2, center_y-radius//3
    ]
    canvas.create_line(tick_points, fill=TEXT_COLOR, width=4, 
                     smooth=True, tags="complete")
    
    # Add particle effects
    global particle_system
    particle_system = []
    for _ in range(20):
        angle = random.uniform(0, math.pi * 2)
        distance = random.uniform(radius * 0.5, radius)
        x = center_x + math.cos(angle) * distance
        y = center_y + math.sin(angle) * distance
        particle_system.append(Particle(canvas, x, y, ACCENT_GREEN))

def update_particles(canvas):
    """Update and draw all particles in the system"""
    if not particle_system:
        return
        
    canvas.delete("particles")
    
    for particle in particle_system:
        x, y, size, color = particle.update()
        canvas.create_oval(x-size, y-size, x+size, y+size, 
                         fill=color, outline="", tags="particles")

def update_animation(status):
    """Update animation based on current status"""
    global animation_canvas, progress_bar, notification_label, particle_system
    
    if animation_canvas is None:
        return
    
    try:
        width = animation_canvas.winfo_width()
        height = animation_canvas.winfo_height()
        
        if width <= 1 or height <= 1:  # Not yet properly sized
            animation_canvas.after(100, lambda: update_animation(status))
            return
            
        phase = time.time() % 1  # Animation phase between 0 and 1
        
        # Draw holographic border around the canvas
        draw_holographic_border(animation_canvas, 2, 2, width-4, height-4, 
                               color=ACCENT_BLUE if "Recording" in status else ACCENT_GREEN)
        
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
            update_particles(animation_canvas)
            if progress_bar:
                progress_bar.config(value=100)
        
        # Continue animation
        animation_canvas.after(30, lambda: update_animation(status))  # Smoother 30ms refresh rate
    except Exception as e:
        print(f"Error in animation update: {e}")
        # Try to recover by scheduling next frame
        animation_canvas.after(100, lambda: update_animation(status))

def show_notification(message, type="info"):
    """Show a temporary holographic notification"""
    global notification_label, root
    
    if notification_label is None or root is None:
        print("Warning: Notification label or root not initialized")
        return
        
    try:
        # Choose color based on notification type
        if type == "success":
            color = ACCENT_GREEN
        elif type == "info":
            color = ACCENT_BLUE
        else:
            color = ACCENT_ORANGE
        
        notification_label.config(
            text=message,
            fg=color,
            bg=GLASS_BG
        )
        
        # Slide in from top - simplified animation to avoid potential issues
        notification_label.place(relx=0.5, y=10, anchor="n")
        
        # Schedule hide after a delay
        notification_label.after(3000, lambda: notification_label.place_forget())
            
    except Exception as e:
        print(f"Error showing notification: {e}")

def create_holographic_button(parent, text, command, is_primary=True, width=150, height=40):
    """Create a futuristic holographic button"""
    button_frame = tk.Frame(parent, bg=PANEL_BG, bd=0, highlightthickness=0)
    
    color = ACCENT_ORANGE if is_primary else ACCENT_BLUE
    hover_color = ACCENT_GREEN if is_primary else ACCENT_GREEN
    
    # Create canvas for button with custom drawing
    canvas = tk.Canvas(
        button_frame, 
        width=width, 
        height=height, 
        bg=PANEL_BG,
        highlightthickness=0, 
        bd=0
    )
    canvas.pack()
    
    # Draw initial button state
    button_id = canvas.create_rectangle(2, 2, width-2, height-2, 
                                       fill=PANEL_BG, outline=color, width=2)
    text_id = canvas.create_text(width//2, height//2, text=text,
                                font=(FONT_FAMILY, 10, "bold"), fill=color)
    
    # Create invisible button for events
    invisible_button = tk.Button(
        canvas,
        text="",
        font=(FONT_FAMILY, 10),
        bg=PANEL_BG,
        activebackground=PANEL_BG,
        relief="flat",
        bd=0,
        highlightthickness=0,
        command=command
    )
    
    # Position the invisible button over the canvas
    canvas.create_window(width//2, height//2, window=invisible_button, 
                        width=width-4, height=height-4)
    
    # Hover effects
    def on_enter(e):
        canvas.itemconfig(button_id, outline=hover_color)
        canvas.itemconfig(text_id, fill=hover_color)
        # Add glow effect
        canvas.create_rectangle(4, 4, width-4, height-4, 
                              outline=hover_color, width=1, tags="glow")
        
    def on_leave(e):
        canvas.itemconfig(button_id, outline=color)
        canvas.itemconfig(text_id, fill=color)
        canvas.delete("glow")
        
    def on_press(e):
        # Create pressed effect
        canvas.itemconfig(button_id, outline=ACCENT_GREEN)
        canvas.move(text_id, 1, 1)
        
    def on_release(e):
        # Return to hover state
        canvas.itemconfig(button_id, outline=hover_color)
        canvas.move(text_id, -1, -1)
    
    invisible_button.bind("<Enter>", on_enter)
    invisible_button.bind("<Leave>", on_leave)
    invisible_button.bind("<ButtonPress-1>", on_press)
    invisible_button.bind("<ButtonRelease-1>", on_release)
    
    # Add ARIA properties for accessibility
    invisible_button.config(takefocus=1)
    
    return button_frame

def create_holographic_progress(parent, width=460, height=8):
    """Create a futuristic holographic progress bar"""
    # Create a frame to hold the progress elements
    frame = tk.Frame(parent, bg=DARK_BG, height=height)
    frame.pack(fill="x", pady=(5, 15))
    
    # Create a canvas to draw the progress bar
    canvas = tk.Canvas(
        frame, 
        bg=DARK_BG, 
        height=height, 
        width=width,
        highlightthickness=0, 
        bd=0
    )
    canvas.pack(fill="x")
    
    # Draw track
    track = canvas.create_rectangle(
        0, 0, width, height,
        fill=DARKER_BG, outline=ACCENT_BLUE, width=1
    )
    
    # Draw progress fill
    fill = canvas.create_rectangle(
        0, 0, 0, height,
        fill=ACCENT_BLUE, outline=""
    )
    
    # Function to update progress
    def update_progress(value):
        # value should be between 0 and 100
        fill_width = (value / 100) * width
        canvas.coords(fill, 0, 0, fill_width, height)
        
        # Add glow effect based on progress
        if value > 0:
            glow_color = ACCENT_BLUE
            if value > 75:
                glow_color = ACCENT_GREEN
            canvas.itemconfig(track, outline=glow_color)
    
    # Create a custom progress bar object with update method
    class HolographicProgress:
        def __init__(self):
            self.value = 0
            
        def config(self, **kwargs):
            if 'value' in kwargs:
                self.value = kwargs['value']
                update_progress(self.value)
                
        def __getitem__(self, key):
            if key == 'value':
                return self.value
            return None
    
    return HolographicProgress()

def setup_jarvis_ui(root_window, pause_func, resume_func):
    """Setup the enhanced JARVIS UI components"""
    global root, status_label, animation_canvas, progress_bar, notification_label
    
    root = root_window
    root.title("J.A.R.V.I.S. Screen Recorder")
    root.geometry("550x450")
    root.attributes('-topmost', True)
    root.configure(bg=DARK_BG)
    
    # Set application icon
    try:
        root.iconbitmap('icon.ico')
    except:
        pass
    
    # Main container with glassmorphic effect
    main_frame = tk.Frame(root, bg=DARK_BG, bd=0)
    main_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    # Header with futuristic styling
    header_frame = tk.Frame(main_frame, bg=DARK_BG, height=50)
    header_frame.pack(fill="x", pady=(0, 10))
    
    # JARVIS logo/title with futuristic typography
    title_label = tk.Label(
        header_frame,
        text="J.A.R.V.I.S.",
        font=(FONT_FAMILY, 20, "bold"),
        bg=DARK_BG,
        fg=ACCENT_BLUE
    )
    title_label.pack(side="left", padx=(0, 10))
    
    subtitle_label = tk.Label(
        header_frame,
        text="AUDIO RECORDER",
        font=(FONT_FAMILY, 12),
        bg=DARK_BG,
        fg=TEXT_COLOR_DIM
    )
    subtitle_label.pack(side="left", pady=8)
    
    # Animation area with glassmorphic panel
    animation_frame = tk.Frame(main_frame, bg=PANEL_BG, bd=0, highlightthickness=1, highlightbackground=ACCENT_BLUE)
    animation_frame.pack(fill="both", expand=True, pady=10)
    
    # Create animation canvas with enhanced styling
    animation_canvas = tk.Canvas(
        animation_frame,
        bg=PANEL_BG,
        bd=0,
        highlightthickness=0,
        height=180
    )
    animation_canvas.pack(fill="both", expand=True, padx=3, pady=3)
    
    # Status frame with futuristic style
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
    
    # Custom holographic progress bar
    progress_bar = create_holographic_progress(main_frame)
    
    # Time indicator with futuristic styling
    time_frame = tk.Frame(main_frame, bg=DARK_BG)
    time_frame.pack(fill="x", pady=(0, 10))
    
    time_label = tk.Label(
        time_frame,
        text="00:00",
        font=(FONT_FAMILY, 10),
        bg=DARK_BG,
        fg=TEXT_COLOR_DIM
    )
    time_label.pack(side="right")
    
    # Update time dynamically
    def update_time():
        if status_label and "Recording in progress" in status_label.cget("text"):
            current_time = time_label.cget("text")
            minutes, seconds = map(int, current_time.split(":"))
            seconds += 1
            if seconds >= 60:
                minutes += 1
                seconds = 0
            time_label.config(text=f"{minutes:02d}:{seconds:02d}")
        else:
            time_label.config(text="00:00")
        root.after(1000, update_time)
    
    update_time()
    
    # Buttons frame with holographic styling
    buttons_frame = tk.Frame(main_frame, bg=DARK_BG)
    buttons_frame.pack(pady=15)
    
    # Start/Resume button with enhanced styling
    start_button = create_holographic_button(
        buttons_frame, 
        "START RECORDING", 
        resume_func,
        True
    )
    start_button.pack(side="left", padx=15)
    
    # Stop button with enhanced styling
    stop_button = create_holographic_button(
        buttons_frame, 
        "STOP RECORDING", 
        pause_func,
        False
    )
    stop_button.pack(side="left", padx=15)
    
    # Notification label with glassmorphic effect
    notification_label = tk.Label(
        root,
        text="Recording saved successfully",
        font=(FONT_FAMILY, 10),
        bg=GLASS_BG,
        fg=ACCENT_GREEN,
        padx=15,
        pady=8,
        borderwidth=1,
        relief="solid"
    )
    
    # Add a subtle footer with version info
    footer_frame = tk.Frame(main_frame, bg=DARK_BG)
    footer_frame.pack(fill="x", side="bottom", pady=(15, 0))
    
    footer_label = tk.Label(
        footer_frame,
        text="J.A.R.V.I.S. v2.0",
        font=(FONT_FAMILY, 8),
        bg=DARK_BG,
        fg=TEXT_COLOR_DIM
    )
    footer_label.pack(side="right")
    
    # Start animation
    update_animation("Waiting for sound...")
    
    # Key bindings for accessibility
    root.bind('<space>', lambda e: resume_func())
    root.bind('<Escape>', lambda e: pause_func())
    
    return status_label

def update_status(status_text):
    """Update the status label text with subtle animation"""
    global status_label
    if status_label:
        # Add a subtle fade effect
        current_fg = status_label.cget("fg")
        status_label.config(fg=TEXT_COLOR_DIM)
        status_label.config(text=status_text)
        
        # Fade back to normal color
        def fade_in(alpha=0.0):
            if alpha <= 1.0:
                # Blend colors
                r = int(int(TEXT_COLOR_DIM[1:3], 16) * (1-alpha) + int(TEXT_COLOR[1:3], 16) * alpha)
                g = int(int(TEXT_COLOR_DIM[3:5], 16) * (1-alpha) + int(TEXT_COLOR[3:5], 16) * alpha)
                b = int(int(TEXT_COLOR_DIM[5:7], 16) * (1-alpha) + int(TEXT_COLOR[5:7], 16) * alpha)
                color = f"#{r:02x}{g:02x}{b:02x}"
                status_label.config(fg=color)
                status_label.after(20, lambda: fade_in(alpha + 0.1))
            else:
                status_label.config(fg=TEXT_COLOR)
        
        fade_in()
        update_animation(status_text) 

