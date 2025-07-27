import cv2 as cv
import numpy as np
import time
import threading
import base64
from typing import Optional
from pathlib import Path
from ultralytics import YOLO
from schemas import SettingsModel, ObjectData, HSV_SCOPE

YOLO_MODELS_PATH = Path(__file__).parent.parent / "yolo_models/object_model.pt"

class Camera:
    def __init__(self, camera_index: int, retry_interval: int):
        self.detection_result: ObjectData = None
        self.settings:SettingsModel = None

        self.camera_index = camera_index
        self.retry_interval = retry_interval

        self.lock = threading.Lock()

        self.cap = None
        self.connected = False
        self.keep_running = True
        self.ret = False
        self.corrected_frame = None
        self.model = YOLO(YOLO_MODELS_PATH)

        self.update_settings(
            SettingsModel(
                type="color",
                show_as="normal",
                gain=100,
                black_level=0,
                red_balance=1000,
                blue_balance=1000,
                hsv_scope=HSV_SCOPE(
                    hue_min=0, hue_max=10,
                    sat_min=100, sat_max=255,
                    val_min=100, val_max=255
                ),
                box_object=True
            )
        )
        self._start_monitor()

    def update_settings(self, settings: SettingsModel):
        self.settings = settings
    
    def _start_monitor(self):
        thread = threading.Thread(target=self._monitor_camera, daemon=True)
        thread.start()

    def _monitor_camera(self):
        while self.keep_running:
            with self.lock:
                if not self.connected or self.cap is None or not self.ret:
                    if self.cap:
                        self.cap.release()
                        self.cap = None
                    self._reconnect()
            time.sleep(self.retry_interval)

    def _reconnect(self):
        if self.cap:
            self.cap.release()
        try:
            cap = cv.VideoCapture(self.camera_index)
            cap.set(cv.CAP_PROP_AUTO_EXPOSURE, 0.25)
            if cap.isOpened():
                self.cap = cap
                self.connected = True
                print("Camera reconnected successfully.")
            else:
                self.connected = False
                print("Failed to reconnect camera.")
        except Exception as e:
            print("Camera exception:", e)
            self.connected = False

    def process(self) -> Optional[ObjectData]:
        with self.lock:
            if self.cap and self.connected:
                self.ret, frame = self.cap.read()
                if self.ret:
                    frame = frame.astype(np.float32)
                    # black level
                    frame = np.maximum(frame - self.settings.black_level, 0)
                    b, g, r = cv.split(frame)
                    # r, b balence
                    r *= self.settings.red_balance / 1000
                    b *= self.settings.blue_balance / 1000
                    # gain
                    frame = cv.merge([b, g, r])
                    gain_factor = self.settings.gain / 100
                    frame *= gain_factor
                    self.corrected_frame = np.clip(frame, 0, 255).astype(np.uint8)

                    if self.settings.type == "color":
                        hsv = cv.cvtColor(self.corrected_frame, cv.COLOR_BGR2HSV)
                        lower = np.array([self.settings.hsv_scope.hue_min, self.settings.hsv_scope.sat_min, self.settings.hsv_scope.val_min])
                        upper = np.array([self.settings.hsv_scope.hue_max, self.settings.hsv_scope.sat_max, self.settings.hsv_scope.val_max])
                        mask = cv.inRange(hsv, lower, upper)
                        contours, _ = cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

                        if not contours:
                            self.detection_result = ObjectData(detected=False, x=0, y=0, a=0)
                            return self.detection_result
                        
                        largest = max(contours, key=cv.contourArea)
                        area = cv.contourArea(largest)
                        
                        if self.settings.box_object:
                            if self.settings.show_as == "mask":
                                self.corrected_frame = cv.cvtColor(mask, cv.COLOR_GRAY2BGR)
                                
                            cv.drawContours(self.corrected_frame, [largest], -1, (0, 255, 0), 2)

                        M = cv.moments(largest)
                        if M["m00"] == 0:
                            self.detection_result = ObjectData(detected=False, x=0, y=0, a=0)
                            return self.detection_result
                        
                        cx = int(M["m10"] / M["m00"])
                        cy = int(M["m01"] / M["m00"])
                        
                        h, w = self.corrected_frame.shape[:2]
                        norm_x = (cx / w) * 2 - 1         
                        norm_y = -((cy / h) * 2 - 1)     
                        norm_a = area / (w*h)   

                        if norm_a* 100 <= self.settings.min_area :
                            self.detection_result = ObjectData(detected=False, x=0, y=0, a=0)
                            return self.detection_result

                        self.detection_result = ObjectData(detected=True, x=norm_x, y=norm_y, a=norm_a)
                        return self.detection_result
                    else:
                        results = self.model(self.corrected_frame)
                        boxes = results[0].boxes
                        if boxes is None or len(boxes) == 0:
                            return ObjectData(detected=False, x=0.0, y=0.0, a=0.0)
                        
                        max_box = max(boxes, key=lambda b: (b.xyxy[0][2] - b.xyxy[0][0]) * (b.xyxy[0][3] - b.xyxy[0][1]))
                        x1, y1, x2, y2 = [float(v) for v in max_box.xyxy[0]]
                        
                        if self.settings.box_object:
                            cv.rectangle(self.corrected_frame, (int(x1), int(y1)), (int(x2), int(y2)), (255, 0, 0), 2)

                        cx = (x1 + x2) / 2
                        cy = (y1 + y2) / 2
                        area = (x2 - x1) * (y2 - y1)

                        h, w = self.corrected_frame.shape[:2]
                        norm_x = (cx / w) * 2 - 1  
                        norm_y = -((cy / h) * 2 - 1)
                        norm_a = area / (w * h)
                        
                        self.detection_result = ObjectData(detected=True, x=norm_x, y=norm_y, a=norm_a)
                        return self.detection_result
                else:
                    self.connected = False
                    return None 
        
    def get_corrected_frame_base64(self) -> Optional[str]:
        with self.lock:
            if self.corrected_frame is None:
                return None
            success, buffer = cv.imencode('.jpg', self.corrected_frame)
            if not success:
                return None
            jpg_as_text = base64.b64encode(buffer).decode('utf-8')
            return jpg_as_text
        
    def shutdown(self):
        self.keep_running = False
        if self.cap:
            self.cap.release()