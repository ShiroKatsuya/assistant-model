import whisper

model = whisper.load_model("base")

def getspech(file_path):
    try:
        print('Converting audio transcripts into text ...')
        result = model.transcribe(file_path)
        text = result["text"]
        print(text)
        return text
    except Exception as e:
        print(f'Error transcribing audio: {e}')
        return None

getspech('Yel_Yel_Plajar_Pancasila.wav')

print("Speech recognition initialized")
