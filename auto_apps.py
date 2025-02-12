import os
import subprocess

try:
    # Use PowerShell command to get installed apps
    command = "powershell -command Get-StartApps"
    applications = subprocess.check_output(command, shell=True, text=True)
    print(applications)
    
    check_aplication = "C:\Users\MyBook Hype AMD\AppData\Local\Programs\Ollama\ollama app.exe"
    
    if os.path.exists(check_aplication):
        print("The application is installed")
        
    if applications == check_aplication.split("\n"):
        print("True because the application is installed")

except subprocess.CalledProcessError as e:
    print(f"Error executing command: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")

