import websockets
import asyncio
import json
from pydantic import BaseModel
from typing import Optional
import cv2 as cv
import numpy as np
import base64

class FrameMessage(BaseModel):
    error: bool
    message: str
    image: Optional[str]

frame_message: FrameMessage = None

async def connect_websocket():
    uri = "ws://localhost:7000/camera/get_frame"

    async with websockets.connect(uri) as websocket:
        print("WebSocket connected.")
        while True:
            try:
                message = await websocket.recv()
                data = json.loads(message)
                frame_msg = FrameMessage.model_validate_json(data) 

                if not frame_msg.error and frame_msg.image:
                    img_data = base64.b64decode(frame_msg.image)
                    nparr = np.frombuffer(img_data, np.uint8)
                    img = cv.imdecode(nparr, cv.IMREAD_COLOR)

                    if img is not None:
                        cv.imshow("WebSocket Image", img)
                        if cv.waitKey(1) & 0xFF == ord('q'):
                            break
                else:
                    print("Error:", frame_msg.message)

            except Exception as e:
                print("Error receiving or displaying image:", e)
                await asyncio.sleep(1)

    cv.destroyAllWindows()

asyncio.run(connect_websocket())