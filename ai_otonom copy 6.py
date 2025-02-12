import os, json, traceback, subprocess, sys
from time import sleep
from litellm import completion
# import ollama
from voice import voice
import requests
from bs4 import BeautifulSoup

# ANSI escape codes for color and formatting (you may remove these if you want plain text output)
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

tools, available_functions = [], {}
MAX_TOOL_OUTPUT_LENGTH = 5000  

api_key = "localhost:11434"
available_api_keys = ["ollama"]  
model_id = "deepseek-r1:1.5b"

def register_tool(name, func, description, parameters):
    global tools
    # Remove any existing tool with the same name
    tools = [tool for tool in tools if tool["function"]["name"] != name]
    available_functions[name] = func
    tools.append({
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": parameters,
                "required": list(parameters.keys())
            }
        }
    })
    print(f"Registered tool: {name}")

def serialize_tool_result(tool_result, max_length=MAX_TOOL_OUTPUT_LENGTH):
    try:
        serialized_result = json.dumps(tool_result)
    except TypeError:
        serialized_result = str(tool_result)
    if len(serialized_result) > max_length:
        return serialized_result[:max_length] + f"\n\n(Note: Result was truncated to {max_length} characters out of {len(serialized_result)})"
    else:
        return serialized_result

def call_tool(function_name, args):
    func = available_functions.get(function_name)
    if not func:
        err_msg = f"Error: Tool '{function_name}' not found."
        print(err_msg)
        return err_msg
    try:
        result = func(**args)
        return result
    except Exception as e:
        err_msg = f"Error executing '{function_name}': {e}"
        print(err_msg)
        return err_msg

def task_completed():
    return "Task marked as completed."

def websearch(query, num_results=5):
    """
    Performs a web search using DuckDuckGo and returns up to 'num_results' search results.
    """
    try:
        response = requests.post("https://html.duckduckgo.com/html", data={"q": query}, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        results = []
        for a in soup.find_all("a", class_="result__a"):
            title = a.get_text(strip=True)
            url = a.get("href")
            results.append({"title": title, "url": url})
            if len(results) >= num_results:
                break
        if not results:
            return "No results found."
        return results
    except Exception as e:
        return f"Error during web search: {e}"

def fetch_website_content(url):
    """
    Fetches content from the specified URL and extracts a title and the page text.
    """
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return f"Error: Received status code {response.status_code} while fetching {url}"
        soup = BeautifulSoup(response.text, "html.parser")
        title_tag = soup.find("title")
        title = title_tag.get_text(strip=True) if title_tag else "No title found"
        paragraphs = soup.find_all("p")
        content = "\n\n".join([p.get_text(strip=True) for p in paragraphs])
        if not content:
            content = soup.get_text(separator="\n", strip=True)
        return {"title": title, "content": content}
    except Exception as e:
        return f"Error fetching website content: {e}"

def learn_from_url(url):
    """
    Fetches website content from a URL and saves it to a local knowledge base,
    but only if the URL hasn't already been learned.
    """
    try:
        kb_file = "knowledge_base.json"
        kb = {}
        if os.path.exists(kb_file):
            with open(kb_file, "r", encoding="utf-8") as f:
                kb = json.load(f)
        if url in kb:
            return f"Content from {url} has already been learned."
        content = fetch_website_content(url)
        if isinstance(content, str):
            return f"Failed to fetch content from {url}: {content}"
        kb[url] = content
        with open(kb_file, "w", encoding="utf-8") as f:
            json.dump(kb, f, indent=2, ensure_ascii=False)
        return f"Content from {url} has been learned and saved."
    except Exception as e:
        return f"Error during learning from URL {url}: {e}"

# Initialize tools
register_tool("task_completed", task_completed, "Marks the current task as completed.", {})

register_tool("websearch", websearch,
              "Performs a web search using DuckDuckGo.",
              {
                  "query": {"type": "string", "description": "The search query."},
                  "num_results": {"type": "integer", "description": "Maximum number of search results to return."}
              })

register_tool("fetch_website_content", fetch_website_content,
              "Fetches text content from a given website URL.",
              {
                  "url": {"type": "string", "description": "The URL to fetch content from."}
              })

register_tool("learn_from_url", learn_from_url,
              "Fetches website content and saves it to a local knowledge base, if not already done.",
              {
                  "url": {"type": "string", "description": "The URL of the website to learn from."}
              })

def run_main_loop(user_input):
    # Get preliminary search results (these inform the AI but will not be explained in the final output)
    search_results = websearch(user_input)
    if isinstance(search_results, str):
        description = search_results
    else:
        description = "\n".join(
            [f"{i+1}. {result['title']} - {result['url']}" 
             for i, result in enumerate(search_results)]
        )
    
    # The system message instructs the AI to simply execute the command without explaining its method.
    messages = [
        {
            'role': 'system',
            'content': (
                "You are a direct executor AI. Execute the user's instructions without commentary on your method. "
                "Provide clear, direct, no-nonsense results. Use tools as needed to fetch and learn data from the internet. "
                "Avoid repeating tasks if data has already been learned. "
                "Available tools: websearch (fetches search results), fetch_website_content (retrieves webpage content), "
                "learn_from_url (stores website data), task_completed (signifies task completion)."
            )
        },
        {
            'role': 'tool',
            'name': 'websearch',
            'content': description
        },
        {
            'role': 'user',
            'content': user_input
        }
    ]

    iteration, max_iterations = 0, 10
    final_response = ""
    while iteration < max_iterations:
        try:
            response = completion(
                model="ollama/deepseek-r1:1.5b", 
                messages=messages,
                api_base="http://localhost:11434"
            )
            if not response.choices:
                final_response = "Error: No response from completion."
                break

            response_message = response.choices[0].message

            if response_message.content:
                final_response = response_message.content
                messages.append({
                    'role': 'assistant',
                    'content': response_message.content or ""
                })

            tool_calls = getattr(response_message, 'tool_calls', None)
            if tool_calls:
                for tool_call in tool_calls:
                    function_name = tool_call.function.name
                    raw_args = tool_call.function.arguments
                    try:
                        if isinstance(raw_args, str):
                            args = json.loads(raw_args)
                        elif isinstance(raw_args, dict):
                            args = raw_args
                        else:
                            args = {}
                    except Exception:
                        args = {}
                    tool_result = call_tool(function_name, args)
                    serialized_tool_result = serialize_tool_result(tool_result)
                    messages.append({
                        'role': 'tool',
                        'name': function_name,
                        'content': serialized_tool_result
                    })
                # If the AI calls "task_completed," then finish the loop.
                if any(tc.function.name == "task_completed" for tc in tool_calls):
                    final_response = "Task Completed."
                    break
        except Exception as e:
            final_response = f"Error in main loop: {e}"
            break
        iteration += 1
        sleep(2)
    print(final_response)

def show_learned_data():
    """
    After the task is complete, display all the information learned from the internet.
    """
    kb_file = "knowledge_base.json"
    if os.path.exists(kb_file):
        with open(kb_file, "r", encoding="utf-8") as f:
            kb = json.load(f)
        print("\nLearned Data from the Internet:")
        for url, data in kb.items():
            if isinstance(data, dict):
                title = data.get("title", "No title")
                content = data.get("content", "No content")
                print(f"\nSource: {url}\nTitle: {title}\nContent: {content}\n")
            else:
                print(f"\nSource: {url}\nData: {data}\n")
    else:
        print("No learned data available.")

if __name__ == "__main__":
    user_input = input("Enter your command: ")
    run_main_loop(user_input)
    show_learned_data()