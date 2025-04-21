#!/usr/bin/env python
# =================================
# Sound viewer
# ------------
# [May 2020] - Mina PECHEUX
#
# Based on the work by Yu-Jie Lin
# (Public Domain)
# Github: https://gist.github.com/manugarri/1c0fcfe9619b775bb82de0790ccb88da

import struct
import time

import matplotlib.animation as animation
import matplotlib.pyplot as plt
from matplotlib import collections as mc
import numpy as np
import colorsys

TITLE = ''

WIDTH = 1280
HEIGHT = 720

SAMPLE_SIZE = 2
CHANNELS = 2
RATE = 44100
FPS = 24.0
nFFT = 512

WINDOW = 0.5  # in seconds

# ========================
# UTILS
# ========================
def hex_to_rgb(hex):
  hex = hex.lstrip('#')
  return tuple(int(hex[i:i+2], 16) / 255 for i in (0, 2, 4))

# ========================
# INITIALIZATION FUNCTIONS
# ========================
def init_color(color):
  if color == 'hue_rotate':
    return colorsys.hsv_to_rgb(0.0, 1.0, 1.0)
  else:
    return hex_to_rgb(color)

def init_bars(lines, color):
  color = init_color(color)
  lines.set_color(color)
  return lines,

def init_spectrum(line, color):
  color = init_color(color)
  line.set_ydata(np.zeros(nFFT - 1))
  line.set_color(color)
  return line,

def init_wave(lines, color, x, MAX_y):
  color = init_color(color)
  lines[0][0].set_ydata(np.zeros(len(x)))
  lines[0][0].set_color(color)
  lines[1][0].set_ydata(MAX_y * np.ones(len(x)))
  lines[1][0].set_color(color)

  return lines,

def init_rain(circles, color):
  color = init_color(color)
  for circle in circles:
    circle.set_color(color)
  return circles,


# ========================
# ANIMATION FUNCTIONS
# ========================
def update_subtitle_text(subtitle, subtitle_data, wf, subtitle_config=None):
    if not subtitle or not subtitle_data:
        return
        
    # Calculate the current time in ms based on audio position
    current_time_ms = 0
    
    # If we have playback timing information, use that for better sync
    if subtitle_config and 'playback_start_time' in subtitle_config:
        # Calculate time since playback started
        elapsed_time = time.time() - subtitle_config['playback_start_time']
        current_time_ms = elapsed_time * 1000
        
        # Apply timing adjustment if specified
        if 'timing_adjustment' in subtitle_config:
            current_time_ms += subtitle_config['timing_adjustment']
            
        # Debug timing (uncomment if needed to debug)
        # print(f"Playback time: {current_time_ms:.2f}ms")
    else:
        # Fallback to file position (less accurate)
        current_time_ms = (wf.tell() / float(wf.getframerate())) * 1000
    
    # Find the subtitle that should be displayed at the current time
    current_text = ""
    current_sub_idx = -1
    
    for idx, sub in enumerate(subtitle_data):
        if sub['start'] <= current_time_ms < sub['end']:
            current_text = sub['text']
            current_sub_idx = idx
            break
    
    # Update the subtitle text
    subtitle.set_text(current_text)
    
    # Store the current subtitle index for debugging or adjustment
    if subtitle_config is not None:
        subtitle_config['current_sub_idx'] = current_sub_idx

def check_audio_playing(subtitle_config=None):
    """Check if audio is still playing"""
    try:
        import pygame
        if pygame.mixer.get_init() and pygame.mixer.music.get_busy():
            return True
        elif subtitle_config and subtitle_config.get('force_continue', False):
            return True
        return False
    except (ImportError, AttributeError):
        # If pygame isn't available or initialized, fallback to always continue
        if subtitle_config and subtitle_config.get('force_continue', False):
            return True
        return False

