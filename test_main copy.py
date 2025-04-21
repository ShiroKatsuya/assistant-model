import multiprocessing
import queue
import threading
import time
import traceback
import os
import sys
import pygame
import matplotlib
# Set the backend before importing pyplot
matplotlib.use('TkAgg')  # Use TkAgg backend which works better with multiprocessing
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from subttile import voice
import numpy as np
import wave
from compute import compute, WIDTH, HEIGHT, RATE, FPS
from display_ai_voice import main
from click.testing import CliRunner
import io

# Global variables to track the active visualization
active_visualization = None
current_text = None
# Queue for communication between threads
vis_queue = queue.Queue()
# Control flags
visualization_running = False
animation_instance = None
ani = None
fig = None
wave_obj = None

def process_audio(text):
    """Process audio generation in a separate thread"""
    try:
        # Generate audio in memory with TTS
        audio_buffer, subtitle_data = voice(text, save_audio=False)
        
        if audio_buffer:            
            # Put results in queue for main thread to use
            vis_queue.put({
                'audio_buffer': audio_buffer,
                'subtitle_data': subtitle_data,
                'text': text
            })
            return True
        else:
            print(f"Failed to generate audio for: '{text}'")
            return False
    except Exception as e:
        print(f"Audio processing error: {e}")
        traceback.print_exc()
        return False

def update_frame(*args):
    """Animation update function for Matplotlib"""
    global wave_obj, animation_instance, current_text
    
    try:
        # Check for new data - non-blocking
        try:
            data = vis_queue.get_nowait()
            
            # We have new data - update visualization
            audio_buffer = data['audio_buffer']
            subtitle_data = data['subtitle_data']
            current_text = data['text']
            
            # Stop any previous playback
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
            
            # Close previous wave object if open
            if wave_obj is not None:
                wave_obj.close()
                
            # Clear the figure
            plt.clf()
            
            # Open wave file from buffer for visualization
            wave_obj = wave.open(audio_buffer, 'rb')
            print(f"Audio info: {wave_obj.getnchannels()} channels, {wave_obj.getsampwidth()} bytes per sample, {wave_obj.getframerate()} Hz")
            
            # Create subtitle configuration
            subtitle_config = {
                'font_family': 'sans-serif',
                'font_color': 'white',
                'font_size': 14,
                'pos_x': 0.5,
                'pos_y': 0.95,
                'timing_adjustment': 0,
                'force_continue': True,
                'playback_start_time': time.time()
            }
            
            # Make a temporary copy of the buffer for pygame playback
            audio_copy = io.BytesIO(audio_buffer.getvalue())
            audio_copy.seek(0)
            
            # Play the audio
            pygame.mixer.music.load(audio_copy)
            pygame.mixer.music.play()
            
            # Create new visualization using compute function
            animation_instance = compute('bars', 'hue_rotate', fig, wave_obj, subtitle_data, subtitle_config)
            
        except queue.Empty:
            # No new data, just continue with current visualization
            pass
            
    except Exception as e:
        print(f"Frame update error: {e}")
        traceback.print_exc()

def setup_visualization():
    """Setup visualization in the main thread"""
    global fig, ani, visualization_running
    
    try:
        # Initialize pygame mixer for audio playback
        if not pygame.mixer.get_init():
            pygame.mixer.init(frequency=RATE)
        
        # Initialize matplotlib figure
        dpi = plt.rcParams['figure.dpi']
        plt.rcParams['savefig.dpi'] = 300
        plt.rcParams['figure.figsize'] = (1.0 * WIDTH / dpi, 1.0 * HEIGHT / dpi)
        fig = plt.figure(facecolor='black', edgecolor='black')
        
        # Create initial empty animation that will be updated via the queue
        ani = animation.FuncAnimation(
            fig, 
            update_frame, 
            interval=50,  # Update interval in milliseconds
            blit=False    # Redraw the entire figure, needed for text updates
        )
        
        visualization_running = True
        return True
        
    except Exception as e:
        print(f"Setup visualization error: {e}")
        traceback.print_exc()
        return False

def start_visualization(text):
    """Start or update visualization with the given text input"""
    global visualization_running, current_text
    
    # Ensure text is provided and non-empty
    if not text or text.strip() == "":
        print("Error: Text cannot be empty")
        return False

    # Process the audio in a separate thread
    current_text = text
    audio_thread = threading.Thread(target=process_audio, args=(text,))
    audio_thread.daemon = True
    audio_thread.start()
    
    return True

def stop_visualization():
    """Stop the visualization"""
    global visualization_running, wave_obj
    
    visualization_running = False
    
    # Stop audio playback
    if pygame.mixer.get_init():
        pygame.mixer.music.stop()
        pygame.mixer.quit()
    
    # Close wave object if open
    if wave_obj is not None:
        wave_obj.close()
        wave_obj = None
    
    # Close all matplotlib figures
    plt.close('all')
    
    print("Visualization stopped")

if __name__ == "__main__":
    # This ensures multiprocessing works correctly on Windows
    multiprocessing.freeze_support()
    
    print("Starting sound visualization system with single window...")
    print("You can enter new input at any time to update the visualization.")
    
    # Setup the visualization in the main thread
    if not setup_visualization():
        print("Failed to setup visualization. Exiting.")
        sys.exit(1)
        
    # Start matplotlib in non-blocking mode
    plt.ion()
    plt.show(block=False)
    
    # Main input loop
    try:
        while visualization_running:
            # Show status of visualization
            if current_text:
                print(f"\nActive visualization: '{current_text}'")
            
            user_input = input("\nEnter text to visualize (or 'exit' to quit): ")
            
            if user_input.lower() == 'exit':
                # Stop visualization
                stop_visualization()
                break
                
            # Start or update visualization
            print(f"Processing: '{user_input}'")
            start_visualization(user_input)
            
            # Allow some time for the GUI to update
            plt.pause(0.1)
            
    except KeyboardInterrupt:
        print("\nExiting program...")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        traceback.print_exc()
    finally:
        # Clean up
        stop_visualization()
        print("Program exited.")