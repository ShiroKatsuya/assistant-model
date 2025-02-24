import time
import pyautogui
from pynput.keyboard import Key, Controller

keyboard = Controller()

alarm_found = False
timeout = 30  
start_time = time.time()

while not alarm_found and (time.time() - start_time) < timeout:
    alarm_location = pyautogui.locateCenterOnScreen("alarm_icon.png", confidence=0.95, grayscale=True)
    if alarm_location:
        alarm_found = True
    else:
        time.sleep(1)

if alarm_found:
    pyautogui.moveTo(alarm_location.x, alarm_location.y, duration=0.5)
    pyautogui.click()
    time.sleep(2)
else:
    print("Alarm application not found on screen.")
    exit(1)


def generate_alarm_message():

    return "Good morning! Your AI-powered alarm is now active. Time to wake up!"

alarm_message = generate_alarm_message()

for char in alarm_message:
    keyboard.press(char)
    keyboard.release(char)
    time.sleep(0.02)

keyboard.press(Key.enter)
keyboard.release(Key.enter)