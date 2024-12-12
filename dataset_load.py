from datasets import load_dataset
import json

ds = load_dataset("HuggingFaceTB/smollm-corpus", "cosmopedia-v2")
formatted_data = [
    {"instruction": item['prompt'], "input":"", "output": item['text']}
    for item in ds['train']
]

# Optionally, save to a JSON file
with open('smollm-corpus_dataset.json', 'w') as f:
    json.dump(formatted_data, f, indent=4)