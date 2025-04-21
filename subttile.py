import nltk
from gtts import gTTS
import os
import time
import subprocess
from deep_translator import GoogleTranslator
import sys
sys.path.insert(0, 'silero_tts')
from silero_tts import SileroTTS
from concurrent.futures import ThreadPoolExecutor
import tkinter as tk
from pydub import AudioSegment
import speech_recognition as sr
import threading
import re
import tempfile
import uuid
import io

# # Ensure NLTK's Punkt tokenizer is downloaded
# nltk.download('punkt_tab')

# teks = """
#     *Hello, this is a test of the Silero TTS system. It will convert this text into speech and display subtitles in real-time.*
#     *This is a test of the Silero TTS system. It will convert this text into speech and display subtitles in real-time.*
#     """

# # Example usage


def save_audio(teks):

    # Clean filename by removing invalid characters and whitespace
    filename = "".join(c for c in teks if c.isalnum() or c in (' ', '-', '_'))[:50]  # Limit length
    filename = filename.strip().replace(' ', '_')
    if not filename:  # Fallback if filename is empty after cleaning
        filename = "audio"
    
    tts = SileroTTS(
        model_id='v3_en',
        language='en',
        speaker='en_67',  # Using a clearer speaker
        sample_rate=48000,  # Ensuring sample rate does not exceed 48000
        device='cuda',
        put_accent=True,
        put_yo=True,
        num_threads=8  # Optimized number of threads for better processing
    )
    output_path = f"{filename}.wav"
    tts.tts(teks, output_path)
    return output_path


def voice(teks, subtitle_config=None, save_audio=False):
    recognizer = sr.Recognizer()

    print("isis teks", teks)

    tts = SileroTTS(
        model_id='v3_en',
        language='en',
        speaker='en_67',
        sample_rate=48000,
        device='cuda',
        put_accent=True,
        put_yo=True,
        num_threads=8
    )

    """
    Function to convert text to speech and generate subtitles.
    
    Parameters:
    teks (str): Text to be converted to speech.
    subtitle_config (dict, optional): Configuration for subtitle appearance.
    save_audio (bool, optional): Whether to save the audio file to disk.
    
    Returns:
    tuple: (audio_data, subtitles_data) where audio_data is the binary audio data and subtitles_data is a list of dicts with timing and text.
    """
    print("Processing Text-to-Speech with SileroTTS.")

    # Check if user wants to exit
    if teks.lower() == "exit":
        print("Exiting program.")
        return None, None

    # Clean text from special characters
    cleaned_text = re.sub(r"\*(.*?)\*", r"\1", teks)

    # Translate text to English if needed
    translated = GoogleTranslator(source='auto', target='en').translate(cleaned_text)
    print(f"Text to be converted to speech: {translated}")

    # Split translated text into sentences
    sentences = nltk.sent_tokenize(translated)
    print(f"Number of sentences: {len(sentences)}")

    # Generate audio for each sentence and calculate durations
    sentence_audio_segments = []
    sentence_durations = []
    
    for idx, sentence in enumerate(sentences):
        # Create in-memory buffer for audio
        buffer = io.BytesIO()
        
        try:
            # Use a temporary path for Silero TTS, which requires a file path
            temp_path = f"temp_{uuid.uuid4()}.wav"
            tts.tts(sentence, temp_path)
            
            # Read the file into memory immediately and delete it
            with open(temp_path, 'rb') as f:
                buffer.write(f.read())
            os.remove(temp_path)
            
            # Reset buffer position and create audio segment
            buffer.seek(0)
            audio = AudioSegment.from_file(buffer, format="wav")
            sentence_audio_segments.append(audio)
            sentence_durations.append(len(audio))  # Duration in ms
            print(f"Sentence {idx+1}: '{sentence}' duration {len(audio)} ms")
        except Exception as e:
            print(f"Error processing TTS for sentence {idx}: {e}")
            if os.path.exists(temp_path):
                os.remove(temp_path)
            continue

    if not sentence_audio_segments:
        print("No audio was generated.")
        return None, None

    # Combine all sentence audio segments into one
    combined = AudioSegment.empty()
    for audio in sentence_audio_segments:
        combined += audio

    # Export to in-memory buffer
    audio_buffer = io.BytesIO()
    combined.export(audio_buffer, format="wav")
    audio_buffer.seek(0)
    
    # Create subtitles list with timing
    subtitles = []
    current_time = 0
    
    # Add a small initial delay to account for audio playback initialization
    initial_delay = 250  # ms
    
    for idx, sentence in enumerate(sentences):
        # For bilingual subtitles (optional)
        indo_segment = GoogleTranslator(source='en', target='id').translate(sentence)
        subtitle_text = f"{sentence}\n{indo_segment}" if indo_segment != sentence else sentence
        
        subtitle = {
            'start': current_time + initial_delay,
            'end': current_time + sentence_durations[idx] + initial_delay,
            'text': subtitle_text
        }
        subtitles.append(subtitle)
        current_time += sentence_durations[idx]

    return audio_buffer, subtitles


if __name__ == "__main__":
    voice("Hello, this is a test of the Silero TTS system. It will convert this text into speech and display subtitles in real-time.")