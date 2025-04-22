# import google.generativeai as genai
from langchain_community.document_loaders import AsyncChromiumLoader
from langchain_community.document_transformers import BeautifulSoupTransformer
from duckduckgo_search import DDGS
import re
import sys
import os
import concurrent.futures
import torch
from functools import lru_cache
from recording import process_audio, pause_audio_processing, resume_audio_processing, record_audio, process_audio
import threading
from voice import voice
from dataclasses import dataclass
import time
import random
from pathlib import Path
import json
from open_website import embed_app
from bs4 import BeautifulSoup
import google.generativeai as genai
import ollama


genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
client = genai.GenerativeModel('gemini-1.5-flash')
ollama_model = "deepseek-r1:1.5b"

os.environ["USER_AGENT"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"


@dataclass
class Document:
    page_content: str

def simulate_network_delay():
    """Simulate network latency"""
    delay = random.uniform(0.5, 2.0)
    time.sleep(delay)
    return delay

# def load_simulated_cache():
#     """Load cached website content from a JSON file with error handling"""
#     cache_file = Path("website_cache.json")
#     if cache_file.exists():
#         try:
#             with open(cache_file, "r", encoding="utf-8") as f:
#                 data = json.load(f)
#         except json.JSONDecodeError as e:
#             print(f"Cache file decode error: {e}. Resetting cache.")
#             return {}
#         if not isinstance(data, dict):
#             print("Cache file format invalid. Resetting cache.")
#             return {}
#         return data
#     return {}

# def save_to_cache(query, results):
#     """Save search results to the cache file"""
#     cache_file = Path("website_cache.json")
#     cache = load_simulated_cache()
#     cache[query] = results
#     with open(cache_file, "w", encoding="utf-8") as f:
#         json.dump(cache, f, indent=2)

def process_url(args):
    """Helper function to process URLs in parallel"""
    url, use_simulation = args
    return get_and_transform_page(url, use_simulation)

@lru_cache(maxsize=100)
def ddg_search(query, use_simulation=False):
    """Cache search results for identical queries with simulation option"""
    if use_simulation:
        print("\nSimulating search process...")
        delay = simulate_network_delay()
        print(f"Search engine request took {delay:.2f} seconds")
    
    results = DDGS().text(query, max_results=3)
    urls = []
    for result in results:
        if isinstance(result, dict) and 'href' in result:
            urls.append(result['href'])
        else:
            print(f"Skipping invalid result item: {result}")

    if use_simulation:
        print(f"\nFound {len(urls)} relevant pages to analyze")
        embed_app(urls)
        
        # Loop for print confirmation
        while True:
            print("Do you want to continue? Please say 'Yes' for an explanation or 'No' to skip.")
            resume_audio_processing()
            audio_processor = process_audio()
            translate = next(audio_processor)
            accepted_responses = {"yes", "sure", "ok", "okay", "yup", "yep"}
            negative_responses = {"no", "nope", "nah"}

            if any(resp in translate.lower() for resp in accepted_responses):
                print("Validated response received. Continuing with page processing...")
                break
            elif any(resp in translate.lower() for resp in negative_responses):
                print("User opted out. Aborting processing of search results.")
                return []
            else:
                print("Response not recognized. Please try again.")

        # Process pages sequentially (to avoid concurrently running multiple print prompts)
        docs = [get_and_transform_page(url, use_simulation=True, already_validated=True) for url in urls]
    else:
        url_args = [(url, use_simulation) for url in urls]
        with concurrent.futures.ProcessPoolExecutor(max_workers=os.cpu_count()) as executor:
            docs = list(executor.map(process_url, url_args))
    
    # Instead of truncating, return all available content:
    content = [re.sub("\n\n+", "\n", doc.page_content) for doc in docs]
    return content


def _get_and_transform_page_uncached(url, use_simulation=False, already_validated=False):
    """Helper to retrieve and transform a page without caching."""
    # Only perform the validation step if simulation is requested and not already validated.
    if use_simulation and not already_validated:
        print("Do you want to continue? Please say 'Yes' for an explanation or 'No' to skip.")
        resume_audio_processing()
        audio_processor = process_audio()
        translate = next(audio_processor)
        accepted_responses = {"yes", "sure", "ok", "okay", "yup", "yep"}
        if not any(resp in translate.lower() for resp in accepted_responses):
            print("Response not validated. Aborting content return.")
            return Document(page_content="")  # Aborts processing if not confirmed.
        print("Validated response received. Continuing...")

    if use_simulation:
        delay = simulate_network_delay()
        try:
            embed_app([url])
            print(f"\nAccessing: {url} | Page load took {delay:.2f} seconds")
        except Exception as e:
            print(f"Embed error: {e}")

    loader = AsyncChromiumLoader([url])
    html = loader.load()[0]

    if use_simulation:
        print("Extracting full content...")
        delay = simulate_network_delay()
        print(f"Content extraction took {delay:.2f} seconds")

    # Instead of selectively extracting elements, extract all text from the page:
    soup = BeautifulSoup(str(html.page_content), 'html.parser')
    final_text = soup.get_text(separator="\n")

    return Document(page_content=final_text)


@lru_cache(maxsize=100)
def _get_and_transform_page_cached(url):
    """Cached version for non-simulation (non-interactive) mode."""
    # In cached mode, we force use_simulation=False so that no print prompt is produced.
    return _get_and_transform_page_uncached(url, use_simulation=False)


def get_and_transform_page(url, use_simulation=False, already_validated=False):
    """
    Retrieve and transform the webpage at the given URL.
    
    In simulation mode (use_simulation=True) the function will prompt for user validation
    unless already_validated is True. When use_simulation is False (non-interactive mode),
    the result is cached.
    """
    if use_simulation:
        return _get_and_transform_page_uncached(url, use_simulation, already_validated)
    else:
        return _get_and_transform_page_cached(url)

def truncate(text, word_limit=400):
    """Limit text to specified number of words"""
    words = text.split()
    return " ".join(words[:word_limit])

def create_prompt(query, search_results):
    """Create a formatted prompt with search context"""
    prompt = (
        "Please provide a detailed explanation about the following topic.\n"
        "Note: If the query relates to stores, products, shopping, or purchasing, provide only basic factual information without detailed explanations."
        f"{'\n\n---\n\n'.join(search_results)}\n\n"
        f"Question: {query}\nDetailed Answer:"
    )
    return prompt

def create_completion_gemini(prompt, use_simulation=True):
    """Generate completion using Gemini model"""
    if use_simulation:
        print("\nGenerating response using AI model...")
        delay = simulate_network_delay()
        print(f"AI processing took {delay:.2f} seconds")

    chat = client.start_chat(history=[])
    response = chat.send_message(prompt)
    return response

def create_completion_ollama(prompt, use_simulation=True):
    """Generate completion using Ollama model"""
    if use_simulation:
        print("\nGenerating response using AI model...")
        delay = simulate_network_delay()
        print(f"AI processing took {delay:.2f} seconds")

    try:
        response_ollama = ollama.generate(model=ollama_model, prompt=prompt)

        response = response_ollama['response']
        return response
        

        
    except Exception as e:
        print(f"Error generating Ollama response: {str(e)}")
        return f"Error: {str(e)}"


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
                    
                    # Check if the user said a stop command.
                    if any(keyword in translate.lower() for keyword in [
                        "stop internet", "hentikan internet", "matikan internet"]):
                        print("Menghentikan akses internet...")
                        resume_audio_processing()
                        return None

                    query = translate
                    search_results = ddg_search(query, use_simulation=True)
                    
                    # If user response was negative (i.e. "No") then skip AI processing.
                    if not search_results:
                        print("User opted out, skipping AI processing.")
                        resume_audio_processing()
                        continue

                    prompt = create_prompt(query, search_results)
                    response_ollama = create_completion_ollama(prompt, use_simulation=True)
                    # Check if create_completion_ollama returned an error string
                    if isinstance(response_ollama, str) and response_ollama.startswith("Error:"):
                        print(response_ollama) # Print the error message
                        # Optionally decide how to handle the error, e.g., continue or exit
                        resume_audio_processing()
                        continue # Or return None, depending on desired behavior
                    
                    response = response_ollama # Corrected line: response_ollama is already the string
                    print(response)
                    voice(response)
                    # The return here will exit the main loop after the first successful query. 
                    # Consider removing it if you want the loop to continue.
                    # return response # Commented out or remove if loop should continue

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