from fastapi import FastAPI
import ollama

app = FastAPI()

@app.get("/generate_response")
def generate_response(transcription: str):

                
    response = ollama.generate(
        model='rina-chan',
        prompt=transcription,
        language='id',
    )
    return {"response": response.response}