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
audio_thread = None
playback_start_time = None
audio_duration = None
# Event for signaling visualization completion
visualization_complete_event = threading.Event()

def process_audio(text):
    """Process audio generation in a separate thread"""
    global playback_start_time
    
    try:
        print(f"Starting audio processing for: '{text}'")
        
        # Generate audio in memory with TTS
        try:
            # Using a small try/catch block to handle voice generation separately
            audio_buffer, subtitle_data = voice(text, save_audio=False)
        except Exception as voice_error:
            print(f"Voice generation error: {voice_error}")
            vis_queue.put({
                'error': f"Failed to generate voice: {str(voice_error)}",
                'text': text
            })
            # Signal completion on error for faster thread transition
            return False
        
        if audio_buffer:            
            # Put results in queue for main thread to use
            vis_queue.put({
                'audio_buffer': audio_buffer,
                'subtitle_data': subtitle_data,
                'text': text
            })
            print("Audio generation complete, visualization will start soon")
            
            # Wait to ensure visualization starts, with reduced timeout
            timeout = 10  # Reduced timeout for faster thread transition
            start_time = time.time()
            while playback_start_time is None and time.time() - start_time < timeout:
                time.sleep(0.1)
                
            if playback_start_time is None:
                print("Visualization did not start after audio generation")
                # Return anyway to allow thread to complete
                return False
                
            return True
        else:
            print(f"Failed to generate audio for: '{text}'")
            vis_queue.put({
                'error': "Failed to generate audio (empty buffer)",
                'text': text
            })
            return False
    except Exception as e:
        print(f"Audio processing error: {e}")
        traceback.print_exc()
        # Put an error message in the queue so the main thread knows about the failure
        vis_queue.put({
            'error': str(e),
            'text': text
        })
        return False

def update_frame(*args):
    """Animation update function for Matplotlib"""
    global wave_obj, animation_instance, current_text, playback_start_time, audio_duration, audio_thread
    
    try:
        # Keep UI responsive by processing events
        if plt.fignum_exists(plt.gcf().number):
            plt.gcf().canvas.flush_events()
        
        # Check if audio is finished playing but visualization is still running
        if playback_start_time and audio_duration:
            current_time = time.time()
            if current_time - playback_start_time > audio_duration and pygame.mixer.get_init() and pygame.mixer.music.get_busy() == 0:
                # Audio and subtitles have finished
                if audio_thread and audio_thread.is_alive():
                    audio_thread = None
                playback_start_time = None
                audio_duration = None
                
        # Check for new data - non-blocking
        try:
            data = vis_queue.get_nowait()
            
            # Check if there was an error in processing
            if 'error' in data:
                print(f"Error in audio processing: {data['error']}")
                # Display error message on visualization
                plt.clf()
                plt.figtext(0.5, 0.5, f"Error: {data['error']}", 
                           horizontalalignment='center', color='red', fontsize=14)
                plt.draw()
                return
            
            # We have new data - update visualization
            audio_buffer = data['audio_buffer']
            subtitle_data = data['subtitle_data']
            current_text = data['text']
            
            # Stop any previous playback
            if pygame.mixer.get_init() and pygame.mixer.music.get_busy():
                pygame.mixer.music.fadeout(500)  # Gentle fadeout
                time.sleep(0.6)  # Wait for fadeout
            
            # Close previous wave object if open
            if wave_obj is not None:
                try:
                    wave_obj.close()
                except Exception as e:
                    print(f"Error closing wave object: {e}")
                wave_obj = None
                
            # Clear the figure
            plt.clf()
            
            try:
                # Open wave file from buffer for visualization
                wave_obj = wave.open(audio_buffer, 'rb')
                
                # Calculate audio duration
                frames = wave_obj.getnframes()
                rate = wave_obj.getframerate()
                audio_duration = frames / float(rate)
                playback_start_time = time.time()
                
                # Create subtitle configuration
                subtitle_config = {
                    'font_family': 'sans-serif',
                    'font_color': 'white',
                    'font_size': 14,
                    'pos_x': 0.5,
                    'pos_y': 0.95,
                    'timing_adjustment': 0,
                    'force_continue': True,
                    'playback_start_time': playback_start_time
                }
                
                # Make a temporary copy of the buffer for pygame playback
                audio_copy = io.BytesIO(audio_buffer.getvalue())
                audio_copy.seek(0)
                
                # Process GUI events before playing to ensure responsiveness
                if plt.fignum_exists(plt.gcf().number):
                    plt.gcf().canvas.draw_idle()
                    plt.gcf().canvas.flush_events()
                
                # Initialize pygame if needed
                if not pygame.mixer.get_init():
                    pygame.mixer.init(frequency=RATE, buffer=4096)  # Increased buffer size
                
                # Play the audio
                pygame.mixer.music.load(audio_copy)
                pygame.mixer.music.play()
                
                # Create new visualization using compute function
                animation_instance = compute('bars', 'hue_rotate', fig, wave_obj, subtitle_data, subtitle_config)
            except Exception as viz_error:
                print(f"Error initializing visualization: {viz_error}")
                traceback.print_exc()
                plt.clf()
                plt.figtext(0.5, 0.5, f"Visualization error: {str(viz_error)}", 
                           horizontalalignment='center', color='red', fontsize=14)
                plt.draw()
                playback_start_time = None
                
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
        
        # Only create a new figure if one doesn't exist already
        if fig is None:
            # Set matplotlib to be more responsive
            plt.rcParams['animation.html'] = 'html5'
            plt.rcParams['toolbar'] = 'None'  # Hide the toolbar for cleaner display
            plt.rcParams['figure.autolayout'] = True  # Better layout
            
            # Initialize matplotlib figure
            dpi = plt.rcParams['figure.dpi']
            plt.rcParams['savefig.dpi'] = 300
            plt.rcParams['figure.figsize'] = (1.0 * WIDTH / dpi, 1.0 * HEIGHT / dpi)
            fig = plt.figure(facecolor='black', edgecolor='black')
            
            # Set window title to something descriptive
            fig.canvas.manager.set_window_title('Audio Visualization')
            
            # Create initial empty animation that will be updated via the queue
            ani = animation.FuncAnimation(
                fig, 
                update_frame, 
                interval=50,  # Update interval in milliseconds
                blit=False,   # Redraw the entire figure, needed for text updates
                cache_frame_data=False  # Don't cache frames to avoid memory issues
            )
        
        visualization_running = True
        return True
        
    except Exception as e:
        print(f"Setup visualization error: {e}")
        traceback.print_exc()
        return False

