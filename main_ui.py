# importing required modules
import vlc
import os
import sys
import tkinter as tk
from tkinter import Label
import threading
import recording
import voice
import subprocess

_app_running = False
_app_lock = threading.Lock()

def embed_app():
    global _app_running
    
    with _app_lock:
        if _app_running:
            return
        _app_running = True

    def run_app():
        # # Kill any existing ffplay processes
        # if sys.platform == "win32":
        #     subprocess.run(['taskkill', '/F', '/IM', 'ffplay.exe'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        # else:
        #     subprocess.run(['killall', 'ffplay'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # # Clear any existing audio files
        # if os.path.exists("output_ai.wav"):
        #     os.remove("output_ai.wav")
            
        if sys.maxsize > 2**32:  
            os.add_dll_directory(r'C:\Program Files\VideoLAN\VLC')
        else:  
            os.add_dll_directory(r'C:\Program Files (x86)\VideoLAN\VLC')


        root = tk.Tk()
        root.geometry('1920x1080')
        root.overrideredirect(True)


        video_label = Label(root)
        video_label.pack(expand=True, fill='both')


        player = vlc.Instance()
        media_player = player.media_player_new()
        media = player.media_new("particles.mp4") 
        media_player.set_media(media)
        media_player.set_fullscreen(False)


        media.add_option('input-repeat=999999') 

        def set_pink_color():
            media_player.video_set_adjust_int(vlc.VideoAdjustOption.Enable, 1)
            media_player.video_set_adjust_float(vlc.VideoAdjustOption.Hue, -45.0)  
            media_player.video_set_adjust_float(vlc.VideoAdjustOption.Saturation, 2.0)
        

        def set_red_color():
            media_player.video_set_adjust_int(vlc.VideoAdjustOption.Enable, 1)
            media_player.video_set_adjust_float(vlc.VideoAdjustOption.Hue, 45.0)  
            media_player.video_set_adjust_float(vlc.VideoAdjustOption.Saturation, 2.0) 


        def reset_color():
            media_player.video_set_adjust_int(vlc.VideoAdjustOption.Enable, 1)
            media_player.video_set_adjust_float(vlc.VideoAdjustOption.Hue, 0)  
            media_player.video_set_adjust_float(vlc.VideoAdjustOption.Saturation, 1.0)
            media_player.video_set_adjust_float(vlc.VideoAdjustOption.Contrast, 1.0)


        def check_status():

            audio_playing = False
            
       
            try:
                import subprocess
                result = subprocess.run(['tasklist'], capture_output=True, text=True)
                if 'ffplay.exe' in result.stdout:
                    audio_playing = True
            except:
                pass
                
        
            try:
                import threading
                for thread in threading.enumerate():
                    if thread.name == 'audio_thread' and thread.is_alive():
                        audio_playing = True
                        break
                    

                for widget in tk._default_root.winfo_children():
                    if isinstance(widget, tk.Tk) and widget.title() == "Subtitle":
                        audio_playing = True
                        break
            except:
                pass

            # Check for output_ai.wav file
            if os.path.exists("output_ai.wav"):
                audio_playing = True

            if audio_playing:
                set_red_color()
            elif not recording.resume_event.is_set():
                set_pink_color()
            else:
                reset_color()
                
            root.after(50, check_status) 


        check_status()


        if sys.platform == "win32":
            video_label.update()
            media_player.set_hwnd(video_label.winfo_id())
        else:
            media_player.set_xwindow(video_label.winfo_id())



        media_player.set_hwnd(video_label.winfo_id())  
        video_label.configure(width=1920, height=1080)  


        media_player.play()

        def check_video():
            state = media_player.get_state()
            if state == vlc.State.Ended:
                media_player.set_position(0)  
                media_player.play()
            root.after(1000, check_video)  

        check_video()



        def on_closing():
            media_player.stop()
            root.destroy()

        root.protocol("WM_DELETE_WINDOW", on_closing)
        root.mainloop()


    app_thread = threading.Thread(target=run_app, daemon=True)
    app_thread.start()