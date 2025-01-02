import ollama
from recording import process_audio, pause_audio_processing, resume_audio_processing
import recording
from voice import voice
import time
import requests
from PIL import Image
import io
# from intro import audio_thread_intro
# from model import embed_app
from main_ui import embed_app
from image_audio import audio_thread_intro_image
from intro import audio_thread_intro

import os
import google.generativeai as genai
from monsterapi import client

from internet_access import main as internet_access

os.environ['MONSTER_API_KEY']
monster_client = client()

def main():
    # Run embed_app() once before the main loop
    # embed_app()
    embed_app()
    audio_thread_intro.start()
    audio_thread_intro.join()

    try:
        for translate in process_audio():
            if any(keyword in translate.lower() for keyword in ["create image", "create images", "buatkan saya gambar", "gambar", "image", "buatkan gambar","picture","pictures","buatkan gambar","photo","photos","buatkan gambar","Draw","draw","Make"]):
         
                pause_audio_processing()
                image = None

                try:
                    audio_thread_intro_image.start()
                    audio_thread_intro_image.join()
                    response = monster_client.generate(model='txt2img', data={
                        "prompt": translate})
                    print(response)
                    image_url = response['output'][0]  # Get first URL from output list
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
        # Clear the audio queue without sys.exit()
        for _ in range(len(recording.audio_queue.queue)):
            recording.audio_queue.put(None)
    except Exception as e:
        print(f"Error tak terduga di loop utama: {e}")

if __name__ == "__main__":
    main()
    