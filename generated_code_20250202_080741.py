# resume audio processing directly instead of scheduling
print("Audio processing resumed")

# Start audio recording thread if not already running
record_thread = threading.Thread(target=record_audio, daemon=True)
record_thread.start()

# Start audio processing thread if not already running
process_thread = threading.Thread(target=process_audio, daemon=True)
process_thread.start()

else:
    print("Audio processing not resumed")