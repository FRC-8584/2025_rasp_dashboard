from pyorbbecsdk import Pipeline, Config, OBFormat, OBSensorType
from schemas import StatusData
import threading
import time
import cv2 as cv
import numpy as np
import base64

from configs import COLOR_PROFILE_FPS, COLOR_PROFILE_HEIGHT, COLOR_PROFILE_WIDTH
from configs import DEPTH_PROFILE_FPS, DEPTH_PROFILE_HEIGHT, DEPTH_PROFILE_WIDTH

class Gemini:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if getattr(self, "_initialized", False):
            return
        self._initialized = True

        self.status: StatusData = StatusData(
            error=True,
            connected=False,
            t_x=0,
            t_y=0,
            t_a=0,
            depth=0,
            color_image_base64=None,
            depth_image_base64=None,
            message="connecting to camera"
        )
        self.pipeline = Pipeline()
        self.config = Config()
        self._start_camera_process()
    
    @staticmethod
    def _mat_to_base64(mat, ext=".jpg"):
        success, encoded_image = cv.imencode(ext, mat)
        if not success:
            raise ValueError("Encode image failed")
        b64_bytes = base64.b64encode(encoded_image.tobytes())
        b64_str = b64_bytes.decode('utf-8')
        return b64_str

    @staticmethod
    def _pick_profile(profiles, fmt, width=None, height=None, fps=None):
        for p in profiles:
            profile_fmt = None
            if hasattr(p, 'get_format'):
                profile_fmt = p.get_format()
            elif hasattr(p, 'format'):
                profile_fmt = getattr(p, 'format')
            elif hasattr(p, 'pixel_format'):
                profile_fmt = getattr(p, 'pixel_format')
            else:
                raise RuntimeError("Cannot get format from profile object")

            w = p.get_width() if hasattr(p, 'get_width') else None
            h = p.get_height() if hasattr(p, 'get_height') else None
            f = p.get_fps() if hasattr(p, 'get_fps') else None

            if profile_fmt == fmt:
                if width is not None and w != width:
                    continue
                if height is not None and h != height:
                    continue
                if fps is not None and f != fps:
                    continue
                return p

        for p in profiles:
            profile_fmt = None
            if hasattr(p, 'get_format'):
                profile_fmt = p.get_format()
            elif hasattr(p, 'format'):
                profile_fmt = getattr(p, 'format')
            elif hasattr(p, 'pixel_format'):
                profile_fmt = getattr(p, 'pixel_format')
            else:
                raise RuntimeError("Cannot get format from profile object")

            if profile_fmt == fmt:
                return p
        raise RuntimeError(f"No matching profile for format={fmt} width={width} height={height} fps={fps}")

    def _start_camera_process(self):
        thread = threading.Thread(target=self._run_camera, daemon=True)
        thread.start()

    def _run_camera(self):
        while True:
            try: 
                try:
                    color_profiles = self.pipeline.get_stream_profile_list(OBSensorType.COLOR_SENSOR)
                    depth_profiles = self.pipeline.get_stream_profile_list(OBSensorType.DEPTH_SENSOR)
                    color_profile = self._pick_profile(color_profiles, OBFormat.RGB, COLOR_PROFILE_WIDTH, COLOR_PROFILE_HEIGHT, COLOR_PROFILE_FPS)
                    depth_profile = self._pick_profile(depth_profiles, OBFormat.Y16, DEPTH_PROFILE_WIDTH, DEPTH_PROFILE_HEIGHT, DEPTH_PROFILE_FPS)
                
                    self.config.enable_stream(color_profile)
                    self.config.enable_stream(depth_profile)

                    self.pipeline.start(self.config)
                except Exception:
                    raise Exception("can't get camera profile")

                self.status.connected = True

                while True:
                    self.status.error = False
                    self.status.message = "working normally"
                    try:
                        frame_set = self.pipeline.wait_for_frames(5000)
                        color_frame = frame_set.get_color_frame()
                        depth_frame = frame_set.get_depth_frame()

                        if not color_frame or not depth_frame:
                            raise Exception("can't get frame from gemini")
                    
                        color_data = color_frame.get_data()
                        depth_data = depth_frame.get_data()

                        color_image = np.frombuffer(color_data, dtype=np.uint8).reshape(color_frame.get_height(), color_frame.get_width(), 3)
                        depth_image = np.frombuffer(depth_data, dtype=np.uint16).reshape(depth_frame.get_height(), depth_frame.get_width())

                        h, w = depth_image.shape
                        x, y = w // 2, h // 2

                        # depth
                        self.status.depth = depth_image[y, x]

                    except Exception:
                        time.sleep(0.01)
                        continue

                    try:
                        # color image
                        self.status.color_image_base64 = self._mat_to_base64(cv.cvtColor(color_image, cv.COLOR_RGB2BGR))
                        # depth image
                        depth_normalized = cv.normalize(depth_image, None, 0, 255, cv.NORM_MINMAX)
                        depth_uint8 = depth_normalized.astype(np.uint8)
                        self.status.depth_image_base64 = self._mat_to_base64(cv.applyColorMap(depth_uint8, cv.COLORMAP_JET))

                    except Exception:
                        raise Exception("failed to encode images")
                    
            except Exception as e:
                try:
                    self.pipeline.stop()
                except Exception:
                    pass
                self.status = StatusData(
                    error=True,
                    connected=False,
                    t_x=0,
                    t_y=0,
                    t_a=0,
                    depth=0,
                    color_image_base64=None,
                    depth_image_base64=None,
                    message="connecting to camera"
                )
                print(f"Camera error: {e}, retrying...")
                time.sleep(1)

    def get_current_status(self) -> StatusData:
        return self.status