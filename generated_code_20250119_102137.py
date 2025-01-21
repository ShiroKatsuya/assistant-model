import unittest
import pyaudio
from unittest.mock import patch


def check_audio_device(channels):
    p = pyaudio.PyAudio()
    for i in range(p.get_device_count()):
        print("\n\n Index " + str(i) + " : \n")
        dev = p.get_device_info_by_index(i)
        print(dev)
        if dev.get('maxInputChannels') >= channels:
           return dev.get('name')
    return None

class TestAudioCheck(unittest.TestCase):

    @patch('pyaudio.PyAudio')
    def test_check_audio_device_found(self, mock_pyaudio):
        mock_instance = mock_pyaudio.return_value
        mock_instance.get_device_count.return_value = 2
        mock_instance.get_device_info_by_index.side_effect = [
          {'maxInputChannels': 1, 'name': 'Device 1'},
          {'maxInputChannels': 4, 'name': 'Device 2'},
        ]
        
        result = check_audio_device(2)
        self.assertEqual(result, 'Device 2')

    @patch('pyaudio.PyAudio')
    def test_check_audio_device_not_found(self, mock_pyaudio):
        mock_instance = mock_pyaudio.return_value
        mock_instance.get_device_count.return_value = 2
        mock_instance.get_device_info_by_index.side_effect = [
          {'maxInputChannels': 1, 'name': 'Device 1'},
          {'maxInputChannels': 1, 'name': 'Device 2'},
        ]
       
        result = check_audio_device(2)
        self.assertIsNone(result)

    @patch('pyaudio.PyAudio')
    def test_check_audio_no_devices(self, mock_pyaudio):
        mock_instance = mock_pyaudio.return_value
        mock_instance.get_device_count.return_value = 0
        result = check_audio_device(2)
        self.assertIsNone(result)
if __name__ == '__main__':
    unittest.main()