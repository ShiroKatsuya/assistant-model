import google.generativeai as genai
from langchain_community.document_loaders import AsyncChromiumLoader
from langchain_community.document_transformers import BeautifulSoupTransformer
from duckduckgo_search import DDGS
import re
import sys
import os
import concurrent.futures
import torch
from functools import lru_cache
from recording import process_audio, pause_audio_processing, resume_audio_processing,record_audio,process_audio
import threading
from voice_internet_access import process_internet_access
from voice import voice

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
client = genai.GenerativeModel('gemini-1.5-flash')

os.environ["USER_AGENT"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

@lru_cache(maxsize=100)
def ddg_search(query):
    audio_thread = threading.Thread(target=process_internet_access)
    audio_thread.start()
    audio_thread.join()
    """Cache search results for identical queries"""
    results = DDGS().text(query, max_results=3)
    urls = [result['href'] for result in results]

    with concurrent.futures.ProcessPoolExecutor(max_workers=os.cpu_count()) as executor:
        docs = list(executor.map(get_and_transform_page, urls))

    content = [truncate(re.sub("\n\n+", "\n", doc.page_content)) for doc in docs]
    return content

@lru_cache(maxsize=100)
def get_and_transform_page(url):
    """Cache transformed pages for identical URLs"""
    loader = AsyncChromiumLoader([url])
    html = loader.load()[0]

    bs_transformer = BeautifulSoupTransformer()
    docs_transformed = bs_transformer.transform_documents(
        [html],
        tags_to_extract=["p"],
        remove_unwanted_tags=["a"]
    )

    return docs_transformed[0]

def truncate(text, word_limit=400):
    """Limit text to specified number of words"""
    words = text.split()
    return " ".join(words[:word_limit])

def create_prompt(query, search_results):
    """Create a formatted prompt with search context"""
    prompt = (
        "Answer the question using only the context below.\n\n"
        "Context:\n"
        f"{'\n\n---\n\n'.join(search_results)}\n\n"
        f"Question: {query}\nAnswer:"
    )
    return prompt

def create_completion_gemini(prompt):
    """Generate completion using Gemini model"""
    chat = client.start_chat(history=[])
    response = chat.send_message(prompt)
    return response

def main():
    if torch.cuda.is_available():
        print("CUDA is available. Utilizing GPU for processing.")
    else:
        print("CUDA is not available. Proceeding with CPU.")
    audio_processor = process_audio()
    resume_audio_processing()
    try:
        while True:
            try:
                translate = next(audio_processor)
                if translate:
                    pause_audio_processing()
                    if any(keyword in translate.lower() for keyword in ["stop internet", "hentikan internet", "stop internet", "matikan internet"]):
                        voice("Menghentikan akses internet...")
                        resume_audio_processing()
                        return None
                    query = translate
                    search_results = ddg_search(query)
                    prompt = create_prompt(query, search_results)
                    response = create_completion_gemini(prompt)
                    return response
            except StopIteration:
                continue
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        return None
    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")
        resume_audio_processing()
        return None

if __name__ == "__main__":
    main()
