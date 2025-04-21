#!/usr/bin/env python
# =================================
# Sound viewer
# ------------
# [May 2020] - Mina PECHEUX
#
# Based on the work by Yu-Jie Lin
# (Public Domain)
# Github: https://gist.github.com/manugarri/1c0fcfe9619b775bb82de0790ccb88da

import wave
import click
import pygame
import os
from subttile import voice
import threading
import time

from compute import plt, compute, WIDTH, HEIGHT, \
 SAMPLE_SIZE, CHANNELS, RATE, FPS

@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.argument('filename', type=str)
@click.option('-m', '--method', help='Method to use for the video processing', required=True,
              type=click.Choice(['bars', 'spectrum', 'wave', 'rain'], case_sensitive=False))
@click.option('-c', '--color', help='An hex color or "hue_rotate" to auto-update the color throughout the film',
              type=str, default='hue_rotate', show_default=True)
@click.option('--output/--no-output', help='Whether to save the result in a file or display it directly',
              default=False, show_default=True)
@click.option('--play/--no-play', help='Whether to play audio while visualizing',
              default=False, show_default=True)
@click.option('--subtitle/--no-subtitle', help='Whether to display subtitles while visualizing',
              default=False, show_default=True)
@click.option('--subtitle-text', help='Text to display as subtitles (used with --subtitle option)',
              type=str, default=None)
@click.option('--subtitle-font', help='Font for subtitles',
              type=str, default='sans-serif')
@click.option('--subtitle-color', help='Color for subtitles',
              type=str, default='white')
@click.option('--subtitle-size', help='Font size for subtitles',
              type=int, default=14)
@click.option('--subtitle-pos-x', help='X position for subtitles (0-1)',
              type=float, default=0.5)
@click.option('--subtitle-pos-y', help='Y position for subtitles (0-1)',
              type=float, default=0.95)
@click.option('--subtitle-timing', help='Adjust subtitle timing (ms, positive = delay, negative = advance)',
              type=int, default=0)
@click.option('--keep-open/--no-keep-open', help='Whether to keep the visualization window open after playback',
              default=False, show_default=True)
@click.option('--save-audio/--no-save-audio', help='Whether to save audio when processing text input',
              default=False, show_default=True)
def main(filename, method, color, output, play, subtitle, subtitle_text, 
         subtitle_font, subtitle_color, subtitle_size, subtitle_pos_x, subtitle_pos_y, 
         subtitle_timing, keep_open, save_audio):
  dpi = plt.rcParams['figure.dpi']
  plt.rcParams['savefig.dpi'] = 300
  plt.rcParams['figure.figsize'] = (1.0 * WIDTH / dpi, 1.0 * HEIGHT / dpi)

  # Process input and handle text-to-speech if needed
  wav_filename = None
  subtitle_data = None
  temp_audio_file = None
  
  # Create subtitle configuration
  subtitle_config = {
    'font_family': subtitle_font,
    'font_color': subtitle_color,
    'font_size': subtitle_size,
    'pos_x': subtitle_pos_x,
    'pos_y': subtitle_pos_y,
    'timing_adjustment': subtitle_timing,
    'force_continue': not play or keep_open  # Force continue if not playing audio or keep-open is enabled
  }
  
  # Check if input is a file or text for TTS
  if os.path.exists(filename):
    # It's an existing file
    wav_filename = filename if filename.lower().endswith('.wav') else filename + '.wav'
  elif os.path.exists(filename + '.wav'):
    # The .wav extension was omitted but file exists
    wav_filename = filename + '.wav'
  elif subtitle:
    # Input is text for TTS
    final_subtitle_text = subtitle_text if subtitle_text else filename
    print(f"Generating audio from text: {filename}")
    wav_filename, subtitle_data = voice(filename, subtitle_config, save_audio=save_audio)
    # If not saving audio, mark the file for cleanup
    if not save_audio and wav_filename and os.path.exists(wav_filename):
      temp_audio_file = wav_filename
  else:
    # Regular file handling
    wav_filename = filename if filename.lower().endswith('.wav') else filename + '.wav'
    
  # Check if file exists after processing
  if not os.path.exists(wav_filename):
    print(f"Error: File '{wav_filename}' not found.")
    return

  wf = wave.open(wav_filename, 'rb')
  # Print file info
  print(f"Audio file info: {wf.getnchannels()} channels, {wf.getsampwidth()} bytes per sample, {wf.getframerate()} Hz")

  fig = plt.figure(facecolor='black', edgecolor='black')

  # For TTS with subtitles, we already have subtitle_data
  # Otherwise, create subtitle text from parameters
  if subtitle and not subtitle_data and subtitle_text:
    # Simple subtitle data structure for static text
    subtitle_data = [{
      'start': 0,
      'end': float('inf'),  # Show for entire duration
      'text': subtitle_text
    }]

  if play:
    pygame.mixer.init(frequency=RATE)
    pygame.mixer.music.load(wav_filename)
    
    # Add timing information to subtitle_config for synchronization
    if subtitle_config:
      subtitle_config['playback_start_time'] = time.time()
    
    pygame.mixer.music.play()

  # Pass subtitle data and config to compute
  ani = compute(method, color, fig, wf, subtitle_data, subtitle_config if subtitle else subtitle_config)
  if ani is None:
    wf.close()
    if play:
      pygame.mixer.music.stop()
      pygame.mixer.quit()
    # Clean up temporary audio file if it exists
    if temp_audio_file and os.path.exists(temp_audio_file):
      try:
        os.remove(temp_audio_file)
        print(f"Removed temporary audio file: {temp_audio_file}")
      except Exception as e:
        print(f"Error removing temporary audio file: {e}")
    return

  if output:
    output_filename = filename if filename.lower().endswith('.wav') else filename + '.mp4'
    if output_filename.lower().endswith('.wav'):
      output_filename = output_filename[:-4] + '.mp4'
    ani.save(output_filename, fps=FPS, savefig_kwargs={'facecolor':'black'})
  else:
    plt.show(block=keep_open)  # Use block=True when keep-open is enabled to prevent window from closing

  wf.close()
  if play:
    pygame.mixer.music.stop()
    pygame.mixer.quit()
    
  # Clean up temporary audio file if it exists
  if temp_audio_file and os.path.exists(temp_audio_file):
    try:
      os.remove(temp_audio_file)
      print(f"Removed temporary audio file: {temp_audio_file}")
    except Exception as e:
      print(f"Error removing temporary audio file: {e}")

if __name__ == '__main__':
  try:
    main()
  except Exception as e:
    import traceback
    print(f"Error: {e}")
    traceback.print_exc()


# This Code Loop is a simple example of how to use the main function for input teks.

