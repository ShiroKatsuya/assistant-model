import ollama
from recording import process_audio, pause_audio_processing, resume_audio_processing
import recording
from voice import voice
import time
import requests
from PIL import Image
import io
from image_audio import audio_thread_intro_image, play_audio, audio_file
from intro import audio_thread_intro
from voice_internet_access import audio_thread_intro_internet_access
import os
from google import genai
from monsterapi import client
import threading
from Ai_Memory_Long_Term import main as ai_memory_long_term
from internet_access import main as internet_access
# from main_ui import embed_app
from youtube_search import main as youtube_search
from langchain_core.messages import get_buffer_string, HumanMessage, SystemMessage, AIMessage
from desktop_understands import main as desktop_understands
os.environ['MONSTER_API_KEY']
monster_client = client()
from o_detection_with_audio import objek_deteksi
from google.genai.types import (GenerateContentConfig
                                
)

import pygame

from test_main import run_with_inputs, visualization_complete_event

from automation import main as automation_main

# from ai_otonom import internet_akses



# from main_ui import embed_app


# from o_detection_transformers import objek_deteksi

detection_stop_event = threading.Event()
detection_thread = None
detection_lock = threading.Lock()  # Add lock for thread safety

# Move conversation_history outside the else block, at class/global level
conversation_history = []
client = genai.Client(api_key="AIzaSyC3mPmd3ps_fGEXMwCjXOUPw7jMpXIeAoE")
model_id = "gemini-2.0-flash-exp"

generation_config = GenerateContentConfig(
        temperature=0,
        top_p=0.95,
        top_k=20,
        candidate_count=1,
        max_output_tokens=500,
        stop_sequences=["STOP!"],
)

