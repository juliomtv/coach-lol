import mss
import numpy as np
from PIL import Image
import cv2
import time

class ScreenCapture:
    def __init__(self):
        self.sct = mss.mss()
        # Define a região de captura (ajustar conforme resolução do usuário)
        # Por padrão, captura a tela inteira (monitor 1)
        self.monitor = self.sct.monitors[1]

    def capture_frame(self):
        """Captura um frame da tela e retorna como array numpy (BGR)."""
        screenshot = self.sct.grab(self.monitor)
        img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
        return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

    def save_debug_frame(self, frame, filename="debug_frame.png"):
        cv2.imwrite(filename, frame)

class ReplayCapture:
    def __init__(self, video_path):
        self.cap = cv2.VideoCapture(video_path)

    def get_frame(self):
        ret, frame = self.cap.read()
        if ret:
            return frame
        return None
