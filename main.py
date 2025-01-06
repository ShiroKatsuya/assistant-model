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
import google.generativeai as genai
from monsterapi import client
import threading
from o_detection_transformers import objek_deteksi
from internet_access import main as internet_access
from main_ui import embed_app

os.environ['MONSTER_API_KEY']
monster_client = client()


detection_stop_event = threading.Event()
detection_thread = None
detection_lock = threading.Lock()  # Add lock for thread safety



            

def main():
    global detection_thread
    embed_app()
    audio_thread_intro.start()
    audio_thread_intro.join()
    try:
        for translate in process_audio():
            if any(keyword in translate.lower() for keyword in ["create image", "create images", "buatkan saya gambar", "gambar", "image", "buatkan gambar","picture","pictures","buatkan gambar","photo","photos","buatkan gambar","Draw","draw","Make"]):
             
                pause_audio_processing()
                image = None

                try:

                    image_intro_thread = threading.Thread(target=play_audio, args=(audio_file,))
                    image_intro_thread.start()
                    image_intro_thread.join()
                    
                    response = monster_client.generate(model='txt2img', data={
                        "prompt": f"Create a realistic and contextually accurate visualization of: {translate} in the context",
                        "negative_prompt": "cartoon, abstract, unrealistic, distorted", 
                        "samples": 1,
                        "steps": 30,  
                        "guidance_scale": 7.5  
                        })
                    print(response)
                    image_url = response['output'][0]  
                    image_bytes = requests.get(image_url).content
                    image = Image.open(io.BytesIO(image_bytes))
                    image.resize((1920, 1080 + 850+1))
                    image.show()
              
                    sentiment = image
                    model = genai.GenerativeModel('gemini-1.5-flash')
         
                    response = model.generate_content(["describe the image in detail", sentiment])
                    cleaned_response = response.text.replace('*', '').replace('\n\n', '\n')
                    print(cleaned_response)
                    voice(cleaned_response)
                except Exception as e:
                    print(f"Error during image generation: {e}")
                finally:
                    sentiment.close()
                    resume_audio_processing()
            elif any(keyword in translate.lower() for keyword in ["internet", "access internet", "connect to internet", "internet access","internet connection","saya ingin akses internet","pelase access internet"]):
                try:
                   
                    audio_thread = threading.Thread(target=audio_thread_intro_internet_access)
                    audio_thread.start()
                    audio_thread.join()
                    pause_audio_processing()
                    response = internet_access()
                    if response and hasattr(response, 'text'):
                  
                        print(f"Rina: {response.text}")
                        cleaned_response = response.text.replace('*', '').replace('\n\n', '\n')
                        voice(cleaned_response)
                    else:
                        print("No response received from internet access")
                except TypeError as e:
                    print(f"Error during internet access: {e}")
                    voice("Sorry, I encountered an error while accessing the internet")
                except Exception as e:
                    print(f"Unexpected error during internet access: {e}")
                    voice("Sorry, something went wrong while accessing the internet")
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
            else:
                try:
             
                    pause_audio_processing()
                    genai.configure(api_key = os.getenv("GEMINI_API_KEY"))
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    chat = model.start_chat(history=[])
                    response = chat.send_message(translate)
                    print(f"Rina: {response.text}")
                    cleaned_response = response.text.replace('*', '').replace('\n\n', '\n')  # Remove asterisks and extra newlines from the response
                    voice(cleaned_response)  # Call the voice function with the cleaned response
                except TypeError as e:
                    print(f"Error during chat generation: {e}")
                except Exception as e:
                    print(f"Unexpected error during processing: {e}")
                finally:
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