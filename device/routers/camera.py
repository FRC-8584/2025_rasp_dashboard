import asyncio
from fastapi import APIRouter, WebSocket, Depends, WebSocketDisconnect
import time
from dependencies import get_camera
from modules import Camera
from schemas import FrameMessage

router = APIRouter(prefix="/camera", tags=["Camera"])

@router.websocket("/get_frame")
async def get_frame(websocket: WebSocket, camera: Camera = Depends(get_camera)):
    await websocket.accept()
    try:
        while True:
            try:
                frame_message = camera.get_frame_data()
                await websocket.send_json(frame_message.model_dump_json())
            except Exception as e:
                await websocket.send_json(FrameMessage(error=True, message=str(e), image=None).model_dump_json())

            await asyncio.sleep(0.01)

    except WebSocketDisconnect:
        print("Client disconnected from /get_frame")
    except Exception as e:
        print("Error in /get_frame:", e)