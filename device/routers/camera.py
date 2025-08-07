import asyncio
from fastapi import APIRouter, WebSocket, Depends, WebSocketDisconnect
import time
from dependencies import get_camera
from modules import Camera
from schemas import FrameMessage

router = APIRouter(prefix="/camera", tags=["Camera"])

latency = 0

@router.websocket("/get_frame")
async def get_frame(websocket: WebSocket, camera: Camera = Depends(get_camera)):
    await websocket.accept()
    try:
        while True:
            try:
                global latency
                frame_message = camera.get_frame_data()
                frame_message.latency = latency
                
                last_time = time.time()
                await websocket.send_json(frame_message.model_dump_json())
                await websocket.receive_text()
                latency = ((time.time() - last_time) / 2 * 1000) 
                    
            except Exception as e:
                await websocket.send_json(FrameMessage(error=True, message=str(e), image=None, latency=time.time()).model_dump_json())

            await asyncio.sleep(0.01)

    except WebSocketDisconnect:
        print("Client disconnected from /get_frame")
    except Exception as e:
        print("Error in /get_frame:", e)