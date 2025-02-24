import os, json
import time
from time import sleep
from litellm import completion
from voice import voice
import requests
from bs4 import BeautifulSoup
import urllib3

# Disable insecure request warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


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
newly_learned_urls = []  # Tracks URLs learned in this run only
MAX_TOOL_OUTPUT_LENGTH = 5000  


def register_tool(name, func, description, parameters):
    global tools
    # Remove any previously registered tool with the same name.
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
    print(f"{Colors.OKGREEN}Registered tool: {name}{Colors.ENDC}")


def serialize_tool_result(tool_result, max_length=MAX_TOOL_OUTPUT_LENGTH):
    try:
        serialized_result = json.dumps(tool_result)
    except TypeError:
        serialized_result = str(tool_result)
    if len(serialized_result) > max_length:
        return serialized_result[:max_length] + (
            f"\n\n(Note: Result was truncated to {max_length} characters out of {len(serialized_result)})"
        )
    return serialized_result


def call_tool(function_name, args):
    func = available_functions.get(function_name)
    if not func:
        err_msg = f"Error: Tool '{function_name}' not found."
        print(f"{Colors.WARNING}{err_msg}{Colors.ENDC}")
        return err_msg
    try:
        return func(**args)
    except Exception as e:
        err_msg = f"Error executing '{function_name}': {e}"
        print(f"{Colors.FAIL}{err_msg}{Colors.ENDC}")
        return err_msg


def task_completed():
    return "Task marked as completed."


