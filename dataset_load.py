from datasets import load_dataset
import json

ds = load_dataset("microsoft/orca-agentinstruct-1M-v1", "code_")
formatted_data = [
    {"instruction": item['prompt'], "input":"", "output": item['text']}
    for item in ds['default']
]

# Optionally, save to a JSON file
with open('orca-agentinstruct-1M-v1.json', 'w') as f:
    json.dump(formatted_data, f, indent=4)