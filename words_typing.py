import time
import pyautogui
from pynput.keyboard import Key, Controller

keyboard = Controller()


found = False
timeout = 30  # seconds
start_time = time.time()

while not found and (time.time() - start_time) < timeout:
    word_location = pyautogui.locateCenterOnScreen("word_icon.png", confidence=0.8)
    if word_location:
        found = True
    else:
        time.sleep(1)

if found:

    pyautogui.moveTo(word_location.x, word_location.y, duration=0.5)
    pyautogui.click()
    time.sleep(2)  
else:
    print("Microsoft Word application not found on screen.")
    exit(1)


text = "Lorem Ipsum is simply dummy text of the printing and."


for char in text:
    keyboard.press(char)
    keyboard.release(char)
    time.sleep(0.02)

keyboard.press(Key.enter)
keyboard.release(Key.enter)