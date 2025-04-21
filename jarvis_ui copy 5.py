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
    """Draw a futuristic 3D AI eye with neon elements and metallic textures"""
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
    
    # Size parameters with 3D perspective scaling
    outer_radius = min(width, height) // 3
    inner_radius = outer_radius * 0.85
    core_radius = outer_radius * 0.6
    
    # Enhanced animation parameters
    pulse = math.sin(time.time() * 1.5 + phase) * 0.05 + 0.95
    spin = (time.time() * 0.2 + phase) % (2 * math.pi)
    depth_pulse = math.sin(time.time() * 0.8) * 0.1 + 0.9  # For 3D pulsing effect
    
    # Vibrant neon color palette
    neon_red = "#FF003C"
    neon_blue = "#00FFFF"
    neon_purple = "#9D00FF"
    metallic_dark = "#1A1A2E"
    metallic_medium = "#303050"
    metallic_light = "#5E5E8E"
    
    # Draw metallic base ring (simulated 3D with gradient effect)
    # Multiple concentric circles with decreasing opacity create depth illusion
    for i in range(5):
        depth_factor = 1 - (i * 0.1)
        size_adjust = outer_radius * (1 + i * 0.03)
        # Calculate gradient shades for metallic effect
        gradient_value = int(40 + i * 15)
        gradient_color = f"#{gradient_value:02x}{gradient_value:02x}{gradient_value+20:02x}"
        
        canvas_to_use.create_oval(
            center_x - size_adjust, center_y - size_adjust,
            center_x + size_adjust, center_y + size_adjust,
            fill="", outline=gradient_color, width=2, tags="wave"
        )
    
    # Draw inner metallic plate with 3D bevel effect
    canvas_to_use.create_oval(
        center_x - inner_radius * 1.05, center_y - inner_radius * 1.05,
        center_x + inner_radius * 1.05, center_y + inner_radius * 1.05,
        fill=metallic_dark, outline=metallic_light, width=2, tags="wave"
    )
    
    # Add highlight reflection on top edge for 3D effect
    canvas_to_use.create_arc(
        center_x - inner_radius * 1.04, center_y - inner_radius * 1.04,
        center_x + inner_radius * 1.04, center_y + inner_radius * 1.04,
        start=30, extent=120, style=tk.ARC,
        outline=metallic_light, width=3, tags="wave"
    )
    
    # Add shadow on bottom edge for 3D effect
    canvas_to_use.create_arc(
        center_x - inner_radius * 1.04, center_y - inner_radius * 1.04,
        center_x + inner_radius * 1.04, center_y + inner_radius * 1.04,
        start=210, extent=120, style=tk.ARC,
        outline="#0A0A18", width=3, tags="wave"
    )
    
    # Draw neon glowing core with 3D layers
    # Layer 1 - Base glow
    canvas_to_use.create_oval(
        center_x - core_radius * pulse, center_y - core_radius * pulse,
        center_x + core_radius * pulse, center_y + core_radius * pulse,
        fill=neon_red, outline=neon_purple, width=2, tags="wave"
    )
    
    # Layer 2 - Inner glow with different pulse
    canvas_to_use.create_oval(
        center_x - core_radius * pulse * 0.8, center_y - core_radius * pulse * 0.8,
        center_x + core_radius * pulse * 0.8, center_y + core_radius * pulse * 0.8,
        fill=neon_purple, outline="", tags="wave"
    )
    
    # Layer 3 - Bright center
    canvas_to_use.create_oval(
        center_x - core_radius * pulse * 0.5, center_y - core_radius * pulse * 0.5,
        center_x + core_radius * pulse * 0.5, center_y + core_radius * pulse * 0.5,
        fill="#FFFFFF", outline="", tags="wave"
    )
    
    # Add 3D iris mechanism with rotating elements
    num_iris_segments = 12
    for i in range(num_iris_segments):
        angle = 2 * math.pi * i / num_iris_segments + spin
        # Calculate 3D perspective adjustments
        depth_effect = 0.6 + 0.4 * math.sin(angle + time.time())  # Simulates depth
        
        # Outer point of iris segment
        iris_outer_x = center_x + math.cos(angle) * core_radius * 0.9 * pulse
        iris_outer_y = center_y + math.sin(angle) * core_radius * 0.9 * pulse
        
        # Inner point of iris segment
        iris_inner_x = center_x + math.cos(angle) * core_radius * 0.4 * pulse
        iris_inner_y = center_y + math.sin(angle) * core_radius * 0.4 * pulse
        
        # Draw segmented iris plate with metallic effect
        canvas_to_use.create_line(
            iris_inner_x, iris_inner_y, iris_outer_x, iris_outer_y,
            fill=metallic_light if i % 2 == 0 else neon_blue, 
            width=3 * depth_effect, tags="wave"
        )
        
        # Add highlight dots at the end of each segment
        if i % 3 == 0:
            canvas_to_use.create_oval(
                iris_outer_x - 3, iris_outer_y - 3,
                iris_outer_x + 3, iris_outer_y + 3,
                fill=neon_blue, outline="", tags="wave"
            )
    
    # Add rotating scanning element with 3D movement
    for i in range(3):
        # Calculate 3D rotation position
        scan_angle = spin + (2 * math.pi / 3) * i
        scan_radius = core_radius * 0.9 * (0.9 + 0.1 * math.sin(time.time() * 2 + i))  # Varying radius for 3D effect
        scan_x = center_x + math.cos(scan_angle) * scan_radius
        scan_y = center_y + math.sin(scan_angle) * scan_radius
        
        # Draw scanning beam - thicker in middle for 3D effect
        points = [
            center_x, center_y,
            center_x + (scan_x - center_x) * 0.3, center_y + (scan_y - center_y) * 0.3,
            center_x + (scan_x - center_x) * 0.7, center_y + (scan_y - center_y) * 0.7,
            scan_x, scan_y
        ]
        canvas_to_use.create_line(
            points, fill="#FFFFFF", width=2, smooth=True, tags="wave"
        )
        
        # Draw glowing dot at end of beam
        scan_dot_size = outer_radius * 0.04 * (1 + 0.3 * math.sin(time.time() * 5 + i))
        canvas_to_use.create_oval(
            scan_x - scan_dot_size, scan_y - scan_dot_size,
            scan_x + scan_dot_size, scan_y + scan_dot_size,
            fill=neon_blue, outline="#FFFFFF", width=1, tags="wave"
        )
        
        # Add secondary pulsing glow for enhanced effect
        canvas_to_use.create_oval(
            scan_x - scan_dot_size*1.5, scan_y - scan_dot_size*1.5,
            scan_x + scan_dot_size*1.5, scan_y + scan_dot_size*1.5,
            fill="", outline=neon_blue, width=1, tags="wave"
        )
    
    # Add tech details around outer ring - metallic segments with 3D bevels
    num_segments = 8
    for i in range(num_segments):
        segment_angle = 2 * math.pi * i / num_segments
        segment_x = center_x + math.cos(segment_angle) * (outer_radius + outer_radius * 0.1)
        segment_y = center_y + math.sin(segment_angle) * (outer_radius + outer_radius * 0.1)
        
        # Segment size with 3D perspective (closer segments appear larger)
        perspective = 0.7 + 0.3 * math.sin(segment_angle + spin)  # Simulates perspective
        segment_width = outer_radius * 0.18 * perspective
        segment_height = outer_radius * 0.1 * perspective
        
        # Draw 3D metallic segment with bevel effect
        canvas_to_use.create_rectangle(
            segment_x - segment_width, segment_y - segment_height,
            segment_x + segment_width, segment_y + segment_height,
            fill=metallic_medium, outline=metallic_light, width=1, tags="wave"
        )
        
        # Add highlight and shadow for 3D effect
        if math.cos(segment_angle) > 0:  # Right side segments get highlight
            canvas_to_use.create_line(
                segment_x - segment_width, segment_y - segment_height,
                segment_x + segment_width, segment_y - segment_height,
                fill=metallic_light, width=2, tags="wave"
            )
        else:  # Left side segments get shadow
            canvas_to_use.create_line(
                segment_x - segment_width, segment_y + segment_height,
                segment_x + segment_width, segment_y + segment_height,
                fill="#0A0A18", width=2, tags="wave"
            )
        
        # Add tech detail in the center of each segment
        if i % 2 == 0:
            canvas_to_use.create_rectangle(
                segment_x - segment_width * 0.5, segment_y - segment_height * 0.3,
                segment_x + segment_width * 0.5, segment_y + segment_height * 0.3,
                fill=neon_purple if i % 4 == 0 else neon_blue, outline="", tags="wave"
            )
    
    # Add dynamic energy arcs for enhanced tech feel
    for i in range(6):
        arc_start = (spin * 57.3 + i * 60) % 360  # Convert radians to degrees
        arc_extent = 20 + 10 * math.sin(time.time() * 3 + i)
        arc_radius = outer_radius * 0.6 * (0.9 + 0.1 * math.sin(time.time() + i))
        
        canvas_to_use.create_arc(
            center_x - arc_radius, center_y - arc_radius,
            center_x + arc_radius, center_y + arc_radius,
            start=arc_start, extent=arc_extent,
            style=tk.ARC, outline=neon_purple if i % 2 == 0 else neon_blue, 
            width=2, tags="wave"
        )
    
    # Add holographic scan lines for tech effect
    for i in range(12):
        line_y = center_y - core_radius + (2 * core_radius * i / 12)
        line_alpha = int(127 + 127 * math.sin(line_y / 10 + time.time() * 2))
        line_color = neon_blue
        
        # Only draw visible lines
        if line_alpha > 30:
            canvas_to_use.create_line(
                center_x - core_radius * 0.9, line_y,
                center_x + core_radius * 0.9, line_y,
                fill=line_color, width=1, tags="wave"
            )
    
    # Add center bright core with lens flare for realistic light effect
    core_size = core_radius * 0.25 * pulse
    canvas_to_use.create_oval(
        center_x - core_size, center_y - core_size,
        center_x + core_size, center_y + core_size,
        fill="#FFFFFF", outline=neon_red, width=1, tags="wave"
    )
    
    # Add diagonal light flares
    flare_size = core_size * 1.2
    for angle in [0, 45, 90, 135]:
        # Convert angle to radians
        rad_angle = math.radians(angle)
        # Calculate endpoints
        x1 = center_x + math.cos(rad_angle) * flare_size * 2
        y1 = center_y + math.sin(rad_angle) * flare_size * 2
        x2 = center_x - math.cos(rad_angle) * flare_size * 2
        y2 = center_y - math.sin(rad_angle) * flare_size * 2
        
        # Draw flare line with gradient effect
        canvas_to_use.create_line(
            x1, y1, x2, y2,
            fill="#FFFFFF", width=1, tags="wave"
        )