def start_visualization(text):
    """Start or update visualization with the given text input"""
    global visualization_running, current_text, audio_thread, vis_queue, visualization_complete_event
    
    # Clear the visualization completion event
    visualization_complete_event.clear()
    
    # Ensure text is provided and non-empty
    if not text or text.strip() == "":
        print("Error: Text cannot be empty")
        visualization_complete_event.set()  # Signal completion even in case of error
        return False

    # Clear any existing items in visualization queue
    while not vis_queue.empty():
        try:
            vis_queue.get_nowait()
            vis_queue.task_done()
        except queue.Empty:
            break

    # Make sure visualization is ready
    if not visualization_running:
        if not setup_visualization():
            print("Failed to setup visualization")
            visualization_complete_event.set()  # Signal completion even in case of error
            return False
            
    # Process the audio in a separate thread
    current_text = text
    
    # Cancel any existing audio thread
    if audio_thread and audio_thread.is_alive():
        # We can't really cancel the thread, but we'll start a new one
        audio_thread = None
    
    # Start new audio processing thread
    audio_thread = threading.Thread(target=process_audio, args=(text,))
    audio_thread.daemon = True
    audio_thread.start()
    
    # Give thread time to initialize
    time.sleep(0.5)
    
    return True

def cleanup_visualization():
    """Clean up visualization resources without stopping the visualization process completely"""
    global playback_start_time, audio_duration, audio_thread, wave_obj
    
    # Stop audio playback
    if pygame.mixer.get_init() and pygame.mixer.music.get_busy():
        pygame.mixer.music.stop()
    
    # Close wave object if open
    if wave_obj is not None:
        try:
            wave_obj.close()
        except Exception as e:
            print(f"Error closing wave object: {e}")
        wave_obj = None
    
    # Reset timing variables
    playback_start_time = None
    audio_duration = None
    
    # Clean up audio thread if running
    if audio_thread and audio_thread.is_alive():
        # Just detach from it, don't try to join again
        audio_thread = None
    
    # Process any remaining events to keep the visualization responsive
    if plt.fignum_exists(plt.gcf().number):
        for _ in range(5):
            plt.pause(0.1)
            plt.gcf().canvas.flush_events()
    
    print("Visualization resources cleaned up")

def stop_visualization():
    """Stop the visualization completely and clean up all resources"""
    global visualization_running, wave_obj, audio_thread, visualization_complete_event
    
    print("Stopping visualization and cleaning up resources...")
    
    # First clean up resources
    cleanup_visualization()
    
    # Then shut down the visualization system
    visualization_running = False
    
    # Close all matplotlib figures
    plt.close('all')
    
    # Shut down pygame mixer if it's running
    if pygame.mixer.get_init():
        pygame.mixer.quit()
    
    # Make sure to signal completion 
    visualization_complete_event.set()
    
    print("Visualization stopped completely")

def handle_input(user_input):
    """Handle user input for visualization
    
    Args:
        user_input (str): Text to visualize or 'exit' to quit
        
    Returns:
        bool: True if processing continues, False if program should exit
    """
    global current_text, visualization_complete_event
    
    # Check for exit command
    if user_input.lower() == 'exit':
        # Stop visualization
        stop_visualization()
        return False
    
    # Clean up any existing visualization resources before starting a new one
    cleanup_visualization()
    
    # Start or update visualization
    print(f"Processing: '{user_input}'")
    if not start_visualization(user_input):
        visualization_complete_event.set()  # Ensure event is set even on failure
        return False
    
    # Show status of visualization
    if current_text:
        print(f"\nActive visualization: '{current_text}'")
    
    return True

