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
from main_ui import embed_app
from youtube_search import main as youtube_search
from langchain_core.messages import get_buffer_string, HumanMessage, SystemMessage, AIMessage
os.environ['MONSTER_API_KEY']
monster_client = client()

# from o_detection_transformers import objek_deteksi

detection_stop_event = threading.Event()
detection_thread = None
detection_lock = threading.Lock()  # Add lock for thread safety

# Move conversation_history outside the else block, at class/global level
conversation_history = []
client = genai.Client(api_key="AIzaSyC3mPmd3ps_fGEXMwCjXOUPw7jMpXIeAoE")
model_id = "gemini-2.0-flash-exp"

def main():
    global detection_thread
    # embed_app()
    # audio_thread_intro.start()
    # audio_thread_intro.join()
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
                    
         
                    response = client.models.generate_content(model=model_id, contents=[sentiment, "Briefly explain the meaning of the image and provide theoretical explanations or in-depth information related to what is depicted in the image."])
                    cleaned_response = response.text.replace('*', '').replace('\n\n', '\n')
                    print(cleaned_response)
                    voice(cleaned_response)
                except Exception as e:
                    print(f"Error during image generation: {e}")
                finally:
                    sentiment.close()
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
            # elif any(keyword in translate.lower() for keyword in ["stop camera","hentikan kamera","stop kamera","stop camera"]):
            #     try:
            #         with detection_lock:
            #             if detection_thread and detection_thread.is_alive():
            #                 print("Menghentikan deteksi objek...")
            #                 voice("Menghentikan deteksi objek.")
            #                 detection_stop_event.set()
            #                 detection_thread.join()
            #                 detection_thread = None  # Clear the thread reference
            #                 print("Deteksi objek dihentikan.")
            #             else:
            #                 print("Kamera tidak berjalan.")
            #                 voice("Kamera tidak berjalan.")
            #     except Exception as e:
            #         print(f"Error saat menghentikan kamera: {e}")
            #     finally:
            #         resume_audio_processing()
            # elif any(keyword in translate.lower() for keyword in ["open camera","buka kamera","kamera","camera"]):
            #     try:
            #         with detection_lock:
            #             if detection_thread and detection_thread.is_alive():
            #                 print("Kamera sudah berjalan.")
            #                 # voice("Kamera sudah berjalan.")
            #             else:
            #                 print("Memulai deteksi objek...")
            #                 voice("Memulai deteksi objek.")
            #                 detection_stop_event.clear()
            #                 detection_thread = threading.Thread(target=objek_deteksi, args=(detection_stop_event,))
            #                 detection_thread.daemon = True  # Make thread daemon so it exits when main thread exits
            #                 detection_thread.start()
            #     except Exception as e:
            #         print(f"Unexpected error during object detection: {str(e)}")
            #         voice("Sorry, something went wrong during object detection")
            
            else:
                try:
                    pause_audio_processing()
                    
                    # Send message with full conversation history
                    responses = ai_memory_long_term(
                        initial_message=translate
                    )
                    
                    
                    if responses:
                        final_response = responses[-1]
                        for node, updates in final_response.items():
                            if "messages" in updates:
                                for msg in updates["messages"]:
                                    if isinstance(msg, AIMessage):
                                        # Skip tool code responses
                                        if (hasattr(msg, 'additional_kwargs') and 
                                            (msg.additional_kwargs.get('tool_calls') or
                                             msg.additional_kwargs.get('tool_code'))):
                                            continue
                                        
                                        # Get the full response content
                                        cleaned_response = msg.content.replace('*', '').replace('\n\n', '\n')
                                        
                                        # Split response into lines
                                        response_lines = cleaned_response.split('\n')
                                        
                                        # Process each line, skipping tool_code blocks
                                        valid_lines = []
                                        skip_block = False
                                        for line in response_lines:
                                            line = line.strip()
                                            # Check for start of tool_code block
                                            if line.startswith('```tool_code'):
                                                skip_block = True
                                                continue
                                            # Check for end of code block    
                                            if line.startswith('```') and skip_block:
                                                skip_block = False
                                                continue
                                            # Skip lines in tool_code block
                                            if skip_block:
                                                continue
                                            # Skip individual tool_code lines
                                            if line.startswith('tool_code'):
                                                continue
                                            if line:
                                                valid_lines.append(line)
                                        
                                        # Only process if we have valid lines
                                        if valid_lines:
                                            final_response = ' '.join(valid_lines)
                                            voice(final_response)
                                            conversation_history.extend([translate, final_response])
                                        break
                    else:
                        print("No response received from AI")
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