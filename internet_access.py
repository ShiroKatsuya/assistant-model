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
from recording import process_audio, pause_audio_processing, resume_audio_processing,record_audio,process_audio
import threading
from voice_internet_access import process_internet_access
from voice import voice
from dataclasses import dataclass
import time
import random
from pathlib import Path
import json
from open_website import embed_app
from bs4 import BeautifulSoup
import google.generativeai as genai


genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
client = genai.GenerativeModel('gemini-1.5-flash')

os.environ["USER_AGENT"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"


@dataclass
class Document:
    page_content: str

def simulate_network_delay():
    """Simulate network latency"""
    delay = random.uniform(0.5, 2.0)
    time.sleep(delay)
    return delay

def load_simulated_cache():
    """Load cached website content from a JSON file"""
    cache_file = Path("website_cache.json")
    if cache_file.exists():
        with open(cache_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_to_cache(query, results):
    """Save search results to the cache file"""
    cache_file = Path("website_cache.json")
    cache = load_simulated_cache()
    cache[query] = results
    with open(cache_file, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2)

def process_url(args):
    """Helper function to process URLs in parallel"""
    url, use_simulation = args
    return get_and_transform_page(url, use_simulation)


@lru_cache(maxsize=100)
def ddg_search(query, use_simulation=True):
    """Cache search results for identical queries with simulation option"""
    if use_simulation:
        print("\nSimulating search process...")
        delay = simulate_network_delay()
        try:
            voice("Simulating search process...")
            print(f"Search engine request took {delay:.2f} seconds")
            voice(f"Search engine request took {delay:.2f} seconds")
        except Exception as e:
            print(f"Voice error: {e}")
        
        cache = load_simulated_cache()
        if query in cache:
            print("Results found in cache")
            try:
                voice("Results found in cache")
            except Exception as e:
                print(f"Voice error: {e}")
            return cache[query]
        print("No cached results found, performing live search")
        try:
            voice("No cached results found, performing live search")
        except Exception as e:
            print(f"Voice error: {e}")
    
    results = DDGS().text(query, max_results=3)
    urls = [result['href'] for result in results]

    if use_simulation:
        print(f"\nFound {len(urls)} relevant pages to analyze")
        try:
            voice(f"\nFound {len(urls)} relevant pages to analyze")
        except Exception as e:
            print(f"Voice error: {e}")

    url_args = [(url, use_simulation) for url in urls]
    with concurrent.futures.ProcessPoolExecutor(max_workers=os.cpu_count()) as executor:
        docs = list(executor.map(process_url, url_args))

    content = [truncate(re.sub("\n\n+", "\n", doc.page_content)) for doc in docs]
    
    if use_simulation:
        print("\nSaving results to cache for future use")
        try:
            voice("Saving results to cache for future use")
        except Exception as e:
            print(f"Voice error: {e}")
        save_to_cache(query, content)
    
    return content

@lru_cache(maxsize=100)
def get_and_transform_page(url, use_simulation=False):
    """Cache transformed pages for identical URLs"""
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
        print("Extracting relevant content...")
        delay = simulate_network_delay()
        print(f"Content extraction took {delay:.2f} seconds")
        if delay >= 3:
            delay = 1
            try:
                voice(f"Content extraction took {delay:.2f} seconds")
            except Exception as e:
                print(f"Voice error: {e}")

    # Parse HTML with BeautifulSoup
    soup = BeautifulSoup(str(html.page_content), 'html.parser')
    
    # Extract text from different elements
    content = {
        'title': soup.find('h1').text.strip() if soup.find('h1') else '',
        'paragraphs': [p.text.strip() for p in soup.find_all('p') if p.text.strip()],
        'headings': [h.text.strip() for h in soup.find_all(['h2', 'h3', 'h4']) if h.text.strip()],
        'lists': [li.text.strip() for li in soup.find_all('li') if li.text.strip()]
    }


    if use_simulation:
        print("Extracted content by type:")

        try:
 
            voiced_messages = set()


            def voice_once(message_key, condition):
                if condition and message_key not in voiced_messages:
                    voice(message_key)
                    voiced_messages.add(message_key)
                  

            if content['title']:
                print("\nTitle:")
                print(content['title'])
                voice_once("Multiple titles found", len(content['title']) >= 3)
       

            if content['headings']:
                print("Headings Accessed")
                voice_once("Multiple headings found", len(content['headings']) >= 3)
    

            if content['paragraphs']:
                print("Paragraphs Accessed") 
                voice_once("Multiple paragraphs found", len(content['paragraphs']) >= 3)
          
            if content['lists']:
                print("List Accessed")
                voice_once("Multiple list items found", len(content['lists']) >= 3)


        except Exception as e:
            print(f"Voice error: {e}")

    # Combine all content with section headers
    final_text = ""
    if content['title']:
        final_text += "TITLE:\n" + content['title'] + "\n\n"
    if content['headings']:
        final_text += "HEADINGS:\n" + "\n".join(content['headings']) + "\n\n"
    if content['paragraphs']:
        final_text += "PARAGRAPHS:\n" + "\n\n".join(content['paragraphs']) + "\n\n"
    if content['lists']:
        final_text += "LIST ITEMS:\n" + "\n".join("• " + item for item in content['lists'])

    # Create document with extracted content using dataclass
    doc = Document(page_content=final_text)
    
    return doc

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
        try:
            voice("Generating response using AI model...")
            voice(f"AI processing took {delay:.2f} seconds")
        except Exception as e:
            print(f"Voice error: {e}")

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
                    search_results = ddg_search(query,use_simulation=True)
                    prompt = create_prompt(query, search_results)
                    response = create_completion_gemini(prompt,use_simulation=True)
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
