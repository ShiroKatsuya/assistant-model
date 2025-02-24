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
    """
    Registers a tool with a given name, function, description, and parameters.
    Ensures any duplicate tool names are removed.
    """
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
    # Print tool registration in green
    print(f"{Colors.OKGREEN}Registered tool: {name}{Colors.ENDC}")

def serialize_tool_result(tool_result, max_length=MAX_TOOL_OUTPUT_LENGTH):
    """
    Serializes a tool result to a JSON string.
    Truncates the result if it exceeds max_length.
    """
    try:
        serialized_result = json.dumps(tool_result)
    except TypeError:
        serialized_result = str(tool_result)
    if len(serialized_result) > max_length:
        return serialized_result[:max_length] + f"\n\n(Note: Result was truncated to {max_length} characters out of {len(serialized_result)})"
    else:
        return serialized_result

def call_tool(function_name, args):
    """
    Calls the registered tool with the given arguments.
    Handles missing tools and exceptions gracefully.
    """
    func = available_functions.get(function_name)
    if not func:
        err_msg = f"Error: Tool '{function_name}' not found."
        # Print error in warning color
        print(f"{Colors.WARNING}{err_msg}{Colors.ENDC}")
        return err_msg
    try:
        result = func(**args)
        return result
    except Exception as e:
        err_msg = f"Error executing '{function_name}': {e}"
        # Print errors in red
        print(f"{Colors.FAIL}{err_msg}{Colors.ENDC}")
        return err_msg

def task_completed():
    """Marks the current task as completed."""
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
    Fetches content from the specified URL and extracts a title and text content.
    Supports both HTML and PDF content types.
    """
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return f"Error: Received status code {response.status_code} while fetching {url}"
        
        content_type = response.headers.get("Content-Type", "").lower()
        if "application/pdf" in content_type or url.lower().endswith(".pdf"):
            # Process PDF content
            try:
                import io
                from PyPDF2 import PdfReader
                reader = PdfReader(io.BytesIO(response.content))
                # Use PDF metadata if available for the title
                title = "PDF Document"
                if reader.metadata and reader.metadata.title:
                    title = reader.metadata.title
                text = ""
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                text = text.strip() if text.strip() else "No text content could be extracted from the PDF."
                return {"title": title, "content": text}
            except Exception as e:
                return f"Error processing PDF: {e}"
        else:
            # Assume HTML content if not a PDF
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

def learn_all_search_results(search_results):
    """
    Iterates over all website link search results and processes them using learn_from_url
    to store the website content (title and content) into the knowledge_base.json file.
    """
    if isinstance(search_results, str):
        print(f"{Colors.WARNING}No valid search results to learn from.{Colors.ENDC}")
        return

    for result in search_results:
        url = result.get("url")
        if url:
            print(f"{Colors.OKCYAN}Learning content from: {url}{Colors.ENDC}")
            message = learn_from_url(url)
            print(f"{Colors.OKBLUE}{message}{Colors.ENDC}")
            # Sleep briefly between calls to be polite to target servers.
            sleep(1)

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

def print_search_results(search_results):
    """
    Prints website search results with color enhancements.
    """
    print(f"{Colors.HEADER}--- Website Link Search Results ---{Colors.ENDC}")
    if isinstance(search_results, str):
        # In case of an error or no results, print the message in warning color.
        print(f"{Colors.WARNING}{search_results}{Colors.ENDC}")
    else:
        for i, result in enumerate(search_results):
            title = result.get("title", "No Title")
            url = result.get("url", "No URL")
            print(f"{Colors.OKGREEN}{i+1}. {title} - {Colors.OKBLUE}{url}{Colors.ENDC}")

def run_main_loop(user_input):
    """
    Runs the main loop of the AI. It fetches initial search results,
    sends a directive to the AI (with a system prompt that instructs it to be direct and non-explanatory),
    and processes tool calls until the task is marked as completed.
    """
    # Obtain initial search results to provide context to the assistant
    search_results = websearch(user_input)
    print_search_results(search_results)

    # New addition: Automatically learn from all website link search results.
    learn_all_search_results(search_results)

    if isinstance(search_results, str):
        description = search_results
    else:
        description = "\n".join(
            [f"{i+1}. {result['title']} - {result['url']}" 
             for i, result in enumerate(search_results)]
        )
    
    messages = [
        {
            'role': 'system',
            'content': (
                "You are a direct executor AI. "
                "Execute the user's instructions without commentary on your internal process. "
                "Provide clear, direct, and no-nonsense results. "
                "Use available tools to search, fetch, and learn data from the internet. "
                "Do not repeat learning of already-stored content. "
                "Tools available: websearch, fetch_website_content, learn_from_url, task_completed."
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
    
    iteration, max_iterations = 0, 2
    final_response = ""
    while iteration < max_iterations:
        print(f"{Colors.OKCYAN}--- Iteration {iteration+1} of {max_iterations} ---{Colors.ENDC}")
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
                    print(f"{Colors.OKBLUE}Calling tool: {function_name} with arguments: {args}{Colors.ENDC}")
                    tool_result = call_tool(function_name, args)
                    serialized_tool_result = serialize_tool_result(tool_result)
                    messages.append({
                        'role': 'tool',
                        'name': function_name,
                        'content': serialized_tool_result
                    })
                if any(tc.function.name == "task_completed" for tc in tool_calls):
                    final_response = "Task Completed."
                    break
        except Exception as e:
            final_response = f"Error in main loop: {e}"
            break
        iteration += 1
        sleep(2)
    print("\nFinal Response:")
    print(final_response)
    # voice(final_response)

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