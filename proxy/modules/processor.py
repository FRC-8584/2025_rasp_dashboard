import cv2 as cv
import numpy as np
import threading
import base64
import io
from typing import Optional
from PIL import Image
from ultralytics import YOLO
from pathlib import Path
from schemas import SettingsModel, HSV_SCOPE, ObjectData

YOLO_MODELS_PATH = Path(__file__).parent.parent / "yolo_models/object_model.pt"

class Processor:
    def __init__(self):
        self.detection_result: ObjectData = ObjectData(x=0, y=0, a=0, detected=False)
        self.settings: SettingsModel = None

        self.lock = threading.Lock()
        self.corrected_frame = None

        self.message: str = ""
        self.latency: float = 0
        
        # self.model = YOLO(YOLO_MODELS_PATH)

        self.update_settings(
            SettingsModel(
                type="color",
                show_as="normal",
                gain=100,
                black_level=0,
                red_balance=1000,
                blue_balance=1000,
                min_area=10,
                hsv_scope=HSV_SCOPE(
                    hue_min=0, hue_max=100,
                    sat_min=0, sat_max=255,
                    val_min=0, val_max=255
                ),
                box_object=True
            )
        )

    def update_status(self, message: bool, latency: float):
        self.message = message
        self.latency = latency

    def update_settings(self, settings: SettingsModel):
        self.settings = settings

    def process(self, image_base64: str):
        with self.lock:
            image_bytes = base64.b64decode(image_base64)
            image = Image.open(io.BytesIO(image_bytes))
            image_np = np.array(image)
            frame = image_np.astype(np.float32)

            frame = np.maximum(frame - self.settings.black_level, 0)
            b, g, r = cv.split(frame)
            # r, b balence
            r *= self.settings.red_balance / 1000
            b *= self.settings.blue_balance / 1000
            # gain
            frame = cv.merge([b, g, r])
            gain_factor = (self.settings.gain+50) / 100
            frame *= gain_factor
            self.corrected_frame = np.clip(frame, 0, 255).astype(np.uint8)

            h, w = self.corrected_frame.shape[:2]

            if self.settings.type == "color":
                hsv = cv.cvtColor(self.corrected_frame, cv.COLOR_BGR2HSV)
                lower = np.array([self.settings.hsv_scope.hue_min, self.settings.hsv_scope.sat_min, self.settings.hsv_scope.val_min])
                upper = np.array([self.settings.hsv_scope.hue_max, self.settings.hsv_scope.sat_max, self.settings.hsv_scope.val_max])
                mask = cv.inRange(hsv, lower, upper)
                kernel = cv.getStructuringElement(cv.MORPH_RECT, (5, 5))
                mask = cv.morphologyEx(mask, cv.MORPH_OPEN, kernel)
                contours, _ = cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

                if self.settings.show_as == "mask":
                    self.corrected_frame = mask
                    self.corrected_frame = cv.cvtColor(mask, cv.COLOR_GRAY2BGR)

                if not contours:
                    self.detection_result = ObjectData(detected=False, x=0, y=0, a=0)
                    return
                        
                largest = max(contours, key=cv.contourArea)
                area = cv.contourArea(largest)
                norm_a = area / (w*h)

                if (norm_a * 100) <= self.settings.min_area:
                    if self.settings.show_as == "mask":
                        self.corrected_frame = mask
                    self.detection_result = ObjectData(detected=False, x=0, y=0, a=norm_a)
                    return
                        
                if self.settings.box_object:
                    x, y, w_box, h_box = cv.boundingRect(largest)
                    cv.rectangle(self.corrected_frame, (x, y), (x + w_box, y + h_box), (0, 255, 0), 2)

                M = cv.moments(largest)
                if M["m00"] == 0:
                    self.detection_result = ObjectData(detected=False, x=0, y=0, a=0)
                    return
                        
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                        
                norm_x = (cx / w) * 2 - 1         
                norm_y = -((cy / h) * 2 - 1)    

                self.detection_result = ObjectData(detected=True, x=norm_x, y=norm_y, a=norm_a)
                return
            
            else:
                self.corrected_frame = cv.resize(self.corrected_frame.copy(), [256, 192])
                results = self.model(self.corrected_frame, classes=[1])  
                boxes = results[0].boxes

                if not boxes:
                    self.detection_result = ObjectData(detected=False, x=0.0, y=0.0, a=0.0)
                    return
                
                boxes_np = boxes.xyxy.cpu().numpy()
                classes_np = boxes.cls.cpu().numpy()

                target_boxes = [xyxy for xyxy, cls in zip(boxes_np, classes_np) if int(cls) == 1]

                if not target_boxes:
                    self.detection_result =  ObjectData(detected=False, x=0.0, y=0.0, a=0.0)
                    return

                max_box = max(target_boxes, key=lambda b: (b[2] - b[0]) * (b[3] - b[1]))
                x1, y1, x2, y2 = max_box

                if self.settings.box_object:
                    x1i, y1i, x2i, y2i = map(int, (x1, y1, x2, y2))
                    cx_int = (x1i + x2i) // 2
                    cy_int = (y1i + y2i) // 2
                    cv.rectangle(self.corrected_frame, (x1i, y1i), (x2i, y2i), (255, 0, 0), 2)
                    cv.circle(self.corrected_frame, (cx_int, cy_int), 5, (0, 0, 255), -1)

                cx = (x1 + x2) / 2
                cy = (y1 + y2) / 2
                area = (x2 - x1) * (y2 - y1)

                h, w = self.corrected_frame.shape[:2]
                norm_x = (cx / w) * 2 - 1
                norm_y = -((cy / h) * 2 - 1)
                norm_a = area / (w * h)
            
                self.detection_result = ObjectData(detected=True, x=norm_x, y=norm_y, a=norm_a)
                return
            
    def get_corrected_frame_base64(self) -> Optional[str]:
        with self.lock:
            if self.corrected_frame is None:
                return None
            success, buffer = cv.imencode('.jpg', self.corrected_frame)
            if not success:
                return None
            jpg_as_text = base64.b64encode(buffer).decode('utf-8')
            return jpg_as_text
        
    def get_corrected_object_data(self) -> ObjectData:
        with self.lock:
            return self.detection_result