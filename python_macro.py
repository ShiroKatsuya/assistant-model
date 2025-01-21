import pyautogui
import time
import webbrowser
import os
from desktop_video_understands import get_insights
from desktop_video_understands import _insights_cache


def detect_language_extension(content):

    if '```python' in content.lower():
        return '.py'
    if content.startswith('```html') or '<!DOCTYPE html>' in content:
        return '.html'
    
    
        

    python_indicators = [
        'print(',
        'import ',
        'def ',
        'class ',
        'if __name__ == "__main__":'
    ]
    
    for indicator in python_indicators:
        if indicator in content:
            return '.py'
    

    language_markers = {
        'python': '.py',
        'javascript': '.js',
        'js': '.js', 
        'typescript': '.ts',
        'c++': '.cpp',
        'cpp': '.cpp',
        'c': '.c',
        'c#': '.cs',
        'csharp': '.cs',
        'php': '.php',
        'rust': '.rs',
        'html': '.html',
        'css': '.css',
        'java': '.java',
        'kotlin': '.kt',
        'swift': '.swift',
        'go': '.go',
        'golang': '.go',
        'ruby': '.rb',
        'perl': '.pl',
        'scala': '.scala',
        'r': '.r',
        'matlab': '.m',
        'sql': '.sql',
        'assembly': '.asm',
        'fortran': '.f90',
        'pascal': '.pas',
        'lua': '.lua',
        'haskell': '.hs',
        'erlang': '.erl',
        'clojure': '.clj',
        'julia': '.jl',
        'dart': '.dart',
        'elixir': '.ex',
        'f#': '.fs',
        'groovy': '.groovy',
        'objective-c': '.m',
        'powershell': '.ps1',
        'vb': '.vb',
        'bash': '.sh',
        'shell': '.sh',
        'xml': '.xml',
        'yaml': '.yaml',
        'json': '.json',
        'markdown': '.md',
        'latex': '.tex',
        'sass': '.scss',
        'less': '.less',
        'coffeescript': '.coffee',
        'vhdl': '.vhd',
        'verilog': '.v',
        'd': '.d',
        'cobol': '.cob',
        'ada': '.ada',
        'lisp': '.lisp',
        'prolog': '.pl'
    }
    
    # Look for language indicators more carefully to avoid false matches
    content_lower = content.lower()
    for lang, ext in language_markers.items():
        # Check for word boundaries to avoid partial matches
        if f' {lang} ' in f' {content_lower} ':
            return ext
    
    # Default to .txt if no language detected
    return '.txt'

def save_to_file(content):
    if not content:
        print("No content to save")
        return None
        
    # Detect file extension based on content
    extension = detect_language_extension(content)
    
    # Create filename with timestamp to avoid overwrites
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f"generated_code_{timestamp}{extension}"
    
    # Save the content
    with open(filename, 'w') as file:
        file.write(content)
    
    return filename

def process_code(code_text):
    import re as pd
    code_blocks = pd.findall(r'```(?:\w+\n)?(.*?)```', code_text, pd.DOTALL)
    
    if code_blocks:
        code = code_blocks[0].strip()
        saved_file = save_to_file(code)
        if saved_file:
            print(f"Code saved to: {saved_file}")

            if saved_file.endswith('.html'):
                webbrowser.open(saved_file)

            elif saved_file.endswith('.py'):
                os.system(f'code {saved_file}')

            else:
                webbrowser.open(saved_file)
    else:
        print("No code blocks found in response")


video_path = "desktop_recording.mp4"
if video_path in _insights_cache:
    program_content = _insights_cache[video_path]
    print("Using cached insights")
else:

    program_content = _insights_cache.get(video_path)

print("Generated content:")
print(program_content)

if program_content:
    time.sleep(1)

    saved_file = save_to_file(program_content)
    if saved_file:
        print(f"Saved to: {saved_file}")
        webbrowser.open(saved_file)
else:
    print("No content was generated")