def draw_recording_animation(canvas, width, height, phase=0):
    """Draw futuristic 3D recording animation with holographic and neon elements"""
    canvas.delete("recording")
    
    # Center coordinates
    center_x = width // 2
    center_y = height // 2
    
    # Size parameters with 3D perspective
    outer_radius = min(width, height) // 3
    inner_radius = outer_radius * 0.7
    
    # Enhanced animation parameters
    pulse = math.sin(time.time() * 2) * 0.1 + 0.9
    rotation = (time.time() * 0.5 + phase) % (2 * math.pi)
    depth_oscillation = math.sin(time.time() * 0.7) * 0.15 + 0.85  # For 3D depth effect
    
    # Vibrant neon color palette
    neon_cyan = "#00FFFF"
    neon_magenta = "#FF00FF"
    neon_blue = "#3366FF"
    neon_orange = "#FF6600"
    neon_green = "#33FF99"
    metallic_dark = "#1A1A2E"
    metallic_light = "#5E5E8E"
    
    # Draw 3D layered base plate - multiple ovals create depth illusion
    for i in range(3):
        depth_factor = 1 - (i * 0.05)
        canvas.create_oval(
            center_x - outer_radius * 1.1 * depth_factor, 
            center_y - outer_radius * 1.1 * depth_factor,
            center_x + outer_radius * 1.1 * depth_factor, 
            center_y + outer_radius * 1.1 * depth_factor,
            fill="", outline=f"#{30+i*10:02x}{30+i*10:02x}{50+i*10:02x}", 
            width=2, tags="recording"
        )
    
    # Draw outer hexagonal frame with 3D perspective effect
    hex_points = []
    for i in range(6):
        angle = math.pi/6 + i * math.pi/3 + rotation * 0.1
        # Add perspective by varying the radius based on position
        perspective = 1.0 + 0.1 * math.sin(angle + rotation)
        hex_x = center_x + math.cos(angle) * outer_radius * 1.1 * perspective
        hex_y = center_y + math.sin(angle) * outer_radius * 1.1 * perspective
        hex_points.extend([hex_x, hex_y])
    
    # Draw hexagon with gradient-like effect for 3D
    canvas.create_polygon(
        hex_points, 
        fill="", 
        outline=neon_blue, 
        width=3, 
        tags="recording"
    )
    
    # Add metallic inner ring with 3D bevels
    canvas.create_oval(
        center_x - inner_radius * 1.05, center_y - inner_radius * 1.05,
        center_x + inner_radius * 1.05, center_y + inner_radius * 1.05,
        fill=metallic_dark, outline=metallic_light, width=2, tags="recording"
    )
    
    # Add highlight reflection on top edge for 3D effect
    canvas.create_arc(
        center_x - inner_radius * 1.04, center_y - inner_radius * 1.04,
        center_x + inner_radius * 1.04, center_y + inner_radius * 1.04,
        start=30, extent=120, style=tk.ARC,
        outline=metallic_light, width=3, tags="recording"
    )
    
    # Add inner hexagonal frame with 3D dynamic rotation
    inner_hex_points = []
    for i in range(6):
        angle = math.pi/6 + i * math.pi/3 - rotation * 0.2
        # Inner hex has different perspective than outer
        perspective = 1.0 + 0.08 * math.cos(angle - rotation * 1.5)
        hex_x = center_x + math.cos(angle) * outer_radius * 0.8 * perspective
        hex_y = center_y + math.sin(angle) * outer_radius * 0.8 * perspective
        inner_hex_points.extend([hex_x, hex_y])
    
    canvas.create_polygon(
        inner_hex_points, 
        fill="", 
        outline=neon_orange, 
        width=2, 
        tags="recording"
    )
    
    # Draw circular progress indicator with 3D metallic track
    # Base metallic track with 3D bevel effect
    canvas.create_arc(
        center_x - inner_radius, center_y - inner_radius,
        center_x + inner_radius, center_y + inner_radius,
        start=0, extent=360,
        outline="#404050", width=4, style=tk.ARC, tags="recording"
    )
    
    # Add highlight on top of track for 3D effect
    canvas.create_arc(
        center_x - inner_radius, center_y - inner_radius,
        center_x + inner_radius, center_y + inner_radius,
        start=30, extent=120, style=tk.ARC,
        outline="#606070", width=3, tags="recording"
    )
    
    # Progress arc with neon glow effect
    start_angle = 90
    extent = -phase * 360
    
    # Main progress arc - thicker for prominence
    canvas.create_arc(
        center_x - inner_radius, center_y - inner_radius,
        center_x + inner_radius, center_y + inner_radius,
        start=start_angle, extent=extent,
        outline=neon_cyan, width=5,
        style=tk.ARC, tags="recording"
    )
    
    # Outer glow effect for progress arc
    canvas.create_arc(
        center_x - inner_radius * 1.02, center_y - inner_radius * 1.02,
        center_x + inner_radius * 1.02, center_y + inner_radius * 1.02,
        start=start_angle, extent=extent,
        outline=neon_cyan, width=2,
        style=tk.ARC, tags="recording"
    )
    
    # Draw holographic orbit circles with 3D movement
    for i in range(4):
        # Each orbit has different phase and oscillation
        orbit_phase = rotation + i * (2 * math.pi / 4)
        orbit_oscillation = 0.2 * math.sin(time.time() * (1 + i * 0.5) + i)
        orbit_radius = inner_radius * (0.4 + i * 0.15)
        
        # Calculate 3D position with perspective oscillation
        orbit_x = center_x + math.cos(orbit_phase) * orbit_radius * (1 + orbit_oscillation)
        orbit_y = center_y + math.sin(orbit_phase) * orbit_radius * (1 + orbit_oscillation)
        
        # Size varies with perspective
        perspective_factor = 1 + 0.3 * math.sin(orbit_phase + rotation)
        orbit_size = outer_radius * 0.08 * pulse * perspective_factor
        
        # Draw the orbiting element with metallic gradient
        # Main orbit body
        canvas.create_oval(
            orbit_x - orbit_size, orbit_y - orbit_size,
            orbit_x + orbit_size, orbit_y + orbit_size,
            fill=neon_magenta if i % 2 == 0 else neon_green, 
            outline="#FFFFFF", width=1, tags="recording"
        )
        
        # Add outer glow for depth
        canvas.create_oval(
            orbit_x - orbit_size * 1.3, orbit_y - orbit_size * 1.3,
            orbit_x + orbit_size * 1.3, orbit_y + orbit_size * 1.3,
            fill="", outline=neon_magenta if i % 2 == 0 else neon_green, 
            width=1, tags="recording"
        )
        
        # Draw connecting beam to center with light intensity varying by distance
        # Multiple segments create 3D tube effect
        for j in range(3):
            segment_factor = j / 3
            x1 = center_x + (orbit_x - center_x) * segment_factor
            y1 = center_y + (orbit_y - center_y) * segment_factor
            x2 = center_x + (orbit_x - center_x) * (segment_factor + 0.3)
            y2 = center_y + (orbit_y - center_y) * (segment_factor + 0.3)
            
            width = 2 - segment_factor  # Thicker near center
            color = neon_orange if i % 2 == 0 else neon_cyan
            canvas.create_line(
                x1, y1, x2, y2,
                fill=color, width=width, tags="recording"
            )
    
    # Draw central recording indicator with 3D layers
    # Base pulsing circle
    inner_size = inner_radius * 0.25 * pulse
    canvas.create_oval(
        center_x - inner_size, center_y - inner_size,
        center_x + inner_size, center_y + inner_size,
        fill="#800000", outline=neon_orange, width=2, tags="recording"
    )
    
    # Middle layer with different pulse rate
    mid_pulse = math.sin(time.time() * 3) * 0.1 + 0.9
    canvas.create_oval(
        center_x - inner_size * 0.8 * mid_pulse, center_y - inner_size * 0.8 * mid_pulse,
        center_x + inner_size * 0.8 * mid_pulse, center_y + inner_size * 0.8 * mid_pulse,
        fill="#FF2000", outline=neon_magenta, width=1, tags="recording"
    )
    
    # Core with brightest color
    core_pulse = math.sin(time.time() * 4) * 0.2 + 0.8
    canvas.create_oval(
        center_x - inner_size * 0.5 * core_pulse, center_y - inner_size * 0.5 * core_pulse,
        center_x + inner_size * 0.5 * core_pulse, center_y + inner_size * 0.5 * core_pulse,
        fill="#FFFFFF", outline="", tags="recording"
    )
    
    # Add 3D tech details - digital particles with depth simulation
    for i in range(12):
        particle_angle = 2 * math.pi * i / 12 + rotation
        # Particles move in and out from center
        particle_distance = inner_radius * (0.5 + 0.1 * math.sin(time.time() * 3 + i))
        particle_x = center_x + math.cos(particle_angle) * particle_distance
        particle_y = center_y + math.sin(particle_angle) * particle_distance
        
        # Particle size varies with perspective and time
        perspective = 0.7 + 0.3 * math.cos(particle_angle + rotation * 2)
        particle_size = outer_radius * 0.025 * (1 + math.sin(time.time() * 5 + i) * 0.5) * perspective
        
        # Alternate between different shapes and colors for variety
        if i % 3 == 0:
            # Squares for tech feel
            canvas.create_rectangle(
                particle_x - particle_size, particle_y - particle_size,
                particle_x + particle_size, particle_y + particle_size,
                fill=neon_blue, outline="", tags="recording"
            )
        elif i % 3 == 1:
            # Circles for organic feel
            canvas.create_oval(
                particle_x - particle_size, particle_y - particle_size,
                particle_x + particle_size, particle_y + particle_size,
                fill=neon_cyan, outline="", tags="recording"
            )
        else:
            # Diamonds for edge
            points = [
                particle_x, particle_y - particle_size * 1.2,
                particle_x + particle_size, particle_y,
                particle_x, particle_y + particle_size * 1.2,
                particle_x - particle_size, particle_y,
            ]
            canvas.create_polygon(
                points, fill=neon_magenta, outline="", tags="recording"
            )
    
    # Add dynamic energy rings pulsing outward for holographic effect
    num_rings = 3
    for i in range(num_rings):
        # Ring expands with time and resets
        ring_phase = ((time.time() * 0.5) % 1 + i/num_rings) % 1
        ring_radius = inner_radius * 0.2 + ring_phase * inner_radius * 0.7
        ring_opacity = int(255 * (1 - ring_phase))  # Fade as it expands
        
        if ring_opacity > 30:  # Only draw visible rings
            ring_color = neon_cyan if i % 2 == 0 else neon_magenta
            canvas.create_oval(
                center_x - ring_radius, center_y - ring_radius,
                center_x + ring_radius, center_y + ring_radius,
                fill="", outline=ring_color, width=2, tags="recording"
            )
    
    # Add horizontal and vertical scan lines for tech effect
    # Digital holographic scan lines
    num_scan_lines = 10
    for i in range(num_scan_lines):
        # Horizontal scan lines - moving down
        y_pos = center_y - inner_radius + inner_radius * 2 * ((time.time() * 0.3 + i/num_scan_lines) % 1)
        # Opacity varies with sine wave
        opacity = int(150 * math.sin(y_pos / 10 + time.time() * 3) ** 2)
        
        if opacity > 30:  # Only draw visible lines
            line_width = 1 + int(opacity / 75)
            canvas.create_line(
                center_x - inner_radius, y_pos,
                center_x + inner_radius, y_pos,
                fill=neon_blue, width=line_width, tags="recording"
            )
            
        # Vertical scan lines - moving right
        x_pos = center_x - inner_radius + inner_radius * 2 * ((time.time() * 0.2 + (i+5)/num_scan_lines) % 1)
        opacity = int(150 * math.cos(x_pos / 10 + time.time() * 2) ** 2)
        
        if opacity > 30:  # Only draw visible lines
            line_width = 1 + int(opacity / 75)
            canvas.create_line(
                x_pos, center_y - inner_radius * 0.7,
                x_pos, center_y + inner_radius * 0.7,
                fill=neon_green, width=line_width, tags="recording"
            )
    
    # Add tech corner brackets for framing
    bracket_size = outer_radius * 0.2
    for i in range(4):
        angle = i * math.pi/2  # 0, 90, 180, 270 degrees
        # Corner positions with slight perspective effect
        perspective = 1 + 0.05 * math.sin(time.time() + i)
        corner_x = center_x + math.cos(angle) * outer_radius * 1.2 * perspective
        corner_y = center_y + math.sin(angle) * outer_radius * 1.2 * perspective
        
        # Each corner has two lines making an L shape
        # First line
        line1_end_x = corner_x - math.cos(angle) * bracket_size
        line1_end_y = corner_y - math.sin(angle) * bracket_size
        # Second line
        line2_end_x = corner_x - math.cos(angle + math.pi/2) * bracket_size
        line2_end_y = corner_y - math.sin(angle + math.pi/2) * bracket_size
        
        # Draw the bracket lines
        canvas.create_line(
            corner_x, corner_y, line1_end_x, line1_end_y,
            fill=neon_orange, width=2, tags="recording"
        )
        canvas.create_line(
            corner_x, corner_y, line2_end_x, line2_end_y,
            fill=neon_orange, width=2, tags="recording"
        )