def main():
    global detection_thread
    # embed_app()
    # audio_thread_intro.start()
    # audio_thread_intro.join()
    try:
        for translate in process_audio():
            if any(keyword in translate.lower() for keyword in ["create image", "create images", "buatkan saya gambar", "gambar", "image", "buatkan gambar", "picture", "pictures", "photo", "photos", "Draw", "draw", "Make"]):
                context = translate
                pause_audio_processing()
                image = None

                try:
                    image_intro_thread = threading.Thread(target=play_audio, args=(audio_file,))
                    image_intro_thread.start()
                    image_intro_thread.join()
                    
                    response = monster_client.generate(model='txt2img', data={
                        "prompt": f"Create a realistic and contextually accurate visualization of: {translate}",
                        "negative_prompt": "cartoon, abstract, unrealistic, distorted", 
                        "samples": 1,
                        "steps": 30,  
                        "guidance_scale": 7.5  
                    })
                    print(response)
                    image_url = response['output'][0]  
                    image_bytes = requests.get(image_url).content
                    image = Image.open(io.BytesIO(image_bytes))
                    image = image.resize((1920, 1080 + 850 + 1))
                    image.show()
              
                    sentiment = image

                    # Ask the user whether they want an explanation for this image.
                    voice("Do you want an explanation of this image? Please say 'Yes' for an explanation or 'No' to skip.")
                    resume_audio_processing()
                    # Wait for the user's response.
                    answer = next(process_audio())
                    
                    if any(keyword in answer.lower() for keyword in ["ya", "yes", "iya", "sure", "ok", "oke", "yup", "yep"]):
                        voice("Please wait while I generate the explanation for the image.")
                        explanation_response = client.models.generate_content(
                            model=model_id, 
                            config=generation_config,
                            contents=[
                                sentiment, 
                                f"Discuss the context: {context} briefly with a focus on the information conveyed by the image. Briefly explain the meaning of the image and provide any theoretical or in-depth information related to what is depicted."
                            ]
                        )
                        cleaned_response = explanation_response.text.replace('*', '').replace('\n\n', '\n')
                        print(cleaned_response)
                        voice(cleaned_response)
                    else:
                        voice("I hope you enjoy the image.")
                except Exception as e:
                    print(f"Error during image generation: {e}")
                finally:
                    sentiment.close()
                    resume_audio_processing()


            elif any(keyword in translate.lower() for keyword in ["open", "buka", "jalankan", "run", "start", "execute", "launch", "mulai", "nyalakan", "hidupkan", "application", "aplikasi", "app", "program", "software"]):
                context = translate
                try:
                    import re
                    keywords = ["open", "buka", "jalankan", "run", "start", "execute", "launch", "mulai", "nyalakan", "hidupkan", "application", "aplikasi", "app", "program", "software"]
                    pattern = r'\b(?:' + '|'.join(map(re.escape, keywords)) + r')\b'
                    cleaned_translate = re.sub(pattern, '', translate, flags=re.IGNORECASE).strip()
                    cleaned_translate = re.sub(r'\s+', ' ', cleaned_translate)
                    automation_main(cleaned_translate)
                finally:
                    resume_audio_processing()


            elif any(keyword in translate.lower() for keyword in ["stop internet", "hentikan internet", "stop internet", "stop internet", "matikan internet"]):
                try:
                    with detection_lock:
                        if detection_thread and detection_thread.is_alive():
                            print("Menghentikan internet...")
                            voice("Menghentikan internet.")
                            detection_stop_event.set()
                            detection_thread.join()
                            detection_thread = None  # Clear the thread reference
                            print("internet dihentikan.")
                        else:
                            print("internet tidak berjalan.")
                            voice("internet tidak berjalan.")
                except Exception as e:
                    print(f"Error saat menghentikan internet: {e}")
                finally:
                    resume_audio_processing()
                continue  # Add continue to skip the next elif block
                
            elif any(keyword in translate.lower() for keyword in ["internet", "access internet", "connect to internet", "internet access", "internet connection", "saya ingin akses internet", "please access internet"]):
                try:
                    with detection_lock:
                        if detection_thread and detection_thread.is_alive():
                            print("Internet sudah berjalan.")
                        else:
                            print("Memulai akses internet...")
                            voice("Memulai akses internet.")
                            detection_stop_event.clear()
                            detection_thread = threading.Thread(target=internet_access, args=(detection_stop_event,))
                            detection_thread.daemon = True
                            detection_thread.start()
                            
                            audio_thread = threading.Thread(target=audio_thread_intro_internet_access)
                            audio_thread.start()
                            audio_thread.join()
                            
                            while not detection_stop_event.is_set():
                                response = internet_access()
                                if response and hasattr(response, 'text'):
                                    print(f"Rina: {response.text}")
                                    cleaned_response = response.text.replace('*', '').replace('\n\n', '\n')
                                    voice(cleaned_response)
                                else:
                                    print("No response received from internet access")
                                    break
                except TypeError as e:
                    print(f"Error during internet access: {e}")
                    voice("Sorry, I encountered an error while accessing the internet")
                except Exception as e:
                    print(f"Unexpected error during internet access: {e}")
                    voice("Sorry, something went wrong while accessing the internet")
                finally:
                    resume_audio_processing()
            elif any(keyword in translate.lower() for keyword in ["stop youtube", "hentikan youtube", "stop youtube", "stop youtube"]):
                try:
                    with detection_lock:
                        if detection_thread and detection_thread.is_alive():
                            print("Menghentikan youtube search...")
                            voice("Menghentikan youtube search...")
                            detection_stop_event.set()
                            detection_thread.join()
                            detection_thread = None  # Clear the thread reference
                            print("youtube search dihentikan.")
                        else:
                            print("youtube search tidak berjalan.")
                            voice("youtube search tidak berjalan.")
                except Exception as e:
                    print(f"Error saat menghentikan youtube search: {e}")
                    voice("Sorry, something went wrong while stopping the youtube search")
                finally:
                    resume_audio_processing()
                continue
            elif any(keyword in translate.lower() for keyword in ["youtube","youtube search","youtube search","youtube search","youtube search"]):
                try:
                    with detection_lock:
                        if detection_thread and detection_thread.is_alive():
                            print("youtube sudah berjalan.")
                        else:
                            print("Memulai youtube...")
                            voice("Memulai youtube.")
                            detection_stop_event.clear()
                            detection_thread = threading.Thread(target=youtube_search, args=(detection_stop_event,))
                            detection_thread.daemon = True
                            detection_thread.start()
                            
                            while not detection_stop_event.is_set():
                                response = youtube_search()
                                if response and hasattr(response, 'text'):
                                    print(f"Rina: {response.text}")
                                    cleaned_response = response.text.replace('*', '').replace('\n\n', '\n')
                                    voice(cleaned_response)
                                else:
                                    print("No response received from youtube search")
                                    break
                                
                except Exception as e:
                    print(f"Unexpected error during youtube search: {str(e)}")
                    voice("Sorry, something went wrong during youtube search")
                finally:
                    resume_audio_processing()
            elif any(keyword in translate.lower() for keyword in ["stop camera","hentikan kamera","stop kamera","stop camera"]):
                try:
                    with detection_lock:
                        if detection_thread and detection_thread.is_alive():
                            print("Menghentikan deteksi objek...")
                            voice("Menghentikan deteksi objek.")
                            detection_stop_event.set()
                            detection_thread.join()
                            detection_thread = None  # Clear the thread reference
                            print("Deteksi objek dihentikan.")
                        else:
                            print("Kamera tidak berjalan.")
                            voice("Kamera tidak berjalan.")
                except Exception as e:
                    print(f"Error saat menghentikan kamera: {e}")
                finally:
                    resume_audio_processing()
            elif any(keyword in translate.lower() for keyword in ["open camera","buka kamera","kamera","camera"]):
                try:
                    with detection_lock:
                        if detection_thread and detection_thread.is_alive():
                            print("Kamera sudah berjalan.")
                            # voice("Kamera sudah berjalan.")
                        else:
                            print("Memulai deteksi objek...")
                            voice("Memulai deteksi objek.")
                            detection_stop_event.clear()
                            detection_thread = threading.Thread(target=objek_deteksi, args=(detection_stop_event,))
                            detection_thread.daemon = True  # Make thread daemon so it exits when main thread exits
                            detection_thread.start()
                except Exception as e:
                    print(f"Unexpected error during object detection: {str(e)}")
                    voice("Sorry, something went wrong during object detection")
            elif any(keyword in translate.lower() for keyword in ["stop desktop","hentikan desktop","stop desktop","stop desktop"]):
                try:
                    with detection_lock:
                        if detection_thread and detection_thread.is_alive():
                            print("Menghentikan desktop...")
                            voice("Menghentikan desktop...")
                            detection_stop_event.set()
                            detection_thread.join()
                            detection_thread = None  # Clear the thread reference
                            print("Desktop dihentikan.")
                        else:
                            print("Desktop tidak berjalan.")
                            voice("Desktop tidak berjalan.")
                except Exception as e:
                    print(f"Error saat menghentikan desktop: {e}")
                    voice("Sorry, something went wrong while stopping the desktop")
                finally:
                    resume_audio_processing()
            elif any(keyword in translate.lower() for keyword in ["Run desktop","Run desktop","Run desktop","Run desktop"]):
                try:
                    with detection_lock:
                        if detection_thread and detection_thread.is_alive():
                            print("Desktop sudah berjalan.")
                        else:
                            print("Memulai desktop...")
                            voice("Memulai desktop.")
                            detection_stop_event.clear()
                            detection_thread = threading.Thread(target=desktop_understands, args=(detection_stop_event,))
                            detection_thread.daemon = True  # Make thread daemon so it exits when main thread exits
                            detection_thread.start()
                except Exception as e:
                    print(f"Unexpected error during desktop: {str(e)}")
                    voice("Sorry, something went wrong during desktop")
            else:
                try:
                    # Create a lock to ensure thread safety
                    visualization_lock = threading.Lock()
                    
                    # Acquire lock and pause audio processing before generating content
                    with visualization_lock:
                        print("Pausing audio processing before generating response...")
                        pause_audio_processing()
                        
                        # Short delay to ensure audio processing is fully paused
                        time.sleep(1)
                        
                        print("Audio processing paused, generating response...")
                    
                        # Get response from model
                        response = client.models.generate_content(
                            model=model_id, 
                            config=generation_config,
                            contents=[
                                translate, 
                                f"Please respond to this: {translate} in a friendly and informative manner."
                            ]
                        )

                        # Clean up response
                        cleaned_response = response.text.replace('*', '').replace('\n\n', '\n')
                        
                        # Run visualization and wait for it to complete before resuming audio processing
                        
                        # Maximum retries for failed visualizations
                        max_retries = 3
                        retry_count = 0
                        visualization_completed = False
                        
                        try:
                            # Reset the visualization completion event
                            visualization_complete_event.clear()
                            
                            while not visualization_completed and retry_count < max_retries:
                                # Run visualization
                                visualization_completed = run_with_inputs(cleaned_response)
                                
                                if not visualization_completed and retry_count < max_retries - 1:
                                    print(f"Visualization attempt failed, retrying in 3 seconds...")
                                    retry_count += 1
                                    time.sleep(3)  # Longer pause before retrying
                                    # Reset the event for the next attempt
                                    visualization_complete_event.clear()
                                    # Stop any ongoing playback
                                    if pygame.mixer.get_init() and pygame.mixer.music.get_busy():
                                        pygame.mixer.music.fadeout(500)
                                        time.sleep(0.6)
                                elif not visualization_completed:
                                    print("Visualization failed after maximum retries")
                                    break
                            
                            # Wait for the visualization to fully complete using the event
                            # Using a shorter timeout to speed up transition to audio processing
                            wait_result = visualization_complete_event.wait(timeout=30)
                            if not wait_result:
                                print("Visualization timed out, proceeding to resume audio processing")
                            
                            # Reduced delay before resuming audio processing
                            time.sleep(0.5)
                        finally:
                            # Always resume audio processing when we're done, even if there were errors
                            # Ensure we're outside any lock when resuming
                            print("Transitioning to resume audio processing...")
                            resume_audio_processing()
                        
                except Exception as e:
                    print(f"Error processing response: {e}")
                    # Always resume audio processing on error
                    resume_audio_processing()
                    
    except KeyboardInterrupt:
        print("\nMenghentikan program...")

        for _ in range(len(recording.audio_queue.queue)):
            recording.audio_queue.put(None)
    except Exception as e:
        print(f"Error tak terduga di loop utama: {e}")
    finally:
        with detection_lock:
            if detection_thread and detection_thread.is_alive():
                detection_stop_event.set()
                detection_thread.join()

if __name__ == "__main__":
    main()