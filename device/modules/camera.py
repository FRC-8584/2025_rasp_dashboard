import cv2 as cv
import numpy as np
import time
import threading
import base64

from schemas import FrameMessage

class Camera:
    def __init__(self, index: int, retry_interval: int):
        self.index = index
        self.retry_interval = retry_interval
    
        self.lock = threading.Lock()

        self.cap: cv.VideoCapture = None
        self.camera_connected = False

        self._start_monitor()

    def _start_monitor(self):
        thread = threading.Thread(target=self._monitor_camera, daemon=True)
        thread.start()

    def _monitor_camera(self):
        while True:
            with self.lock:
                if not self.camera_connected or self.cap is None:
                    if self.cap:
                        self.cap.release()
                        self.cap = None
                    self._reconnect()
            time.sleep(self.retry_interval)

    def _reconnect(self):
        if self.cap:
            self.cap.release()
        try:
            cap = cv.VideoCapture(self.index)
            if cap.isOpened():
                self.cap = cap
                self.camera_connected = True
                print("Camera reconnected successfully.")
            else:
                self.camera_connected = False
                print("Failed to reconnect camera.")

        except Exception as e:
            print("Camera exception:", e)
            self.camera_connected = False

    def get_frame_data(self):
        with self.lock:
            if self.cap and self.camera_connected:
                ret, frame = self.cap.read()
                if ret:
                    success, buffer = cv.imencode('.jpg', frame)
                    if not success:
                        return FrameMessage(error=True, message="can't encode frame", image=None, latency=0)
                    jpg_as_text = base64.b64encode(buffer).decode('utf-8')
                    return FrameMessage(error=False, message="get frame successfully", image=jpg_as_text, latency=0)
                else:
                    self.camera_connected = False
                    return FrameMessage(error=True, message="can't get frame", image=None, latency=0)
            else:
                return FrameMessage(error=True, message="camera not connected", image=None, latency=0)