def run_with_inputs(input_text):
    """Run the visualization with a single text input
    
    Args:
        input_text (str): String to visualize
        
    Returns:
        bool: True if completed successfully
    """
    global visualization_running, playback_start_time, audio_thread, visualization_complete_event
    
    # Reset the completion event
    visualization_complete_event.clear()
    
    print("Starting sound visualization system...")
    
    # Setup the visualization in the main thread
    if not setup_visualization():
        print("Failed to setup visualization. Exiting.")
        visualization_complete_event.set()  # Signal completion even in case of error
        return False
        
    # Start matplotlib in non-blocking mode
    plt.ion()
    plt.show(block=False)
    
    # Process the input
    try:
        if visualization_running:
            # Process the input
            if not handle_input(input_text):
                visualization_complete_event.set()  # Signal completion even in case of error
                return False
                
            # Wait for audio playback to start
            audio_started = False
            
            # Wait for audio to start (playback_start_time will be set)
            timeout_start = time.time()
            max_start_wait = 30  # Reduced timeout for audio generation
            
            while not audio_started and time.time() - timeout_start < max_start_wait:
                if playback_start_time is not None:
                    audio_started = True
                plt.pause(0.1)
                
                # Process any GUI events to keep window responsive
                if plt.fignum_exists(plt.gcf().number):
                    plt.gcf().canvas.flush_events()
            
            if not audio_started:
                print("Audio initialization taking longer than expected, continuing to wait...")
                
                # Extended wait time for slow systems
                extended_start_wait = 10  # Reduced extended wait time further
                extended_timeout_start = time.time()
                
                while not audio_started and time.time() - extended_timeout_start < extended_start_wait:
                    if playback_start_time is not None:
                        audio_started = True
                    plt.pause(0.1)
                    if plt.fignum_exists(plt.gcf().number):
                        plt.gcf().canvas.flush_events()
                
                if not audio_started:
                    print("Audio playback initialization failed. Checking audio thread...")
                    
                    # Check if audio thread had errors
                    if audio_thread and audio_thread.is_alive():
                        print("Audio thread is still running - waiting for it to complete")
                        audio_thread.join(timeout=3)  # Reduced timeout
                    
                    visualization_complete_event.set()
                    return False
                
            # Now wait for audio playback to complete
            
            # Wait for the audio to finish playing
            max_playback_wait = 120  # Reduced to 2 minutes maximum playback wait
            playback_timeout_start = time.time()
            
            while pygame.mixer.get_init() and pygame.mixer.music.get_busy() and time.time() - playback_timeout_start < max_playback_wait:
                plt.pause(0.1)
                # Process events to keep window responsive
                if plt.fignum_exists(plt.gcf().number):
                    plt.gcf().canvas.flush_events()
                
            # If we timed out waiting for playback
            if pygame.mixer.get_init() and pygame.mixer.music.get_busy():
                print("Audio playback reached maximum duration, gracefully finishing playback")
                pygame.mixer.music.fadeout(300)  # Reduced fadeout time for faster completion
                time.sleep(0.4)  # Reduced wait for fadeout to complete
                
            # Signal completion BEFORE waiting for audio thread, to allow faster thread transition
            visualization_complete_event.set()
            
            # Make sure audio thread has completed
            if audio_thread and audio_thread.is_alive():
                print("Waiting for audio processing thread to complete...")
                audio_thread.join(timeout=2)  # Reduced timeout
                
            # Add a minimal delay for clean thread transition
            time.sleep(0.2)  # Minimal delay
            
            # Process any remaining events to keep the visualization responsive
            if plt.fignum_exists(plt.gcf().number):
                plt.gcf().canvas.flush_events()
                
            return True
                
    except KeyboardInterrupt:
        print("\nExiting program...")
    except Exception as e:
        print(f"\nAn error occurred in run_with_inputs: {e}")
        traceback.print_exc()
        visualization_complete_event.set()  # Signal completion even in case of error
        return False
    finally:
        # Don't stop visualization between inputs
        # Ensure event is set if not already
        if not visualization_complete_event.is_set():
            visualization_complete_event.set()
        
    return True

if __name__ == "__main__":
    # This ensures multiprocessing works correctly on Windows
    multiprocessing.freeze_support()
    
    # # Usage with a single text input
    # sample_input1 = "halo1"
    # run_with_inputs(sample_input1)

    # sample_input2 = "halo2"
    # run_with_inputs(sample_input2)
    
    # # Clean up after all inputs are processed
    # print("All inputs processed. Cleaning up...")
    # stop_visualization()
    # print("Program exited.")