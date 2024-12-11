import sounddevice as sd
check_device = sd.query_devices()
print("Available channels:", check_device[1]['max_input_channels'])