def animate_bars(i, lines, lines_x, wf, color, max_y, bar_min, subtitle=None, subtitle_data=None, subtitle_config=None):
  # Check if audio is still playing - stop animation if not
  if not check_audio_playing(subtitle_config):
      plt.close()
      return lines,
      
  N = (int((i + 1) * RATE / FPS) - wf.tell()) // nFFT
  if not N:
    return lines,
  N *= nFFT
  data = wf.readframes(N)
  # print('{:5.1f}% - V: {:5,d} - A: {:10,d} / {:10,d}'.format(
  #   100.0 * wf.tell() / wf.getnframes(), i, wf.tell(), wf.getnframes()
  # ))

  # Unpack data, LRLRLR...
  y = np.array(struct.unpack("%dh" % (len(data) / SAMPLE_SIZE), data)) / max_y
  y_L = y[::2]
  y_R = y[1::2]

  Y_L = np.fft.fft(y_L, nFFT)
  Y_R = np.fft.fft(y_R, nFFT)

  # Sewing FFT of two channels together, DC part uses right channel's
  Y = abs(np.hstack((Y_L[-nFFT // 2:-1], Y_R[:nFFT // 2])))
  Y_v = Y[::2]

  lines_data = []
  for i, x in enumerate(lines_x):
    lines_data.append([(x, min(-bar_min, -Y_v[i])), (x, max(bar_min, Y_v[i]))])

  lines.set_segments(lines_data)
  if color == 'hue_rotate':
    lines.set_color(colorsys.hsv_to_rgb(wf.tell() / float(wf.getnframes()), 1.0, 1.0))

  # Update subtitle if provided
  update_subtitle_text(subtitle, subtitle_data, wf, subtitle_config)
      
  return lines,

def animate_spectrum(i, line, wf, color, max_y, subtitle=None, subtitle_data=None, subtitle_config=None):
  # Check if audio is still playing - stop animation if not
  if not check_audio_playing(subtitle_config):
      plt.close()
      return line,
      
  N = (int((i + 1) * RATE / FPS) - wf.tell()) // nFFT
  if not N:
    return line,
  N *= nFFT
  data = wf.readframes(N)
  print('{:5.1f}% - V: {:5,d} - A: {:10,d} / {:10,d}'.format(
    100.0 * wf.tell() / wf.getnframes(), i, wf.tell(), wf.getnframes()
  ))

  # Unpack data, LRLRLR...
  y = np.array(struct.unpack("%dh" % (len(data) / SAMPLE_SIZE), data)) / max_y
  y_L = y[::2]
  y_R = y[1::2]

  Y_L = np.fft.fft(y_L, nFFT)
  Y_R = np.fft.fft(y_R, nFFT)

  # Sewing FFT of two channels together, DC part uses right channel's
  Y = abs(np.hstack((Y_L[-nFFT // 2:-1], Y_R[:nFFT // 2])))
  if color == 'hue_rotate':
    line.set_color(colorsys.hsv_to_rgb(wf.tell() / float(wf.getnframes()), 1.0, 1.0))

  line.set_ydata(Y)
  
  # Update subtitle if provided
  update_subtitle_text(subtitle, subtitle_data, wf, subtitle_config)
      
  return line,

def animate_wave(i, lines, wf, color, x, MAX_y, subtitle=None, subtitle_data=None, subtitle_config=None):
  # Check if audio is still playing - stop animation if not
  if not check_audio_playing(subtitle_config):
      plt.close()
      return lines,
      
  N = (int((i+1) * RATE / FPS) - wf.tell())
  if not N:
    return lines,
  data = wf.readframes(N)
  y = np.array(struct.unpack("%dh" % (len(data) / SAMPLE_SIZE), data))
  print('{:5.1f}% - V: {:5,d} - A: {:10,d} / {:10,d}'.format(
    100.0 * wf.tell() / wf.getnframes(), i, wf.tell(), wf.getnframes()
  ))

  if len(y) != 2 * len(x):
    return lines,

  # Split the data into channels
  channels = [[] for channel in range(CHANNELS)]
  for index, datum in enumerate(y):
      channels[index%len(channels)].append(datum)

  if color == 'hue_rotate':
    color = (colorsys.hsv_to_rgb(wf.tell() / float(wf.getnframes()), 1.0, 1.0))
    lines[0][0].set_color(color)
    lines[1][0].set_color(color)
  lines[0][0].set_ydata(channels[0])
  lines[1][0].set_ydata([c + MAX_y for c in channels[1]])

  # Update subtitle if provided
  update_subtitle_text(subtitle, subtitle_data, wf, subtitle_config)
      
  return lines,

def animate_rain(i, circles, wf, color, max_y, max_point_size, min_amp_ratio, subtitle=None, subtitle_data=None, subtitle_config=None):
  # Check if audio is still playing - stop animation if not
  if not check_audio_playing(subtitle_config):
      plt.close()
      return circles,
      
  N = (int((i + 1) * RATE / FPS) - wf.tell()) // nFFT
  if not N:
    return circles,
  N *= nFFT
  data = wf.readframes(N)
  print('{:5.1f}% - V: {:5,d} - A: {:10,d} / {:10,d}'.format(
    100.0 * wf.tell() / wf.getnframes(), i, wf.tell(), wf.getnframes()
  ))

  # Unpack data, LRLRLR...
  y = np.array(struct.unpack("%dh" % (len(data) / SAMPLE_SIZE), data)) / max_y
  Y = abs(np.fft.fft(y, nFFT))
  Y_max = np.max(Y)

  if Y_max == 0.0:
    return circles,

  if color == 'hue_rotate':
    color = colorsys.hsv_to_rgb(wf.tell() / float(wf.getnframes()), 1.0, 1.0)
    for circle in circles:
      circle.set_color(color)
  for i, circle in enumerate(circles):
    if (Y[i] < min_amp_ratio):
      circle.set_radius(0.05)
    circle.set_radius(Y[i] / Y_max * max_point_size)

  # Update subtitle if provided
  update_subtitle_text(subtitle, subtitle_data, wf, subtitle_config)
      
  return circles,


# ========================
# COMPUTE FUNCTIONS
# ========================
def compute_bars(fig, wf, color, subtitle_data=None, subtitle_config=None):
  bar_step = 2
  bar_min = 0.05

  # Frequency range
  x_f = 1.0 * np.arange(-nFFT / 2 + 1, nFFT / 2) / nFFT * RATE
  x_range = x_f[-1] - x_f[0]
  ax = fig.add_subplot(111, title=TITLE, xlim=(x_f[0], x_f[-1]),
                       ylim=(-np.pi * nFFT ** 2 / RATE, np.pi * nFFT ** 2 / RATE))
  ax.set_yscale('symlog', linthresh=nFFT ** 0.5)
  plt.axis('off')
  plt.subplots_adjust(left=0, bottom=0.1, right=1, top=0.9, wspace=0, hspace=0.1)

  lines_data = []
  lines_x = []
  for i in range(-nFFT // (bar_step * 2), nFFT // (bar_step * 2)):
    ix = i * bar_step * x_range / float(nFFT)
    lines_x.append(ix)
    lines_data.append([(ix, -bar_min), (ix, bar_min)])

  lines = mc.LineCollection(lines_data, linewidths=2)
  ax.add_collection(lines)
  
  # Add subtitle text
  subtitle = None
  if subtitle_data:
    pos_x = subtitle_config.get('pos_x', 0.5) if subtitle_config else 0.5
    pos_y = subtitle_config.get('pos_y', 0.95) if subtitle_config else 0.95
    font_size = subtitle_config.get('font_size', 14) if subtitle_config else 14
    font_color = subtitle_config.get('font_color', 'white') if subtitle_config else 'white'
    font_family = subtitle_config.get('font_family', 'sans-serif') if subtitle_config else 'sans-serif'
    
    subtitle = ax.text(pos_x, pos_y, "", ha='center', va='top', 
                     transform=ax.transAxes, color=font_color, fontsize=font_size,
                     family=font_family,
                     bbox=dict(boxstyle="round", ec="black", fc="black", alpha=0.8))
  
  max_y = 2.0 ** (SAMPLE_SIZE * 8 - 1)
  
  return animation.FuncAnimation(
    fig, animate_bars, int(wf.getnframes() / RATE * FPS),
    init_func=lambda: init_bars(lines, color),
    fargs=(lines, lines_x, wf, color, max_y, bar_min, subtitle, subtitle_data, subtitle_config),
    interval=1000.0 / FPS, blit=False
  )

def compute_spectrum(fig, wf, color, subtitle_data=None, subtitle_config=None):
  # Frequency range
  x_f = 1.0 * np.arange(-nFFT / 2 + 1, nFFT / 2) / nFFT * RATE
  ax = fig.add_subplot(111, title=TITLE, xlim=(x_f[0], x_f[-1]),
                       ylim=(0, 2 * np.pi * nFFT ** 2 / RATE))
  ax.set_yscale('symlog', linthresh=nFFT ** 0.5)
  plt.axis('off')
  plt.subplots_adjust(left=0, bottom=0.1, right=1, top=0.9, wspace=0, hspace=0.1)

  line, = ax.plot(x_f, np.zeros(nFFT - 1))
  
  # Add subtitle text
  subtitle = None
  if subtitle_data:
    pos_x = subtitle_config.get('pos_x', 0.5) if subtitle_config else 0.5
    pos_y = subtitle_config.get('pos_y', 0.95) if subtitle_config else 0.95
    font_size = subtitle_config.get('font_size', 14) if subtitle_config else 14
    font_color = subtitle_config.get('font_color', 'white') if subtitle_config else 'white'
    font_family = subtitle_config.get('font_family', 'sans-serif') if subtitle_config else 'sans-serif'
    
    subtitle = ax.text(pos_x, pos_y, "", ha='center', va='top', 
                     transform=ax.transAxes, color=font_color, fontsize=font_size,
                     family=font_family,
                     bbox=dict(boxstyle="round", ec="black", fc="black", alpha=0.8))
  
  max_y = 2.0 ** (SAMPLE_SIZE * 8 - 1)
  
  return animation.FuncAnimation(
    fig, animate_spectrum, int(wf.getnframes() / RATE * FPS),
    init_func=lambda: init_spectrum(line, color),
    fargs=(line, wf, color, max_y, subtitle, subtitle_data, subtitle_config),
    interval=1000.0 / FPS, blit=False
  )

def compute_wave(fig, wf, color, subtitle_data=None, subtitle_config=None):
  # Time range
  N = (int(1 * RATE / FPS) - wf.tell())
  x = np.linspace(0, WINDOW, N)
  MAX_y = 30000

  ax = fig.add_subplot(111, title=TITLE, xlim=(x[0], x[-1]),
                       ylim=(-MAX_y, MAX_y * CHANNELS))
  ax.axis('off')
  plt.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=0, hspace=0)

  lines = []
  lines.append(ax.plot(x, np.zeros(len(x)), linewidth=2))
  lines.append(ax.plot(x, MAX_y * np.ones(len(x)), linewidth=2))
  
  # Add subtitle text
  subtitle = None
  if subtitle_data:
    pos_x = subtitle_config.get('pos_x', 0.5) if subtitle_config else 0.5
    pos_y = subtitle_config.get('pos_y', 0.95) if subtitle_config else 0.95
    font_size = subtitle_config.get('font_size', 14) if subtitle_config else 14
    font_color = subtitle_config.get('font_color', 'white') if subtitle_config else 'white'
    font_family = subtitle_config.get('font_family', 'sans-serif') if subtitle_config else 'sans-serif'
    
    subtitle = ax.text(pos_x, pos_y, "", ha='center', va='top', 
                     transform=ax.transAxes, color=font_color, fontsize=font_size,
                     family=font_family,
                     bbox=dict(boxstyle="round", ec="black", fc="black", alpha=0.8))

  return animation.FuncAnimation(
    fig, animate_wave, int(wf.getnframes() / RATE * FPS),
    init_func=lambda: init_wave(lines, color, x, MAX_y), 
    fargs=(lines, wf, color, x, MAX_y, subtitle, subtitle_data, subtitle_config),
    interval=1000.0 / FPS, blit=False
  )

def compute_rain(fig, wf, color, subtitle_data=None, subtitle_config=None):
  max_point_size = 7
  min_amp_ratio = None
  col_count = 8

  # Frequency range
  max_y = nFFT * HEIGHT / WIDTH
  ax = fig.add_subplot(111, title=TITLE, xlim=(0, nFFT), ylim=(0, max_y))
  min_amp_ratio = max_y * 0.2

  # ax.set_yscale('symlog', linthreshy=nFFT ** 0.5)
  plt.axis('off')
  plt.subplots_adjust(left=0.01, bottom=0.01, right=0.99, top=0.99, wspace=0, hspace=0)

  circles = []

  cx, cy = 0, 0
  cols = float(nFFT / col_count)
  x_offset = max_point_size * 2.0
  xstep = ((WIDTH - x_offset * 2) / ((cols + 1.0) * max_point_size / (max_point_size / 2.5)))
  ystep = max_y / col_count
  for _ in range(nFFT):
    ix, iy = cx * xstep, cy * ystep
    circles.append(plt.Circle((ix + x_offset, iy + ystep / 2), 0.01))
    cy += 1
    if cy == col_count:
      cy = 0
      cx += 1

  for circle in circles:
    ax.add_patch(circle)
    
  # Add subtitle text
  subtitle = None
  if subtitle_data:
    pos_x = subtitle_config.get('pos_x', 0.5) if subtitle_config else 0.5
    pos_y = subtitle_config.get('pos_y', 0.95) if subtitle_config else 0.95
    font_size = subtitle_config.get('font_size', 14) if subtitle_config else 14
    font_color = subtitle_config.get('font_color', 'white') if subtitle_config else 'white'
    font_family = subtitle_config.get('font_family', 'sans-serif') if subtitle_config else 'sans-serif'
    
    subtitle = ax.text(pos_x, pos_y, "", ha='center', va='top', 
                     transform=ax.transAxes, color=font_color, fontsize=font_size,
                     family=font_family,
                     bbox=dict(boxstyle="round", ec="black", fc="black", alpha=0.8))

  return animation.FuncAnimation(
    fig, animate_rain, int(wf.getnframes() / RATE * FPS),
    init_func=lambda: init_rain(circles, color),
    fargs=(circles, wf, color, max_y, max_point_size, min_amp_ratio, subtitle, subtitle_data, subtitle_config),
    interval=1000.0 / FPS, blit=False
  )

# global computation function
def compute(method, color, fig, wf, subtitle_data=None, subtitle_config=None):
  if method == 'bars':
    return compute_bars(fig, wf, color, subtitle_data, subtitle_config)
  elif method == 'spectrum':
    return compute_spectrum(fig, wf, color, subtitle_data, subtitle_config)
  elif method == 'wave':
    return compute_wave(fig, wf, color, subtitle_data, subtitle_config)
  elif method == 'rain':
    return compute_rain(fig, wf, color, subtitle_data, subtitle_config)