import time
import math
import threading

# Animation constants
TARGET_FPS = 60
FRAME_TIME = 1.0 / TARGET_FPS
last_frame_time = 0
transition_state = None
transition_progress = 0
transition_duration = 0.3  # seconds 

# Add these variables for object pooling
animation_objects = {}
object_pool = {}

def get_pooled_object(canvas, obj_type, tag, **kwargs):
    """Get an object from the pool or create a new one"""
    pool_key = f"{obj_type}_{tag}"
    if pool_key not in object_pool:
        object_pool[pool_key] = []
    
    if not object_pool[pool_key]:
        # Create new object based on type
        if obj_type == "oval":
            obj_id = canvas.create_oval(0, 0, 1, 1, tags=tag, **kwargs)
        elif obj_type == "line":
            obj_id = canvas.create_line(0, 0, 1, 1, tags=tag, **kwargs)
        elif obj_type == "polygon":
            obj_id = canvas.create_polygon([0, 0, 1, 1], tags=tag, **kwargs)
        elif obj_type == "rectangle":
            obj_id = canvas.create_rectangle(0, 0, 1, 1, tags=tag, **kwargs)
        elif obj_type == "arc":
            obj_id = canvas.create_arc(0, 0, 1, 1, tags=tag, **kwargs)
        else:
            return None
    else:
        # Reuse existing object
        obj_id = object_pool[pool_key].pop()
        # Update properties
        if obj_type == "oval":
            canvas.itemconfig(obj_id, tags=tag, **kwargs)
        elif obj_type == "line":
            canvas.itemconfig(obj_id, tags=tag, **kwargs)
        elif obj_type == "polygon":
            canvas.itemconfig(obj_id, tags=tag, **kwargs)
        elif obj_type == "rectangle":
            canvas.itemconfig(obj_id, tags=tag, **kwargs)
        elif obj_type == "arc":
            canvas.itemconfig(obj_id, tags=tag, **kwargs)
    
    return obj_id

def return_to_pool(tag):
    """Return all objects with a tag to the pool"""
    global animation_canvas, object_pool, animation_objects
    
    if tag not in animation_objects:
        return
        
    for obj_id in animation_objects[tag]:
        obj_type = animation_canvas.type(obj_id)
        pool_key = f"{obj_type}_{tag}"
        object_pool[pool_key].append(obj_id)
        
    animation_objects[tag] = []

def update_animation_thread():
    """Update animations in a separate thread to avoid UI blocking"""
    global animation_running, current_status
    
    animation_running = True
    last_time = time.time()
    
    while animation_running:
        current_time = time.time()
        delta = current_time - last_time
        last_time = current_time
        
        # Request UI thread to update canvas
        root.after(0, lambda: update_animation_frame(current_status, delta))
        
        # Sleep to maintain target frame rate
        sleep_time = max(0, FRAME_TIME - (time.time() - current_time))
        time.sleep(sleep_time)

def update_animation_frame(status, delta_time):
    """Update a single animation frame - called from main thread"""
    # Animation logic using delta_time
    # ...existing update_animation code modified to use delta_time...

# Add these easing functions
def ease_out_cubic(x):
    return 1 - pow(1 - x, 3)

def ease_in_out_quad(x):
    return 2 * x * x if x < 0.5 else 1 - pow(-2 * x + 2, 2) / 2

def ease_in_out_sine(x):
    return -(math.cos(math.pi * x) - 1) / 2

def ease_out_elastic(x):
    c4 = (2 * math.pi) / 3
    return 0 if x == 0 else (1 if x == 1 else pow(2, -10 * x) * math.sin((x * 10 - 0.75) * c4) + 1)

def blend_animations(status_from, status_to, progress, canvas, width, height):
    """Blend between two animation states for smooth transitions"""
    # Save current state
    canvas.addtag_all("temp_save")
    
    # Draw both animations at reduced opacity
    if status_from == "Waiting for sound...":
        draw_sound_wave(canvas, width, height, opacity=1-progress)
    elif status_from == "Recording in progress...":
        recording_phase = (time.time() * 0.1) % 1
        draw_recording_animation(canvas, width, height, phase=recording_phase, opacity=1-progress)
    elif status_from == "Recording complete":
        draw_complete_animation(canvas, width, height, opacity=1-progress)
        
    if status_to == "Waiting for sound...":
        draw_sound_wave(canvas, width, height, opacity=progress)
    elif status_to == "Recording in progress...":
        recording_phase = (time.time() * 0.1) % 1
        draw_recording_animation(canvas, width, height, phase=recording_phase, opacity=progress)
    elif status_to == "Recording complete":
        draw_complete_animation(canvas, width, height, opacity=progress)

    # Restore original state
    canvas.dtag("temp_save", "temp_save") 

def draw_sound_wave(canvas=None, width=None, height=None, phase=0, opacity=1.0):
    """Draw a futuristic 3D AI eye with opacity support for transitions"""
    # ... existing code ...
    
    # Apply opacity to colors if supported
    def apply_opacity(color, alpha):
        if color.startswith("#") and len(color) == 7:
            r = int(color[1:3], 16)
            g = int(color[3:5], 16)
            b = int(color[5:7], 16)
            return f"#{r:02x}{g:02x}{b:02x}"
        return color
    
    neon_red = apply_opacity(neon_red, opacity)
    neon_blue = apply_opacity(neon_blue, opacity)
    neon_purple = apply_opacity(neon_purple, opacity)
    
    # ... rest of the function with width adjustments based on opacity ...
    # For example:
    width = max(1, int(width * opacity))
    
    # ... existing code ... 

def draw_motion_blur(canvas, points, num_trails, decay, color, width, tags):
    """Draw motion blur trails for smoother animation"""
    for i in range(num_trails):
        # Calculate trail opacity and width
        trail_opacity = (1 - (i / num_trails)) * decay
        trail_width = max(1, width * trail_opacity)
        
        # Skip nearly invisible trails
        if trail_opacity < 0.1:
            continue
            
        # Apply opacity to color
        r = int(color[1:3], 16)
        g = int(color[3:5], 16)
        b = int(color[5:7], 16)
        trail_color = f"#{r:02x}{g:02x}{b:02x}"
        
        # Draw the trail
        canvas.create_line(points, fill=trail_color, width=trail_width, tags=tags) 

def draw_soft_particle(canvas, x, y, radius, color, falloff=0.7, tags="particle"):
    """Draw a soft-edged particle with realistic glow"""
    # Draw multiple concentric circles with decreasing opacity
    for i in range(5):
        opacity = 1.0 * (1 - i * 0.2) * falloff
        if opacity < 0.1:
            continue
            
        size = radius * (1 + i * 0.25)
        canvas.create_oval(
            x - size, y - size,
            x + size, y + size,
            fill="" if i > 0 else color,
            outline=color,
            width=1,
            tags=tags
        ) 