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
    current_time = time.time()
    pulse = math.sin(current_time * 1.5 + phase) * 0.05 + 0.95
    spin = (current_time * 0.2 + phase) % (2 * math.pi)
    depth_pulse = math.sin(current_time * 0.8) * 0.1 + 0.9  # For 3D pulsing effect
    
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
        size_adjust = outer_radius * (1 + i * 0.03) * depth_pulse # Added depth pulse
        # Calculate gradient shades for metallic effect
        gradient_value = int(40 + i * 15)
        gradient_color = f"#{gradient_value:02x}{gradient_value:02x}{gradient_value+20:02x}"
        
        canvas_to_use.create_oval(
            center_x - size_adjust, center_y - size_adjust,
            center_x + size_adjust, center_y + size_adjust,
            fill="", outline=gradient_color, width=2, tags="wave"
        )
    
    # Draw inner metallic plate with 3D bevel effect
    inner_radius_3d = inner_radius * depth_pulse # Apply depth pulse
    canvas_to_use.create_oval(
        center_x - inner_radius_3d * 1.05, center_y - inner_radius_3d * 1.05,
        center_x + inner_radius_3d * 1.05, center_y + inner_radius_3d * 1.05,
        fill=metallic_dark, outline=metallic_light, width=2, tags="wave"
    )
    
    # Add highlight reflection on top edge for 3D effect
    canvas_to_use.create_arc(
        center_x - inner_radius_3d * 1.04, center_y - inner_radius_3d * 1.04,
        center_x + inner_radius_3d * 1.04, center_y + inner_radius_3d * 1.04,
        start=30, extent=120, style=tk.ARC,
        outline=metallic_light, width=3, tags="wave"
    )
    
    # Add shadow on bottom edge for 3D effect
    canvas_to_use.create_arc(
        center_x - inner_radius_3d * 1.04, center_y - inner_radius_3d * 1.04,
        center_x + inner_radius_3d * 1.04, center_y + inner_radius_3d * 1.04,
        start=210, extent=120, style=tk.ARC,
        outline="#0A0A18", width=3, tags="wave"
    )
    
    # Draw neon glowing core with 3D layers
    core_radius_3d = core_radius * depth_pulse # Apply depth pulse
    # Layer 1 - Base glow
    canvas_to_use.create_oval(
        center_x - core_radius_3d * pulse, center_y - core_radius_3d * pulse,
        center_x + core_radius_3d * pulse, center_y + core_radius_3d * pulse,
        fill=neon_red, outline=neon_purple, width=2, tags="wave"
    )
    
    # Layer 2 - Inner glow with different pulse
    canvas_to_use.create_oval(
        center_x - core_radius_3d * pulse * 0.8, center_y - core_radius_3d * pulse * 0.8,
        center_x + core_radius_3d * pulse * 0.8, center_y + core_radius_3d * pulse * 0.8,
        fill=neon_purple, outline="", tags="wave"
    )
    
    # Layer 3 - Bright center
    canvas_to_use.create_oval(
        center_x - core_radius_3d * pulse * 0.5, center_y - core_radius_3d * pulse * 0.5,
        center_x + core_radius_3d * pulse * 0.5, center_y + core_radius_3d * pulse * 0.5,
        fill="#FFFFFF", outline="", tags="wave"
    )
    
    # Add 3D iris mechanism with rotating elements
    num_iris_segments = 12
    for i in range(num_iris_segments):
        angle = 2 * math.pi * i / num_iris_segments + spin
        # Calculate 3D perspective adjustments
        depth_effect = 0.6 + 0.4 * math.sin(angle + current_time)  # Simulates depth and rotation effect
        
        # Outer point of iris segment with perspective
        iris_outer_x = center_x + math.cos(angle) * core_radius_3d * 0.9 * pulse * depth_effect
        iris_outer_y = center_y + math.sin(angle) * core_radius_3d * 0.9 * pulse * depth_effect
        
        # Inner point of iris segment with perspective
        iris_inner_x = center_x + math.cos(angle) * core_radius_3d * 0.4 * pulse * depth_effect
        iris_inner_y = center_y + math.sin(angle) * core_radius_3d * 0.4 * pulse * depth_effect
        
        # Draw segmented iris plate with metallic effect and perspective width
        canvas_to_use.create_line(
            iris_inner_x, iris_inner_y, iris_outer_x, iris_outer_y,
            fill=metallic_light if i % 2 == 0 else neon_blue,
            width=max(1, 3 * depth_effect * pulse), tags="wave" # Ensure width is at least 1
        )
        
        # Add highlight dots at the end of each segment with perspective scaling
        if i % 3 == 0:
            dot_size = max(1, 3 * depth_effect) # Ensure size is at least 1
            canvas_to_use.create_oval(
                iris_outer_x - dot_size, iris_outer_y - dot_size,
                iris_outer_x + dot_size, iris_outer_y + dot_size,
                fill=neon_blue, outline="", tags="wave"
            )
    
    # Add rotating scanning element with 3D movement
    for i in range(3):
        # Calculate 3D rotation position
        scan_angle = spin + (2 * math.pi / 3) * i
        scan_radius_base = core_radius_3d * 0.9
        # Varying radius and perspective for 3D effect
        scan_radius_oscillation = 0.9 + 0.1 * math.sin(current_time * 2 + i)
        perspective_factor = 1 + 0.2 * math.sin(scan_angle + current_time * 0.5)
        scan_radius = scan_radius_base * scan_radius_oscillation * perspective_factor

        scan_x = center_x + math.cos(scan_angle) * scan_radius
        scan_y = center_y + math.sin(scan_angle) * scan_radius

        # Draw scanning beam - thicker in middle for 3D effect using polygon
        thickness_factor = 1.5 * perspective_factor
        dx = scan_x - center_x
        dy = scan_y - center_y
        norm = math.sqrt(dx*dx + dy*dy)
        if norm == 0: norm = 1 # Avoid division by zero
        perp_dx = -dy / norm
        perp_dy = dx / norm

        points = [
            center_x - perp_dx * thickness_factor * 0.5, center_y - perp_dy * thickness_factor * 0.5, # Base start left
            center_x + perp_dx * thickness_factor * 0.5, center_y + perp_dy * thickness_factor * 0.5, # Base start right
            scan_x + perp_dx * thickness_factor * 0.1, scan_y + perp_dy * thickness_factor * 0.1, # Tip end right
            scan_x - perp_dx * thickness_factor * 0.1, scan_y - perp_dy * thickness_factor * 0.1, # Tip end left
        ]
        canvas_to_use.create_polygon(points, fill="#FFFFFF", outline="", smooth=True, tags="wave")

        # Draw glowing dot at end of beam with perspective size
        scan_dot_size_base = outer_radius * 0.04
        scan_dot_oscillation = 1 + 0.3 * math.sin(current_time * 5 + i)
        scan_dot_size = max(1, scan_dot_size_base * scan_dot_oscillation * perspective_factor) # Ensure size >= 1

        canvas_to_use.create_oval(
            scan_x - scan_dot_size, scan_y - scan_dot_size,
            scan_x + scan_dot_size, scan_y + scan_dot_size,
            fill=neon_blue, outline="#FFFFFF", width=1, tags="wave"
        )

        # Add secondary pulsing glow for enhanced effect with perspective
        canvas_to_use.create_oval(
            scan_x - scan_dot_size*1.5, scan_y - scan_dot_size*1.5,
            scan_x + scan_dot_size*1.5, scan_y + scan_dot_size*1.5,
            fill="", outline=neon_blue, width=1, tags="wave"
        )
    
    # Add tech details around outer ring - metallic segments with 3D bevels
    num_segments = 8
    for i in range(num_segments):
        segment_angle = 2 * math.pi * i / num_segments + spin * 0.5 # Slower spin
        segment_radius = outer_radius * 1.1 * depth_pulse # Place slightly outside main radius

        # Segment size with 3D perspective (closer segments appear larger)
        perspective = 0.7 + 0.3 * math.sin(segment_angle + spin) # Simulates perspective
        segment_width = outer_radius * 0.18 * perspective * depth_pulse
        segment_height = outer_radius * 0.1 * perspective * depth_pulse

        # Calculate position with perspective
        segment_x = center_x + math.cos(segment_angle) * segment_radius * depth_pulse
        segment_y = center_y + math.sin(segment_angle) * segment_radius * depth_pulse

        # Draw 3D metallic segment base
        canvas_to_use.create_rectangle(
            segment_x - segment_width / 2, segment_y - segment_height / 2,
            segment_x + segment_width / 2, segment_y + segment_height / 2,
            fill=metallic_medium, outline="", width=0, tags="wave" # No outline for base
        )

        # Add highlight and shadow for 3D bevel effect
        if math.sin(segment_angle + spin) > 0: # Top segments get highlight
            canvas_to_use.create_line(
                segment_x - segment_width/2, segment_y - segment_height/2, # Top-left
                segment_x + segment_width/2, segment_y - segment_height/2, # Top-right
                fill=metallic_light, width=2, tags="wave"
            )
            canvas_to_use.create_line(
                segment_x - segment_width/2, segment_y - segment_height/2, # Top-left
                segment_x - segment_width/2, segment_y + segment_height/2, # Bottom-left
                fill=metallic_light, width=2, tags="wave"
            )
        else: # Bottom segments get shadow
            canvas_to_use.create_line(
                segment_x + segment_width/2, segment_y - segment_height/2, # Top-right
                segment_x + segment_width/2, segment_y + segment_height/2, # Bottom-right
                fill="#0A0A18", width=2, tags="wave"
            )
            canvas_to_use.create_line(
                segment_x - segment_width/2, segment_y + segment_height/2, # Bottom-left
                segment_x + segment_width/2, segment_y + segment_height/2, # Bottom-right
                fill="#0A0A18", width=2, tags="wave"
            )

        # Add tech detail in the center of each segment with perspective size
        detail_width = segment_width * 0.5
        detail_height = segment_height * 0.3
        if detail_width > 1 and detail_height > 1: # Only draw if large enough
             canvas_to_use.create_rectangle(
                segment_x - detail_width / 2, segment_y - detail_height / 2,
                segment_x + detail_width / 2, segment_y + detail_height / 2,
                fill=neon_purple if i % 4 == 0 else neon_blue, outline="", tags="wave"
            )

    # Add dynamic energy arcs for enhanced tech feel with perspective
    for i in range(6):
        arc_start_angle = (spin * 57.3 + i * 60) % 360 # Convert radians to degrees
        arc_extent = 20 + 10 * math.sin(current_time * 3 + i)
        # Vary radius and perspective
        arc_radius_base = core_radius_3d * 1.2 # Slightly outside core
        arc_oscillation = 0.9 + 0.1 * math.sin(current_time + i)
        perspective = 1 + 0.1 * math.sin(math.radians(arc_start_angle) + current_time * 0.5)
        arc_radius = arc_radius_base * arc_oscillation * perspective

        canvas_to_use.create_arc(
            center_x - arc_radius, center_y - arc_radius,
            center_x + arc_radius, center_y + arc_radius,
            start=arc_start_angle, extent=arc_extent,
            style=tk.ARC, outline=neon_purple if i % 2 == 0 else neon_blue,
            width=max(1, 2 * perspective), tags="wave" # Perspective width
        )

    # Add holographic scan lines for tech effect with perspective
    for i in range(12):
        # Calculate y position relative to center
        rel_y = -core_radius_3d + (2 * core_radius_3d * i / 12)
        line_y = center_y + rel_y

        # Calculate perspective factor based on y position (closer to center = wider)
        perspective_factor = math.sqrt(max(0, core_radius_3d**2 - rel_y**2)) / core_radius_3d if core_radius_3d > 0 else 1
        line_width_half = core_radius_3d * 0.9 * perspective_factor

        line_alpha_factor = 0.5 + 0.5 * math.sin(line_y / 10 + current_time * 2) # More subtle alpha variation
        line_color = neon_blue

        # Only draw visible lines
        if line_alpha_factor > 0.1:
             # Use a subtle width variation instead of alpha if alpha isn't directly supported
            scan_line_width = max(1, 1.5 * line_alpha_factor)
            canvas_to_use.create_line(
                center_x - line_width_half, line_y,
                center_x + line_width_half, line_y,
                fill=line_color, width=scan_line_width, tags="wave"
            )

    # Add center bright core with lens flare for realistic light effect
    core_size = core_radius_3d * 0.15 * pulse # Smaller, sharper core
    canvas_to_use.create_oval(
        center_x - core_size, center_y - core_size,
        center_x + core_size, center_y + core_size,
        fill="#FFFFFF", outline=neon_red, width=1, tags="wave"
    )

    # Add diagonal light flares with varying intensity
    flare_base_length = core_radius_3d * 1.5
    for angle_deg in [0, 45, 90, 135]:
        # Intensity varies with time and angle
        intensity = 0.6 + 0.4 * math.sin(current_time * 3 + math.radians(angle_deg))
        if intensity < 0.1: continue # Skip faint flares

        flare_length = flare_base_length * intensity * pulse
        rad_angle = math.radians(angle_deg)

        # Calculate endpoints
        x1 = center_x + math.cos(rad_angle) * flare_length
        y1 = center_y + math.sin(rad_angle) * flare_length
        x2 = center_x - math.cos(rad_angle) * flare_length
        y2 = center_y - math.sin(rad_angle) * flare_length

        # Draw flare line with width based on intensity
        flare_width = max(1, 1.5 * intensity)
        canvas_to_use.create_line(
            x1, y1, x2, y2,
            fill="#FFFFFF", width=flare_width, tags="wave"
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
    current_time = time.time()
    pulse = math.sin(current_time * 2) * 0.1 + 0.9
    rotation = (current_time * 0.5 + phase) % (2 * math.pi)
    depth_oscillation = math.sin(current_time * 0.7) * 0.15 + 0.85 # For 3D depth effect
    
    # Vibrant neon color palette
    neon_cyan = "#00FFFF"
    neon_magenta = "#FF00FF"
    neon_blue = "#3366FF"
    neon_orange = "#FF6600"
    neon_green = "#33FF99"
    neon_yellow = "#FFFF00"
    metallic_dark = "#1A1A2E"
    metallic_light = "#5E5E8E"
    metallic_medium = "#303050" # Added medium metallic shade
    
    # Draw 3D layered base plate - multiple ovals create depth illusion
    for i in range(3):
        depth_factor = 1 - (i * 0.05)
        radius_3d = outer_radius * 1.1 * depth_factor * depth_oscillation # Apply depth
        gradient_value = int(30 + i * 10)
        gradient_color = f"#{gradient_value:02x}{gradient_value:02x}{gradient_value+20:02x}"
        canvas.create_oval(
            center_x - radius_3d, center_y - radius_3d,
            center_x + radius_3d, center_y + radius_3d,
            fill="", outline=gradient_color,
            width=2, tags="recording"
        )
    
    # Draw outer hexagonal frame with 3D perspective effect
    hex_points = []
    hex_radius = outer_radius * 1.1 * depth_oscillation # Apply depth
    for i in range(6):
        angle = math.pi/6 + i * math.pi/3 + rotation * 0.1
        # Add perspective by varying the radius based on angle relative to rotation
        perspective = 1.0 + 0.08 * math.sin(angle - rotation * 0.5) # Perspective effect tied to rotation
        hex_x = center_x + math.cos(angle) * hex_radius * perspective
        hex_y = center_y + math.sin(angle) * hex_radius * perspective
        hex_points.extend([hex_x, hex_y])
    
    # Draw hexagon with gradient-like outline for 3D
    # Draw multiple lines for thickness and color effect
    canvas.create_polygon(hex_points, fill="", outline=neon_blue, width=4, tags="recording")
    canvas.create_polygon(hex_points, fill="", outline="#FFFFFF", width=1, tags="recording") # Highlight
    
    # Add metallic inner ring with 3D bevels
    inner_radius_3d = inner_radius * depth_oscillation # Apply depth
    canvas.create_oval(
        center_x - inner_radius_3d * 1.05, center_y - inner_radius_3d * 1.05,
        center_x + inner_radius_3d * 1.05, center_y + inner_radius_3d * 1.05,
        fill=metallic_dark, outline=metallic_light, width=2, tags="recording"
    )
    
    # Add highlight reflection on top edge for 3D effect
    canvas.create_arc(
        center_x - inner_radius_3d * 1.04, center_y - inner_radius_3d * 1.04,
        center_x + inner_radius_3d * 1.04, center_y + inner_radius_3d * 1.04,
        start=30, extent=120, style=tk.ARC,
        outline=metallic_light, width=3, tags="recording"
    )
    # Add shadow on bottom edge for 3D effect
    canvas.create_arc(
        center_x - inner_radius_3d * 1.04, center_y - inner_radius_3d * 1.04,
        center_x + inner_radius_3d * 1.04, center_y + inner_radius_3d * 1.04,
        start=210, extent=120, style=tk.ARC,
        outline="#0A0A18", width=3, tags="recording" # Darker shadow
    )
    
    # Draw inner hexagonal frame with 3D dynamic rotation
    inner_hex_points = []
    inner_hex_radius = outer_radius * 0.7 * depth_oscillation # Apply depth
    for i in range(6):
        angle = math.pi/6 + i * math.pi/3 - rotation * 0.2
        # Inner hex has different perspective than outer
        perspective = 1.0 + 0.05 * math.cos(angle - rotation * 1.2)
        hex_x = center_x + math.cos(angle) * inner_hex_radius * perspective
        hex_y = center_y + math.sin(angle) * inner_hex_radius * perspective
        inner_hex_points.extend([hex_x, hex_y])
    
    canvas.create_polygon(
        inner_hex_points,
        fill="",
        outline=neon_orange,
        width=2,
        tags="recording"
    )
    canvas.create_polygon( # Inner highlight
        inner_hex_points,
        fill="",
        outline="#FFFFFF",
        width=1,
        tags="recording"
    )
    
    # Draw circular progress indicator with 3D metallic track
    progress_radius = inner_radius_3d # Use depth-adjusted radius
    # Base metallic track with 3D bevel effect using multiple arcs
    canvas.create_arc( # Dark base
        center_x - progress_radius, center_y - progress_radius,
        center_x + progress_radius, center_y + progress_radius,
        start=0, extent=360,
        outline=metallic_medium, width=6, style=tk.ARC, tags="recording"
    )
    canvas.create_arc( # Shadow
        center_x - progress_radius, center_y - progress_radius,
        center_x + progress_radius, center_y + progress_radius,
        start=200, extent=140, style=tk.ARC,
        outline="#0A0A18", width=5, tags="recording"
    )
    canvas.create_arc( # Highlight
        center_x - progress_radius, center_y - progress_radius,
        center_x + progress_radius, center_y + progress_radius,
        start=20, extent=140, style=tk.ARC,
        outline=metallic_light, width=4, tags="recording"
    )
    
    # Progress arc with neon glow effect
    start_angle = 90
    extent = -phase * 360 * 0.999 # Use phase for progress directly, avoid full circle overlap glitch
    
    # Outer glow effect for progress arc
    canvas.create_arc(
        center_x - progress_radius * 1.02, center_y - progress_radius * 1.02,
        center_x + progress_radius * 1.02, center_y + progress_radius * 1.02,
        start=start_angle, extent=extent,
        outline=neon_cyan, width=8, # Wider glow
        style=tk.ARC, tags="recording"
    )
     # Inner glow effect for progress arc
    canvas.create_arc(
        center_x - progress_radius * 0.98, center_y - progress_radius * 0.98,
        center_x + progress_radius * 0.98, center_y + progress_radius * 0.98,
        start=start_angle, extent=extent,
        outline=neon_cyan, width=6, # Slightly narrower inner glow
        style=tk.ARC, tags="recording"
    )
    # Main progress arc - bright white core
    canvas.create_arc(
        center_x - progress_radius, center_y - progress_radius,
        center_x + progress_radius, center_y + progress_radius,
        start=start_angle, extent=extent,
        outline="#FFFFFF", width=3,
        style=tk.ARC, tags="recording"
    )
    
    # Draw holographic orbit circles with 3D movement
    for i in range(4):
        # Each orbit has different phase and oscillation
        orbit_phase = rotation + i * (math.pi / 2) # 90 degrees separation
        orbit_oscillation = 0.2 * math.sin(current_time * (1 + i * 0.5) + i)
        orbit_radius_base = inner_radius_3d * (0.4 + i * 0.15)
        
        # Calculate 3D position with perspective oscillation
        perspective_factor = 1 + 0.3 * math.sin(orbit_phase + rotation) # Perspective varies with angle
        orbit_radius = orbit_radius_base * (1 + orbit_oscillation) * perspective_factor
        
        orbit_x = center_x + math.cos(orbit_phase) * orbit_radius
        orbit_y = center_y + math.sin(orbit_phase) * orbit_radius
        
        # Size varies with perspective
        orbit_size_base = outer_radius * 0.06 # Slightly smaller base
        orbit_size = max(1, orbit_size_base * pulse * perspective_factor) # Ensure size >= 1
        
        # Draw the orbiting element with metallic gradient look
        orbit_color = neon_magenta if i % 2 == 0 else neon_green
        # Outer glow
        canvas.create_oval(
            orbit_x - orbit_size * 1.3, orbit_y - orbit_size * 1.3,
            orbit_x + orbit_size * 1.3, orbit_y + orbit_size * 1.3,
            fill="", outline=orbit_color,
            width=1, tags="recording"
        )
        # Main orbit body
        canvas.create_oval(
            orbit_x - orbit_size, orbit_y - orbit_size,
            orbit_x + orbit_size, orbit_y + orbit_size,
            fill=orbit_color,
            outline="#FFFFFF", width=1, tags="recording"
        )
        
        # Draw connecting beam to center with light intensity varying by distance
        # Use a gradient line if possible, otherwise simulate with segments
        beam_color = neon_orange if i % 2 == 0 else neon_cyan
        dist_to_center = math.sqrt((orbit_x - center_x)**2 + (orbit_y - center_y)**2)
        if dist_to_center > 1: # Avoid drawing if point is at center
            num_segments = 5
            for j in range(num_segments):
                segment_start = j / num_segments
                segment_end = (j + 1) / num_segments
                x1 = center_x + (orbit_x - center_x) * segment_start
                y1 = center_y + (orbit_y - center_y) * segment_start
                x2 = center_x + (orbit_x - center_x) * segment_end
                y2 = center_y + (orbit_y - center_y) * segment_end
                
                # Width decreases away from center, incorporates perspective
                beam_width = max(1, (3 - segment_start * 2) * perspective_factor)
                canvas.create_line(x1, y1, x2, y2, fill=beam_color, width=beam_width, tags="recording")
    
    # Draw central recording indicator with 3D layers
    base_size = inner_radius_3d * 0.25 # Use depth-adjusted radius
    # Base pulsing circle - Dark red
    canvas.create_oval(
        center_x - base_size * pulse, center_y - base_size * pulse,
        center_x + base_size * pulse, center_y + base_size * pulse,
        fill="#800000", outline=neon_orange, width=2, tags="recording"
    )
    
    # Middle layer with different pulse rate - Bright Red
    mid_pulse = math.sin(current_time * 3) * 0.1 + 0.9
    canvas.create_oval(
        center_x - base_size * 0.8 * mid_pulse, center_y - base_size * 0.8 * mid_pulse,
        center_x + base_size * 0.8 * mid_pulse, center_y + base_size * 0.8 * mid_pulse,
        fill="#FF2000", outline=neon_magenta, width=1, tags="recording"
    )
    
    # Core with brightest color - White
    canvas.create_oval(
        center_x - base_size * 0.5 * pulse, center_y - base_size * 0.5 * pulse,
        center_x + base_size * 0.5 * pulse, center_y + base_size * 0.5 * pulse,
        fill="#FFFFFF", outline="", tags="recording"
    )
    
    # Add 3D tech details - digital particles with depth simulation
    num_particles = 16 # More particles
    for i in range(num_particles):
        particle_angle = 2 * math.pi * i / num_particles + rotation
        # Particles move in and out from center with more variation
        particle_distance_base = inner_radius_3d * 0.5
        particle_oscillation = 0.15 * math.sin(current_time * (2 + i * 0.2) + i)
        particle_distance = particle_distance_base * (1 + particle_oscillation)
        
        # Calculate 3D position with perspective based on angle
        perspective = 0.7 + 0.3 * math.cos(particle_angle + rotation * 2)
        particle_x = center_x + math.cos(particle_angle) * particle_distance * perspective
        particle_y = center_y + math.sin(particle_angle) * particle_distance * perspective
        
        # Particle size varies with perspective and a fast pulse
        particle_size_base = outer_radius * 0.03
        particle_size_pulse = 1 + math.sin(current_time * 6 + i) * 0.3 # Very fast pulse
        particle_size = max(1, particle_size_base * particle_size_pulse * perspective)
        
        # Fade particle as it moves outwards
        opacity_factor = max(0, 1 - (current_time * 0.8) % 1.5)
        if opacity_factor < 0.1: continue # Skip faded particles
        
        # Choose color based on particle type
        shape_type = i % 3
        particle_color = neon_green if shape_type == 0 else (neon_cyan if shape_type == 1 else neon_yellow)
        
        # Draw shape (adjust fill based on opacity if possible, otherwise skip drawing if too faint)
        if shape_type == 0: # Squares
            canvas.create_rectangle(
                particle_x - particle_size, particle_y - particle_size,
                particle_x + particle_size, particle_y + particle_size,
                fill=particle_color, outline="", tags="recording"
            )
        elif shape_type == 1: # Circles
            canvas.create_oval(
                particle_x - particle_size, particle_y - particle_size,
                particle_x + particle_size, particle_y + particle_size,
                fill=particle_color, outline="", tags="recording"
            )
        else: # Diamonds
            diamond_points = [
                particle_x, particle_y - particle_size * 1.2, # Top
                particle_x + particle_size, particle_y,       # Right
                particle_x, particle_y + particle_size * 1.2, # Bottom
                particle_x - particle_size, particle_y,       # Left
            ]
            canvas.create_polygon(diamond_points, fill=particle_color, outline="", tags="recording")
    
    # Add dynamic energy rings pulsing outward for holographic effect
    num_rings = 4 # More rings
    for i in range(num_rings):
        # Ring expands with time and resets, slightly faster
        ring_phase = ((current_time * 0.7 + i/num_rings) % 1)
        ring_radius = inner_radius_3d * 0.1 + ring_phase * inner_radius_3d * 0.8 # Start small, expand wide
        ring_opacity_factor = max(0, (1 - ring_phase) ** 0.7) # Fade curve
        
        if ring_opacity_factor > 0.1: # Only draw visible rings
            ring_color = neon_green if i % 2 == 0 else neon_cyan
            ring_width = max(1, 2 * ring_opacity_factor) # Thinner as they fade
            canvas.create_oval(
                center_x - ring_radius, center_y - ring_radius,
                center_x + ring_radius, center_y + ring_radius,
                fill="", outline=ring_color, width=ring_width, tags="recording"
            )
    
    # Add digital scan lines with 3D motion effect (Green theme)
    num_scan_lines = 12 # More lines
    scan_area_radius = inner_radius_3d * pulse # Pulsing scan area
    for i in range(num_scan_lines):
        # Horizontal scan lines - moving down faster
        y_rel = -scan_area_radius + scan_area_radius * 2 * ((current_time * 0.5 + i/num_scan_lines) % 1)
        y_pos = center_y + y_rel
        # Calculate perspective width based on y position
        perspective_width = math.sqrt(max(0, scan_area_radius**2 - y_rel**2)) if scan_area_radius > 0 else 0
        
        # Opacity varies with sine wave and position
        opacity_factor = 0.5 + 0.5 * math.sin(y_pos / 12 + current_time * 2.5)**2
        
        if opacity_factor > 0.1:
            line_width = max(1, 1.5 * opacity_factor)
            canvas.create_line(
                center_x - perspective_width, y_pos,
                center_x + perspective_width, y_pos,
                fill=neon_green, width=line_width, tags="recording"
            )
    
    # Add tech corner brackets for framing (Cyan/Yellow theme)
    bracket_size = outer_radius * 0.18 # Slightly larger brackets
    bracket_radius = outer_radius * 1.2 * depth_oscillation # Apply depth
    for i in range(4):
        angle = math.pi/4 + i * math.pi/2 # 45 degree angles
        # Corner positions with perspective effect
        perspective = 1 + 0.05 * math.sin(current_time * 1.5 + i) # Faster perspective pulse
        corner_x = center_x + math.cos(angle) * bracket_radius * perspective
        corner_y = center_y + math.sin(angle) * bracket_radius * perspective
        
        # Calculate bracket end points
        bracket_end1_x = corner_x - math.cos(angle - math.pi/4) * bracket_size
        bracket_end1_y = corner_y - math.sin(angle - math.pi/4) * bracket_size
        bracket_end2_x = corner_x - math.cos(angle + math.pi/4) * bracket_size
        bracket_end2_y = corner_y - math.sin(angle + math.pi/4) * bracket_size
        
        # Draw the bracket lines with glow
        bracket_width = max(1, 2 * perspective)
        canvas.create_line(bracket_end1_x, bracket_end1_y, corner_x, corner_y,
                           fill=neon_cyan, width=bracket_width + 1, tags="recording") # Base glow
        canvas.create_line(bracket_end1_x, bracket_end1_y, corner_x, corner_y,
                           fill="#FFFFFF", width=max(1, bracket_width -1), tags="recording") # Highlight
        canvas.create_line(bracket_end2_x, bracket_end2_y, corner_x, corner_y,
                           fill=neon_cyan, width=bracket_width + 1, tags="recording") # Base glow
        canvas.create_line(bracket_end2_x, bracket_end2_y, corner_x, corner_y,
                           fill="#FFFFFF", width=max(1, bracket_width -1), tags="recording") # Highlight
        
        # Add tech dot at corner (Yellow)
        dot_size = max(1, 3 * perspective)
        canvas.create_oval(corner_x - dot_size, corner_y - dot_size,
                           corner_x + dot_size, corner_y + dot_size,
                           fill=neon_yellow, outline="", tags="recording")


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
    pulse = math.sin(current_time * 2) * 0.1 + 0.9 # Base pulse
    fast_pulse = 0.7 + 0.3 * abs(math.sin(current_time * 4)) # Faster, sharper pulse (0.7 to 1.0)
    rotation = current_time * 0.3 % (2 * math.pi)
    depth_oscillation = math.sin(current_time * 0.5) * 0.1 + 0.9 # Gentle depth oscillation
    
    # Vibrant neon color palette (Success/Completion themed)
    neon_green = "#00FF66"
    neon_cyan = "#00FFFF"
    neon_blue = "#3366FF" # Less prominent blue
    neon_yellow = "#FFFF00" # Highlight color
    metallic_dark_green = "#0A3320"
    metallic_medium_green = "#0E6245"
    metallic_light_green = "#18A67C"
    metallic_highlight = "#A0FFE0" # Brighter green highlight
    
    # Draw 3D base plate with metallic gradient (Green theme)
    base_radius = outer_radius * 1.15 * depth_oscillation # Apply depth
    for i in range(4):
        depth_factor = 1 - (i * 0.05)
        radius_3d = base_radius * depth_factor
        gradient_value_g = int(10 + i * 15) # Green channel base
        gradient_value_b = int(5 + i * 5) # Slight blue tint
        gradient_color = f"#0A{gradient_value_g:02x}{gradient_value_b:02x}" # Dark green metallic
        
        canvas.create_oval(
            center_x - radius_3d, center_y - radius_3d,
            center_x + radius_3d, center_y + radius_3d,
            fill="",
            outline=gradient_color,
            width=2,
            tags="complete"
        )
    
    # Draw outer hexagonal frame with 3D perspective (Green theme)
    hex_radius = outer_radius * 1.1 * depth_oscillation # Apply depth
    hex_points = []
    for i in range(6):
        angle = math.pi/6 + i * math.pi/3 + rotation * 0.1 # Slow rotation
        # Add perspective by varying the radius based on angle
        perspective = 1.0 + 0.08 * math.sin(angle + rotation * 0.5)
        hex_x = center_x + math.cos(angle) * hex_radius * perspective
        hex_y = center_y + math.sin(angle) * hex_radius * perspective
        hex_points.extend([hex_x, hex_y])
    
    # Draw hexagon with glow effect
    canvas.create_polygon(hex_points, fill="", outline=neon_green, width=4, tags="complete")
    canvas.create_polygon(hex_points, fill="", outline="#FFFFFF", width=1, tags="complete") # Highlight
    
    # Draw inner rotating hexagonal frame (Cyan theme)
    inner_hex_radius = outer_radius * 0.7 * depth_oscillation # Apply depth
    inner_hex_points = []
    for i in range(6):
        angle = math.pi/6 + i * math.pi/3 - rotation * 0.2 # Faster counter-rotation
        # Different perspective for inner hex
        perspective = 1.0 + 0.05 * math.cos(angle - rotation * 1.2)
        hex_x = center_x + math.cos(angle) * inner_hex_radius * perspective
        hex_y = center_y + math.sin(angle) * inner_hex_radius * perspective
        inner_hex_points.extend([hex_x, hex_y])
    
    canvas.create_polygon(inner_hex_points, fill="", outline=neon_cyan, width=3, tags="complete")
    canvas.create_polygon(inner_hex_points, fill="", outline="#FFFFFF", width=1, tags="complete") # Highlight
    
    # Draw 3D layered success circle with metallic green shading
    inner_radius_3d = inner_radius * depth_oscillation # Apply depth
    # Base layer - dark metallic green
    canvas.create_oval(
        center_x - inner_radius_3d * pulse, center_y - inner_radius_3d * pulse,
        center_x + inner_radius_3d * pulse, center_y + inner_radius_3d * pulse,
        fill=metallic_dark_green, outline=metallic_light_green, width=3,
        tags="complete"
    )
    
    # Add highlight reflection on top edge for 3D effect
    canvas.create_arc(
        center_x - inner_radius_3d * pulse, center_y - inner_radius_3d * pulse,
        center_x + inner_radius_3d * pulse, center_y + inner_radius_3d * pulse,
        start=30, extent=120, style=tk.ARC,
        outline=metallic_highlight, width=3, tags="complete" # Brighter highlight
    )
    
    # Add shadow on bottom edge for 3D effect
    canvas.create_arc(
        center_x - inner_radius_3d * pulse, center_y - inner_radius_3d * pulse,
        center_x + inner_radius_3d * pulse, center_y + inner_radius_3d * pulse,
        start=210, extent=120, style=tk.ARC,
        outline="#051A10", width=3, tags="complete" # Darker shadow
    )
    
    # Draw middle layer with different pulse rate (medium green)
    inner_pulse = math.sin(current_time * 3) * 0.1 + 0.9
    middle_radius = inner_radius_3d * 0.85 # Slightly larger middle layer
    canvas.create_oval(
        center_x - middle_radius * inner_pulse, center_y - middle_radius * inner_pulse,
        center_x + middle_radius * inner_pulse, center_y + middle_radius * inner_pulse,
        fill=metallic_medium_green, outline=neon_green, width=2,
        tags="complete"
    )
    
    # Add tech details - circular segments with 3D effects and rotation
    num_segments = 10 # More segments
    segment_radius = inner_radius_3d * 0.9 * pulse # Pulsing radius
    for i in range(num_segments):
        angle_offset = rotation * 1.5 # Faster rotation for segments
        start_angle = (i * 360 / num_segments + angle_offset * 57.3) % 360 # Degrees
        extent = 360 / num_segments - 10 # Gap between segments
        
        # Calculate perspective based on vertical position (sin)
        segment_mid_angle_rad = math.radians(start_angle + extent / 2)
        perspective = 0.8 + 0.2 * abs(math.sin(segment_mid_angle_rad)) # Wider at top/bottom
        
        segment_width = max(1, (3 if i % 2 == 0 else 2) * perspective) # Varying width with perspective
        segment_color = neon_green if i % 2 == 0 else neon_cyan
        
        # Main segment
        canvas.create_arc(
            center_x - segment_radius, center_y - segment_radius,
            center_x + segment_radius, center_y + segment_radius,
            start=start_angle, extent=extent,
            style=tk.ARC, outline=segment_color,
            width=segment_width,
            tags="complete"
        )
        
        # Add segment end caps for 3D tech feel (small glowing dots)
        if i % 2 == 0: # Only on wider segments
            start_rad = math.radians(start_angle)
            end_rad = math.radians(start_angle + extent)
            
            start_x = center_x + math.cos(start_rad) * segment_radius
            start_y = center_y - math.sin(start_rad) * segment_radius # Tkinter angles are inverted Y
            end_x = center_x + math.cos(end_rad) * segment_radius
            end_y = center_y - math.sin(end_rad) * segment_radius
            
            cap_size = max(1, 2 * perspective) # Perspective size
            for px, py in [(start_x, start_y), (end_x, end_y)]:
                canvas.create_oval(px - cap_size, py - cap_size, px + cap_size, py + cap_size,
                                    fill=neon_yellow, outline="", tags="complete")
    
    # Draw central completion area with 3D check mark
    check_bg_radius = inner_radius_3d * 0.5 # Larger background
    # Base circle for the check mark background (pulsing)
    canvas.create_oval(
        center_x - check_bg_radius * fast_pulse, center_y - check_bg_radius * fast_pulse,
        center_x + check_bg_radius * fast_pulse, center_y + check_bg_radius * fast_pulse,
        fill=metallic_medium_green, outline=neon_green, width=2, tags="complete"
    )
    
    # 3D check mark using multiple lines for thickness and glow
    check_scale = inner_radius_3d * 0.35 * fast_pulse # Scale with fast pulse
    
    # Define check points relative to center
    p1 = (center_x - check_scale * 0.7, center_y + check_scale * 0.1)
    p2 = (center_x - check_scale * 0.1, center_y + check_scale * 0.7) # Bottom point
    p3 = (center_x + check_scale * 0.8, center_y - check_scale * 0.6)
    
    # Draw check mark layers for 3D / glow effect
    # Base Glow (Widest)
    canvas.create_line(p1, p2, p3, fill=neon_green, width=10, smooth=True, capstyle=tk.ROUND, joinstyle=tk.ROUND, tags="complete")
    # Inner Glow / Body
    canvas.create_line(p1, p2, p3, fill=metallic_highlight, width=6, smooth=True, capstyle=tk.ROUND, joinstyle=tk.ROUND, tags="complete")
    # Bright Core
    canvas.create_line(p1, p2, p3, fill="#FFFFFF", width=3, smooth=True, capstyle=tk.ROUND, joinstyle=tk.ROUND, tags="complete")
    
    # Add tech details - digital particles exploding outwards with 3D depth
    num_particles = 20
    explosion_phase = (current_time * 0.8) % 1.5 # Controls explosion radius, resets every 1.5s
    max_explosion_radius = inner_radius_3d * 1.2
    
    for i in range(num_particles):
        particle_angle = 2 * math.pi * i / num_particles + rotation * 0.5 # Angle of explosion
        # Particle travels outwards based on explosion_phase
        current_radius = explosion_phase * max_explosion_radius
        
        # Calculate 3D position with perspective (particles further away appear smaller)
        # Simulate perspective by scaling based on distance (inverse relationship)
        perspective = max(0.1, 1 - (current_radius / max_explosion_radius) * 0.7)
        
        particle_x = center_x + math.cos(particle_angle) * current_radius
        particle_y = center_y + math.sin(particle_angle) * current_radius
        
        # Particle size varies with perspective and a fast pulse
        particle_size_base = outer_radius * 0.03
        particle_size_pulse = 1 + math.sin(current_time * 6 + i) * 0.3 # Very fast pulse
        particle_size = max(1, particle_size_base * particle_size_pulse * perspective)
        
        # Fade particle as it moves outwards
        opacity_factor = max(0, 1 - explosion_phase / 1.5)
        if opacity_factor < 0.1: continue # Skip faded particles
        
        # Choose color based on particle type
        shape_type = i % 3
        particle_color = neon_green if shape_type == 0 else (neon_cyan if shape_type == 1 else neon_yellow)
        
        # Draw shape (adjust fill based on opacity if possible, otherwise skip drawing if too faint)
        if shape_type == 0: # Squares
            canvas.create_rectangle(
                particle_x - particle_size, particle_y - particle_size,
                particle_x + particle_size, particle_y + particle_size,
                fill=particle_color, outline="", tags="complete"
            )
        elif shape_type == 1: # Circles
            canvas.create_oval(
                particle_x - particle_size, particle_y - particle_size,
                particle_x + particle_size, particle_y + particle_size,
                fill=particle_color, outline="", tags="complete"
            )
        else: # Diamonds
            diamond_points = [
                particle_x, particle_y - particle_size * 1.2, # Top
                particle_x + particle_size, particle_y,       # Right
                particle_x, particle_y + particle_size * 1.2, # Bottom
                particle_x - particle_size, particle_y,       # Left
            ]
            canvas.create_polygon(diamond_points, fill=particle_color, outline="", tags="complete")
    
    # Add central glow behind checkmark with 3D layers
    glow_base_size = check_bg_radius * 0.6 # Related to checkmark bg size
    # Base glow (widest, softest)
    canvas.create_oval(
        center_x - glow_base_size * pulse * 1.5, center_y - glow_base_size * pulse * 1.5,
        center_x + glow_base_size * pulse * 1.5, center_y + glow_base_size * pulse * 1.5,
        fill="", outline=neon_green, width=3, tags="complete"
    )
    # Middle glow
    canvas.create_oval(
        center_x - glow_base_size * pulse, center_y - glow_base_size * pulse,
        center_x + glow_base_size * pulse, center_y + glow_base_size * pulse,
        fill="", outline=neon_yellow, width=2, tags="complete"
    )
    # Inner sharp glow
    canvas.create_oval(
        center_x - glow_base_size * pulse * 0.7, center_y - glow_base_size * pulse * 0.7,
        center_x + glow_base_size * pulse * 0.7, center_y + glow_base_size * pulse * 0.7,
        fill="", outline="#FFFFFF", width=1, tags="complete"
    )
    
    # Add dynamic energy rings pulsing outward (Green/Cyan)
    num_rings = 4
    for i in range(num_rings):
        # Ring expands with time and resets, slightly faster
        ring_phase = ((current_time * 0.7 + i/num_rings) % 1)
        ring_radius = inner_radius_3d * 0.1 + ring_phase * inner_radius_3d * 0.8 # Start small, expand wide
        ring_opacity_factor = max(0, (1 - ring_phase) ** 0.7) # Fade curve
        
        if ring_opacity_factor > 0.1: # Only draw visible rings
            ring_color = neon_green if i % 2 == 0 else neon_cyan
            ring_width = max(1, 2 * ring_opacity_factor) # Thinner as they fade
            canvas.create_oval(
                center_x - ring_radius, center_y - ring_radius,
                center_x + ring_radius, center_y + ring_radius,
                fill="", outline=ring_color, width=ring_width, tags="complete"
            )
    
    # Add digital scan lines with 3D motion effect (Green theme)
    num_scan_lines = 12 # More lines
    scan_area_radius = inner_radius_3d * pulse # Pulsing scan area
    for i in range(num_scan_lines):
        # Horizontal scan lines - moving down faster
        y_rel = -scan_area_radius + scan_area_radius * 2 * ((current_time * 0.5 + i/num_scan_lines) % 1)
        y_pos = center_y + y_rel
        # Calculate perspective width based on y position
        perspective_width = math.sqrt(max(0, scan_area_radius**2 - y_rel**2)) if scan_area_radius > 0 else 0
        
        # Opacity varies with sine wave and position
        opacity_factor = 0.5 + 0.5 * math.sin(y_pos / 12 + current_time * 2.5)**2
        
        if opacity_factor > 0.1:
            line_width = max(1, 1.5 * opacity_factor)
            canvas.create_line(
                center_x - perspective_width, y_pos,
                center_x + perspective_width, y_pos,
                fill=neon_green, width=line_width, tags="complete"
            )
    
    # Add tech corner brackets for framing (Cyan/Yellow theme)
    bracket_size = outer_radius * 0.18 # Slightly larger brackets
    bracket_radius = outer_radius * 1.2 * depth_oscillation # Apply depth
    for i in range(4):
        angle = math.pi/4 + i * math.pi/2 # 45 degree angles
        # Corner positions with perspective effect
        perspective = 1 + 0.05 * math.sin(current_time * 1.5 + i) # Faster perspective pulse
        corner_x = center_x + math.cos(angle) * bracket_radius * perspective
        corner_y = center_y + math.sin(angle) * bracket_radius * perspective
        
        # Calculate bracket end points
        bracket_end1_x = corner_x - math.cos(angle - math.pi/4) * bracket_size
        bracket_end1_y = corner_y - math.sin(angle - math.pi/4) * bracket_size
        bracket_end2_x = corner_x - math.cos(angle + math.pi/4) * bracket_size
        bracket_end2_y = corner_y - math.sin(angle + math.pi/4) * bracket_size
        
        # Draw the bracket lines with glow
        bracket_width = max(1, 2 * perspective)
        canvas.create_line(bracket_end1_x, bracket_end1_y, corner_x, corner_y,
                           fill=neon_cyan, width=bracket_width + 1, tags="complete") # Base glow
        canvas.create_line(bracket_end1_x, bracket_end1_y, corner_x, corner_y,
                           fill="#FFFFFF", width=max(1, bracket_width -1), tags="complete") # Highlight
        canvas.create_line(bracket_end2_x, bracket_end2_y, corner_x, corner_y,
                           fill=neon_cyan, width=bracket_width + 1, tags="complete") # Base glow
        canvas.create_line(bracket_end2_x, bracket_end2_y, corner_x, corner_y,
                           fill="#FFFFFF", width=max(1, bracket_width -1), tags="complete") # Highlight
        
        # Add tech dot at corner (Yellow)
        dot_size = max(1, 3 * perspective)
        canvas.create_oval(corner_x - dot_size, corner_y - dot_size,
                           corner_x + dot_size, corner_y + dot_size,
                           fill=neon_yellow, outline="", tags="complete")


def update_animation(status):
    """Update animation based on current status"""
    global animation_canvas, progress_bar, notification_label
    
    if animation_canvas is None:
        return
        
    width = animation_canvas.winfo_width()
    height = animation_canvas.winfo_height()
    
    if width <= 1 or height <= 1: # Not yet properly sized
        animation_canvas.after(100, lambda: update_animation(status))
        return
        
    # Use a continuous time-based phase for smoother animations if needed,
    # but phase = time.time() % 1 is often fine for looping effects.
    # Using full time allows for non-looping elements or longer cycles.
    phase_param = time.time() # Pass full time for more complex animations

    if status == "Waiting for sound...":
        # Pass phase=0 if the animation is self-contained using time.time()
        # Or pass phase_param if the animation needs an external sync value
        draw_sound_wave(animation_canvas, width, height, phase=0) # Changed phase to 0 as time is internal
        if progress_bar:
            # Reset progress bar smoothly? Or just set to 0?
             if progress_bar["value"] > 0:
                 progress_bar.config(value=max(0, progress_bar["value"] - 5)) # Animate reset
             else:
                 progress_bar.config(value=0)


    elif status == "Recording in progress...":
        # Calculate progress based on recording duration if available, otherwise use time modulo
        # For now, use a simple time-based phase for visual progress feedback
        recording_phase = (time.time() * 0.1) % 1 # Example: 10-second loop for progress vis
        draw_recording_animation(animation_canvas, width, height, phase=recording_phase)
        if progress_bar:
            # Update progress bar based on the visual phase or actual recording progress
            progress_bar.config(value=recording_phase * 100)

    elif status == "Recording complete":
        # No phase needed for complete animation usually, it might have its own internal time logic
        draw_complete_animation(animation_canvas, width, height)
        if progress_bar:
             # Animate to full or just set to 100?
            if progress_bar["value"] < 100:
                progress_bar.config(value=min(100, progress_bar["value"] + 5)) # Animate completion
            else:
                 progress_bar.config(value=100)

        # Show notification (logic remains the same)
        # if notification_label:
        #     notification_label.place(relx=0.5, y=10, anchor="n")
        #     notification_label.after(3000, lambda: notification_label.place_forget())

    # Continue animation loop
    # Adjust frame rate (e.g., 30fps -> ~33ms, 60fps -> ~16ms)
    # 50ms is 20fps, might be slightly choppy for complex animations
    animation_canvas.after(33, lambda: update_animation(status)) # Aim for ~30fps

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
    button.config(takefocus=1) # Make it keyboard-focusable
    
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
        # Ensure 'icon.ico' is in the same directory or provide a full path
        root.iconbitmap('eye.ico')
    except tk.TclError:
        print("Warning: icon.ico not found or invalid.")
        pass # Icon not available, continue without it
    
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
    
    # Animation area - Use the neumorphic frame creator for consistency?
    # For now, keeping the simple frame as the canvas itself is the visual focus.
    animation_frame = tk.Frame(main_frame, bg=PANEL_BG, bd=0, highlightthickness=0)
    animation_frame.pack(fill="both", expand=True, pady=10)

    animation_canvas = tk.Canvas(
        animation_frame,
        bg="#000000", # Changed background to solid black
        bd=0,
        highlightthickness=0,
        height=150 # Initial height, will resize
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
    progress_style.theme_use('alt') # 'clam', 'alt', 'default', 'classic'
    progress_style.configure(
        "TProgressbar",
        thickness=6,
        background=ACCENT_BLUE,
        troughcolor=DARKER_BG,
        borderwidth=0,
        # Remove lightcolor/darkcolor if not supported or needed by theme
        # lightcolor=ACCENT_BLUE,
        # darkcolor=ACCENT_BLUE
    )

    progress_bar = ttk.Progressbar(
        main_frame,
        style="TProgressbar",
        orient="horizontal",
        length=460, # Should match container width ideally
        mode="determinate",
        value=0 # Start at 0
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

    # Notification label (hidden initially) - Defined but not placed yet
    notification_label = tk.Label(
        root, # Place relative to root window, appears over other elements
        text="Notification Placeholder",
        font=(FONT_FAMILY, 10),
        bg=ACCENT_BLUE, # Use an accent color for visibility
        fg=DARK_BG, # Dark text on light bg
        padx=10,
        pady=5,
        relief="solid", # Add border for clarity
        bd=1
    )
    # Don't place it here, place it when show_notification is called

    # Start animation loop immediately
    # It needs an initial status to know what to draw
    update_animation("Waiting for sound...")

    # Key bindings for accessibility
    root.bind('<space>', lambda e: resume_func())
    root.bind('<Escape>', lambda e: pause_func())

    return status_label # Return the status label for the main script to update

def update_status(status_text):
    """Update the status label text and trigger animation update"""
    global status_label
    if status_label:
        # Check if the status actually changed to avoid redundant updates
        if status_label.cget("text") != status_text:
            status_label.config(text=status_text)
            # The update_animation function is called continuously by its own timer,
            # it will pick up the new status from the label or passed argument.
            # However, explicitly calling it ensures the *correct* animation starts immediately
            # after the status change, rather than waiting for the next cycle.
            # We need to pass the *new* status here.
            update_animation(status_text)

# Example usage (if running this file directly for testing)
if __name__ == "__main__":
    root_window = tk.Tk()

    # Dummy functions for testing
    def dummy_pause():
        print("Pause requested")
        update_status("Recording complete") # Simulate completion on pause

    def dummy_resume():
        print("Resume requested")
        update_status("Recording in progress...") # Simulate recording on resume

    setup_jarvis_ui(root_window, dummy_pause, dummy_resume)

    # Example of how the main script might update status externally:
    # root_window.after(5000, lambda: update_status("Recording in progress..."))
    # root_window.after(15000, lambda: update_status("Recording complete"))
    # root_window.after(18000, lambda: show_notification("Recording Saved!"))
    # root_window.after(20000, lambda: update_status("Waiting for sound..."))

    root_window.mainloop() 