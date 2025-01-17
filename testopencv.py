import os
import sys

os.add_dll_directory(r'C:\build\install\x64\vc17\bin')
sys.path.append(r'C:\build\install\python')  # Add path to your OpenCV Python bindings

import cv2
print(cv2.__version__)