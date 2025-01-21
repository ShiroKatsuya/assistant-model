import pyaudio

def check_audio_device(CHANNELS):
    p = pyaudio.PyAudio()
    for i in range(p.get_device_count()):
        print("\n\n Index " + str(i) + " :\n")
        dev = p.get_device_info_by_index(i)
        print(dev)  
        if dev.get('maxInputChannels') >= CHANNELS:
            return dev.get('name')
    return None