import ollama
from recording import process_audio, pause_audio_processing, resume_audio_processing
import recording
from voice import voice
import time
# from model import embed_app


def main():
    # Run embed_app() once before the main loop
    # embed_app()
    
    try:
        for translate in process_audio():
            try:
                # Pause audio processing
                pause_audio_processing()
                
                response = ollama.generate(
                    model='rina-chan',
                    prompt=translate,
                    # language='id',
                )
                print(f"Rina: {response.response}")
                cleaned_response = response.response.replace('*', '')  # Remove asterisks from the response
                voice(cleaned_response)  # Call the voice function with the cleaned response
            except TypeError as e:
                print(f"Error selama ollama.generate: {e}")
            except Exception as e:
                print(f"Error tak terduga selama pemrosesan: {e}")
            finally:
                # Tambahkan penundaan singkat sebelum melanjutkan
                # time.sleep(1)  # Tunda selama 1 detik
                resume_audio_processing()
    except KeyboardInterrupt:
        print("\nMenghentikan program...")
        # Beri tahu antrian untuk berhenti, tanpa sys.exit()
        for _ in range(len(recording.audio_queue.queue)):
            recording.audio_queue.put(None)
    except Exception as e:
        print(f"Error tak terduga di loop utama: {e}")

if __name__ == "__main__":
    main()