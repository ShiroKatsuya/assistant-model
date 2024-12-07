import os
import asyncio
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import aiofiles
from voice import voice
from recording import generate_transcription
import ollama
from pydub import AudioSegment

app = FastAPI()

@app.post("/process-audio/")
async def process_audio_endpoint(file: UploadFile = File(...)):
    """
    Endpoint untuk mengunggah file audio dan mendapatkan transkripsi serta respons.
    """
    try:
        # Simpan file audio yang diunggah secara asinkron
        file_location = f"temp/{file.filename}"
        os.makedirs(os.path.dirname(file_location), exist_ok=True)
        async with aiofiles.open(file_location, "wb") as buffer:
            content = await file.read()
            await buffer.write(content)

        # Konversi audio ke PCM WAV jika diperlukan
        pcm_wav_path = f"temp/converted_{file.filename}"
        audio = AudioSegment.from_file(file_location)
        audio = audio.set_channels(1)  # Mono
        audio = audio.set_frame_rate(16000)  # 16kHz
        audio.export(pcm_wav_path, format="wav")

        # Proses transkripsi
        transcription = generate_transcription(pcm_wav_path)
        if not transcription:
            raise HTTPException(status_code=400, detail="Transkripsi gagal.")

        # Dapatkan respons dari Ollama
        response = ollama.generate(
            model='rina-chan',
            prompt=transcription,
            language='id',
        )
        response_text = response.response

        # Ubah respons menjadi suara
        voice(response_text)

        return {
            "transcription": transcription,
            "response": response_text
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Hapus file temporer
        for path in [file_location, pcm_wav_path]:
            if os.path.exists(path):
                os.remove(path)

@app.get("/get-audio/{filename}")
def get_audio(filename: str):
    """
    Endpoint untuk mengambil file audio yang dihasilkan.
    """
    file_path = f"output/{filename}.mp3"
    if os.path.exists(file_path):
        return FileResponse(path=file_path, media_type="audio/mpeg", filename=filename + ".mp3")
    else:
        raise HTTPException(status_code=404, detail="File audio tidak ditemukan.")