def websearch(query, num_results=10):
    """
    Performs a web search using DuckDuckGo and returns up to 'num_results' search results.
    """
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.post(
            "https://html.duckduckgo.com/html", 
            data={"q": query}, 
            timeout=10, 
            headers=headers
        )
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
    Additionally, returns the time taken to access the website.
    """
    start_time = time.time()
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, timeout=10, verify=False, headers=headers)
        access_time = time.time() - start_time
        if response.status_code != 200:
            return f"Error: Received status code {response.status_code} while fetching {url} (accessed in {access_time:.2f}s)"
        
        content_type = response.headers.get("Content-Type", "").lower()
        if "application/pdf" in content_type or url.lower().endswith(".pdf"):
            try:
                import io
                from PyPDF2 import PdfReader
                reader = PdfReader(io.BytesIO(response.content))
                title = "PDF Document"
                if reader.metadata and reader.metadata.title:
                    title = reader.metadata.title
                texts = [page.extract_text() for page in reader.pages if page.extract_text()]
                text = "\n".join(texts) if texts else "No text content could be extracted from the PDF."
                return {"title": title, "content": text, "access_time": f"{access_time:.2f} seconds"}
            except Exception as e:
                return f"Error processing PDF: {e} (accessed in {access_time:.2f}s)"
        else:
            soup = BeautifulSoup(response.text, "html.parser")
            title_tag = soup.find("title")
            title = title_tag.get_text(strip=True) if title_tag else "No title found"
            paragraphs = soup.find_all("p")
            content = "\n\n".join([p.get_text(strip=True) for p in paragraphs])
            if not content:
                content = soup.get_text(separator="\n", strip=True)
            return {"title": title, "content": content, "access_time": f"{access_time:.2f} seconds"}
    except Exception as e:
        access_time = time.time() - start_time
        return f"Error fetching website content: {e} (accessed in {access_time:.2f}s)"


def learn_from_url(url):
    try:
        kb_file = "knowledge_base.json"
        kb = {}
        if os.path.exists(kb_file):
            with open(kb_file, "r", encoding="utf-8") as f:
                kb = json.load(f)
        content = fetch_website_content(url)

        # If a 403 error is encountered, skip saving the data
        if isinstance(content, str) and "Received status code 403" in content:
            return f"Skipped learning from {url} due to 403 Forbidden error."

        kb[url] = content
        with open(kb_file, "w", encoding="utf-8") as f:
            json.dump(kb, f, indent=2, ensure_ascii=False)
        global newly_learned_urls
        if url not in newly_learned_urls:
            newly_learned_urls.append(url)
        return f"Content from {url} has been learned and saved."
    except Exception as e:
        return f"Error during learning from URL {url}: {e}"


def learn_all_search_results(search_results):
    if isinstance(search_results, str):
        print(f"{Colors.WARNING}No valid search results to learn from.{Colors.ENDC}")
        return
    for result in search_results:
        url = result.get("url")
        if url:
            print(f"{Colors.OKCYAN}Learning content from: {url}{Colors.ENDC}")
            message = learn_from_url(url)
            print(f"{Colors.OKBLUE}{message}{Colors.ENDC}")
            sleep(1)


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
        print(f"{Colors.WARNING}{search_results}{Colors.ENDC}")
    else:
        for i, result in enumerate(search_results):
            title = result.get("title", "No Title")
            url = result.get("url", "No URL")
            print(f"{Colors.OKGREEN}{i+1}. {title} - {Colors.OKBLUE}{url}{Colors.ENDC}")


def run_main_loop(user_input):
    search_results = websearch(user_input)
    print_search_results(search_results)
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
    
    # Helper function to robustly extract the tool name.
    def get_tool_name(tool_call):
        if isinstance(tool_call, dict):
            return tool_call.get("function", {}).get("name")
        return getattr(tool_call.function, "name", None)
    
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
            if isinstance(response_message, dict):
                assistant_content = response_message.get("content", "")
                tool_calls = response_message.get("tool_calls", [])
            else:
                assistant_content = response_message.content
                tool_calls = getattr(response_message, 'tool_calls', None)
            
            if assistant_content:
                final_response = assistant_content
                messages.append({
                    'role': 'assistant',
                    'content': assistant_content
                })

            if tool_calls and isinstance(tool_calls, list):
                for tool_call in tool_calls:
                    if isinstance(tool_call, dict):
                        func_data = tool_call.get("function", {})
                        function_name = func_data.get("name")
                        raw_args = func_data.get("arguments")
                    else:
                        try:
                            function_name = tool_call.function.name
                            raw_args = tool_call.function.arguments
                        except AttributeError:
                            continue
                    
                    if not function_name:
                        print(f"{Colors.WARNING}Skipping tool call with missing function name.{Colors.ENDC}")
                        continue
                    
                    try:
                        if isinstance(raw_args, str):
                            args = json.loads(raw_args)
                        elif isinstance(raw_args, dict):
                            args = raw_args
                        else:
                            args = {}
                    except Exception as e:
                        print(f"{Colors.WARNING}Error parsing arguments for {function_name}: {e}{Colors.ENDC}")
                        args = {}
                    print(f"{Colors.OKBLUE}Calling tool: {function_name} with arguments: {args}{Colors.ENDC}")
                    tool_result = call_tool(function_name, args)
                    serialized_tool_result = serialize_tool_result(tool_result)
                    messages.append({
                        'role': 'tool',
                        'name': function_name,
                        'content': serialized_tool_result
                    })
                if any(get_tool_name(tc) == "task_completed" for tc in tool_calls):
                    final_response = "Task Completed."
                    break
        except Exception as e:
            final_response = f"Error in main loop: {e}"
            break
        iteration += 1
        sleep(2)
    print("\nFinal Response:")
    print(final_response)
    voice(final_response)


def show_learned_data():
    if not newly_learned_urls:
        print("No new learned data available in this run.")
        return

    kb_file = "knowledge_base.json"
    if os.path.exists(kb_file):
        with open(kb_file, "r", encoding="utf-8") as f:
            kb = json.load(f)
        print("\nLearned Data from the Current Run:")
        for url in newly_learned_urls:
            data = kb.get(url)
            if data:
                if isinstance(data, dict):
                    title = data.get("title", "No title")
                    print(f"\nSource: {url}\nTitle: {title}")
                else:
                    print(f"\nSource: {url}\nData: {data}\n")
            else:
                print(f"\nSource: {url}\nData: Not found in knowledge base.\n")
    else:
        print("No learned data available.")


if __name__ == "__main__":
    user_input = input("Enter your command: ").strip()
    run_main_loop(user_input)
    show_learned_data()