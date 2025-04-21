import time

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
                 progress_bar.config(value=max(0, progress_bar["value"] - 2)) # Smoother reset (smaller steps)
             else:
                 progress_bar.config(value=0)


    elif status == "Recording in progress...":
        # Calculate progress based on recording duration if available, otherwise use time modulo
        # For now, use a simple time-based phase for visual progress feedback
        recording_phase = (time.time() * 0.1) % 1 # Example: 10-second loop for progress vis
        draw_recording_animation(animation_canvas, width, height, phase=recording_phase)
        if progress_bar:
            # Update progress bar based on the visual phase or actual recording progress
            # Smoother progress updates with smaller increments
            current_value = progress_bar["value"]
            target_value = recording_phase * 100
            increment = (target_value - current_value) * 0.1  # 10% increment toward target for smoothness
            progress_bar.config(value=current_value + increment)

    elif status == "Recording complete":
        # No phase needed for complete animation usually, it might have its own internal time logic
        draw_complete_animation(animation_canvas, width, height)
        if progress_bar:
             # Animate to full or just set to 100?
            if progress_bar["value"] < 100:
                progress_bar.config(value=min(100, progress_bar["value"] + 2)) # Smoother completion with smaller steps
            else:
                 progress_bar.config(value=100)

    # Continue animation loop with higher frame rate
    # 16.7ms is approximately 60fps for smoother animations
    animation_canvas.after(16, lambda: update_animation(status)) # Increased to ~60fps 