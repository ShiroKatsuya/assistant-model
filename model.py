import tkinter as tk
import subprocess
import time
import win32gui
import win32con
import win32process

def embed_app():
    root = tk.Tk()
    root.title("VTube Studio Integration")
    root.geometry("1080x1920+850+5")
    root.minsize(1080, 1920)  # Optional: Set a minimum window size
    root.overrideredirect(True)
    

    # Make the root window transparent
    root.attributes('-alpha', 0.7)  # Set transparency level (0.0 to 1.0)
    
    root.wm_attributes('-transparentcolor', 'black')

    # Create a frame to embed the application with a default size
    app_frame = tk.Frame(root, width=1080, height=1920 ,background="black")  # Set background color to black for better transparency effect
    app_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)  # Position the frame on the right side

    # Start the external application
    proc = subprocess.Popen(r"C:\Program Files (x86)\Steam\steamapps\common\VTube Studio\VTube Studio.exe")
    time.sleep(1)  # Wait for the application window to initialize

    # Find the window handle of the external application
    def enum_windows_callback(hwnd, pid):
        if win32process.GetWindowThreadProcessId(hwnd)[1] == pid:
            # Set the parent of the external window to the app_frame
            win32gui.SetParent(hwnd, app_frame.winfo_id())
            
            # Retrieve the current style and add WS_CHILD to make it resize with the frame
            style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
            style = style | win32con.WS_CHILD
            win32gui.SetWindowLong(hwnd, win32con.GWL_STYLE, win32con.WS_VISIBLE)
            
            # Resize the embedded window to fit the frame
            win32gui.MoveWindow(hwnd, 0, 0, 1080, 1920, True )
            return False  # Stop enumeration
        return True

    win32gui.EnumWindows(lambda hwnd, param: enum_windows_callback(hwnd, proc.pid), None)

    # Update the embedded application size when the frame is resized
    def on_resize(event):
        hwnd = None
        def find_hwnd(hwnd_enum, pid):
            nonlocal hwnd
            if win32process.GetWindowThreadProcessId(hwnd_enum)[1] == proc.pid:
                hwnd = hwnd_enum
                return False
            return True
        win32gui.EnumWindows(find_hwnd, proc.pid)
        if hwnd:
            win32gui.MoveWindow(hwnd, 0, 0, 1080, 1920, True )
            

    app_frame.bind("<Configure>", on_resize)

    root.mainloop()

embed_app()