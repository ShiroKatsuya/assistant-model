import winsound
import datetime
import time

alarm_time = "10:25"

while True:
    now = datetime.datetime.now().strftime("%H:%M")
    if now == alarm_time:
        print("Waktunya bangun!")
        winsound.PlaySound("alarm.wav", winsound.SND_FILENAME)
        break
    time.sleep(30)