def draw_complete_animation(canvas, width, height):
    """Draw futuristic 3D completion animation with holographic elements and metallics"""
    canvas.delete("complete")
    
    # Center coordinates
    center_x = width // 2
    center_y = height // 2
    
    # Size parameters with 3D perspective
    outer_radius = min(width, height) // 3
    inner_radius = outer_radius * 0.85
    
    # Enhanced animation parameters
    current_time = time.time()
    pulse = math.sin(current_time * 2) * 0.1 + 0.9
    fast_pulse = math.sin(current_time * 5) * 0.5 + 0.5
    rotation = current_time * 0.3 % (2 * math.pi)
    
    # Vibrant neon color palette
    neon_green = "#00FF66"
    neon_cyan = "#00FFFF"
    neon_blue = "#3366FF"
    neon_yellow = "#FFFF00"
    metallic_dark_green = "#0A3320"
    metallic_medium_green = "#0E6245"
    metallic_light_green = "#18A67C"
    
    # Draw 3D base plate with metallic gradient
    for i in range(4):
        depth_factor = 1 - (i * 0.05)
        gradient_value = int(10 + i * 15)
        gradient_color = f"#{gradient_value:02x}{gradient_value+25:02x}{gradient_value:02x}"
        
        canvas.create_oval(
            center_x - outer_radius * 1.15 * depth_factor, 
            center_y - outer_radius * 1.15 * depth_factor,
            center_x + outer_radius * 1.15 * depth_factor, 
            center_y + outer_radius * 1.15 * depth_factor,
            fill="", 
            outline=gradient_color, 
            width=2, 
            tags="complete"
        )
    
    # Draw outer hexagonal frame with 3D perspective
    hex_points = []
    for i in range(6):
        angle = math.pi/6 + i * math.pi/3 + current_time * 0.1
        # Add 3D perspective by varying radius
        perspective = 1.0 + 0.08 * math.sin(angle + rotation)
        hex_x = center_x + math.cos(angle) * outer_radius * 1.1 * perspective
        hex_y = center_y + math.sin(angle) * outer_radius * 1.1 * perspective
        hex_points.extend([hex_x, hex_y])
    
    canvas.create_polygon(
        hex_points, 
        fill="", 
        outline=neon_green, 
        width=3, 
        tags="complete"
    )
    
    # Draw inner rotating hexagonal frame
    inner_hex_points = []
    for i in range(6):
        angle = math.pi/6 + i * math.pi/3 - current_time * 0.2
        # Different perspective for inner hex
        perspective = 1.0 + 0.05 * math.cos(angle - rotation * 1.2)
        hex_x = center_x + math.cos(angle) * outer_radius * 0.7 * perspective
        hex_y = center_y + math.sin(angle) * outer_radius * 0.7 * perspective
        inner_hex_points.extend([hex_x, hex_y])
    
    canvas.create_polygon(
        inner_hex_points, 
        fill="", 
        outline=neon_cyan, 
        width=2, 
        tags="complete"
    )
    
    # Draw 3D layered success circle with metallic shading
    # Base layer - dark metallic green
    canvas.create_oval(
        center_x - inner_radius * pulse, center_y - inner_radius * pulse,
        center_x + inner_radius * pulse, center_y + inner_radius * pulse,
        fill=metallic_dark_green, outline=metallic_light_green, width=3,
        tags="complete"
    )
    
    # Add highlight reflection on top edge for 3D effect
    canvas.create_arc(
        center_x - inner_radius * pulse, center_y - inner_radius * pulse,
        center_x + inner_radius * pulse, center_y + inner_radius * pulse,
        start=30, extent=120, style=tk.ARC,
        outline=neon_green, width=3, tags="complete"
    )
    
    # Add shadow on bottom edge for 3D effect
    canvas.create_arc(
        center_x - inner_radius * pulse, center_y - inner_radius * pulse,
        center_x + inner_radius * pulse, center_y + inner_radius * pulse,
        start=210, extent=120, style=tk.ARC,
        outline="#051A10", width=3, tags="complete"
    )
    
    # Draw middle layer with different pulse rate
    inner_pulse = math.sin(current_time * 3) * 0.1 + 0.9
    canvas.create_oval(
        center_x - inner_radius * 0.7 * inner_pulse, center_y - inner_radius * 0.7 * inner_pulse,
        center_x + inner_radius * 0.7 * inner_pulse, center_y + inner_radius * 0.7 * inner_pulse,
        fill=metallic_medium_green, outline=neon_green, width=2,
        tags="complete"
    )
    
    # Add tech details - circular segments with 3D bevels
    for i in range(8):
        start_angle = i * 45 + rotation * 10
        extent = 30
        radius = inner_radius * 0.8
        
        # Main segment
        canvas.create_arc(
            center_x - radius, center_y - radius,
            center_x + radius, center_y + radius,
            start=start_angle, extent=extent,
            style=tk.ARC, outline=neon_green if i % 2 == 0 else neon_cyan, 
            width=3 if i % 2 == 0 else 2,
            tags="complete"
        )
        
        # Add segment end caps for 3D tech feel
        if i % 2 == 0:
            # Convert angles to radians
            start_rad = math.radians(start_angle)
            end_rad = math.radians(start_angle + extent)
            
            # Calculate start and end points of the arc
            start_x = center_x + math.cos(start_rad) * radius
            start_y = center_y - math.sin(start_rad) * radius
            end_x = center_x + math.cos(end_rad) * radius
            end_y = center_y - math.sin(end_rad) * radius
            
            # Draw end caps as small rectangles
            cap_size = 3
            for point_x, point_y in [(start_x, start_y), (end_x, end_y)]:
                canvas.create_rectangle(
                    point_x - cap_size, point_y - cap_size,
                    point_x + cap_size, point_y + cap_size,
                    fill=neon_green, outline="", tags="complete"
                )
    
    # Draw central completion area with 3D check mark
    # Base circle for the check mark background
    check_bg_size = inner_radius * 0.45
    canvas.create_oval(
        center_x - check_bg_size, center_y - check_bg_size,
        center_x + check_bg_size, center_y + check_bg_size,
        fill=metallic_medium_green, outline=neon_green, width=2, tags="complete"
    )
    
    # 3D check mark using Bezier curve with dynamic thickness
    # Main diagonal line - thicker in middle
    check_size = inner_radius * 0.6
    
    # Create points for smooth check mark
    check_points = [
        center_x - check_size * 0.5, center_y,
        center_x - check_size * 0.25, center_y + check_size * 0.4,
        center_x - check_size * 0.1, center_y + check_size * 0.5,
        center_x + check_size * 0.1, center_y + check_size * 0.3,
        center_x + check_size * 0.3, center_y - check_size * 0.1,
        center_x + check_size * 0.6, center_y - check_size * 0.4,
    ]
    
    # Draw check mark with glow
    canvas.create_line(
        check_points,
        fill="#FFFFFF", width=5, smooth=True, tags="complete"
    )
    
    # Draw check mark outline for 3D effect
    canvas.create_line(
        check_points,
        fill=neon_green, width=7, smooth=True, tags="complete"
    )
    
    # Draw over with white for main part
    canvas.create_line(
        check_points,
        fill="#FFFFFF", width=4, smooth=True, tags="complete"
    )
    
    # Add tech details - digital particles with 3D depth and motion
    for i in range(16):
        particle_angle = 2 * math.pi * i / 16 + current_time * 0.2
        # Particles orbit at varying distances and speeds
        orbit_variation = math.sin(current_time * (1 + i * 0.1) + i)
        particle_distance = inner_radius * (0.5 + fast_pulse * 0.2 + orbit_variation * 0.1)
        
        # Calculate 3D position with perspective
        perspective = 0.7 + 0.3 * math.sin(particle_angle * 2 + current_time)
        particle_x = center_x + math.cos(particle_angle) * particle_distance * perspective
        particle_y = center_y + math.sin(particle_angle) * particle_distance * perspective
        
        # Particle size varies with perspective and time
        particle_size = outer_radius * 0.03 * (1 + math.sin(current_time * 3 + i) * 0.3) * perspective
        
        # Alternate between different shapes and colors for variety
        if i % 3 == 0:
            # Squares for tech feel - success indicator
            canvas.create_rectangle(
                particle_x - particle_size, particle_y - particle_size,
                particle_x + particle_size, particle_y + particle_size,
                fill=neon_green, outline="", tags="complete"
            )
        elif i % 3 == 1:
            # Circles for organic feel
            canvas.create_oval(
                particle_x - particle_size, particle_y - particle_size,
                particle_x + particle_size, particle_y + particle_size,
                fill=neon_cyan, outline="", tags="complete"
            )
        else:
            # Diamonds for edge and tech feel
            diamond_points = [
                particle_x, particle_y - particle_size * 1.2,
                particle_x + particle_size, particle_y,
                particle_x, particle_y + particle_size * 1.2,
                particle_x - particle_size, particle_y,
            ]
            canvas.create_polygon(
                diamond_points, fill=neon_yellow, outline="", tags="complete"
            )
    
    # Add central glow with 3D layers
    # Base glow
    glow_size = check_size * 0.3 * pulse
    canvas.create_oval(
        center_x - glow_size, center_y - glow_size,
        center_x + glow_size, center_y + glow_size,
        fill="#FFFFFF", outline=neon_green, width=2, tags="complete"
    )
    
    # Add outer glow ring
    canvas.create_oval(
        center_x - glow_size * 1.3, center_y - glow_size * 1.3,
        center_x + glow_size * 1.3, center_y + glow_size * 1.3,
        fill="", outline=neon_green, width=1, tags="complete"
    )
    
    # Add dynamic energy rings pulsing outward
    num_rings = 3
    for i in range(num_rings):
        # Ring expands with time and resets
        ring_phase = ((current_time * 0.5) % 1 + i/num_rings) % 1
        ring_radius = inner_radius * 0.2 + ring_phase * inner_radius * 0.6
        ring_opacity = int(255 * (1 - ring_phase))  # Fade as it expands
        
        if ring_opacity > 30:  # Only draw visible rings
            ring_color = neon_green if i % 2 == 0 else neon_cyan
            canvas.create_oval(
                center_x - ring_radius, center_y - ring_radius,
                center_x + ring_radius, center_y + ring_radius,
                fill="", outline=ring_color, width=2, tags="complete"
            )
    
    # Add digital scan lines with 3D motion effect
    # Horizontal scan lines with varying opacity to simulate hologram
    num_scan_lines = 8
    for i in range(num_scan_lines):
        # Horizontal scan lines - moving down
        y_pos = center_y - inner_radius + inner_radius * 2 * ((current_time * 0.3 + i/num_scan_lines) % 1)
        # Opacity varies with sine wave and position
        opacity = int(200 * math.sin(y_pos / 10 + current_time * 2) ** 2)
        
        if opacity > 30:  # Only draw visible lines
            line_width = 1 + int(opacity / 100)
            # Add perspective by varying the line width and length
            perspective = 0.7 + 0.3 * math.sin(y_pos / 10 + current_time)
            canvas.create_line(
                center_x - inner_radius * perspective, y_pos,
                center_x + inner_radius * perspective, y_pos,
                fill=neon_green, width=line_width, tags="complete"
            )
    
    # Add tech corner brackets for framing
    bracket_size = outer_radius * 0.2
    for i in range(4):
        angle = i * math.pi/2  # 0, 90, 180, 270 degrees
        # Corner positions with perspective effect
        perspective = 1 + 0.05 * math.sin(current_time + i)
        corner_x = center_x + math.cos(angle) * outer_radius * 1.2 * perspective
        corner_y = center_y + math.sin(angle) * outer_radius * 1.2 * perspective
        
        # Each corner has two lines making an L shape
        # First line
        line1_end_x = corner_x - math.cos(angle) * bracket_size
        line1_end_y = corner_y - math.sin(angle) * bracket_size
        # Second line
        line2_end_x = corner_x - math.cos(angle + math.pi/2) * bracket_size
        line2_end_y = corner_y - math.sin(angle + math.pi/2) * bracket_size
        
        # Draw the bracket lines
        canvas.create_line(
            corner_x, corner_y, line1_end_x, line1_end_y,
            fill=neon_cyan, width=2, tags="complete"
        )
        canvas.create_line(
            corner_x, corner_y, line2_end_x, line2_end_y,
            fill=neon_cyan, width=2, tags="complete"
        )
        
        # Add tech dot at corner
        canvas.create_oval(
            corner_x - 3, corner_y - 3,
            corner_x + 3, corner_y + 3,
            fill=neon_yellow, outline="", tags="complete"
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
    # notification_label = tk.Label(
    #     root,
    #     text="Recording saved successfully",
    #     font=(FONT_FAMILY, 10),
    #     bg=PANEL_BG,
    #     fg=TEXT_COLOR,
    #     padx=10,
    #     pady=5
    # )
    
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