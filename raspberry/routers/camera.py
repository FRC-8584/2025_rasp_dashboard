import asyncio
from fastapi import APIRouter, WebSocket, Depends, WebSocketDisconnect
from dependencies import get_camera, get_networktable
from modules import Camera, NetworkTable

router = APIRouter(prefix="/camera", tags=["Camera"])

@router.websocket("/get_object")
async def get_object(websocket: WebSocket, camera: Camera = Depends(get_camera), nt: NetworkTable = Depends(get_networktable)):
    await websocket.accept()

    def put_nt_object_data(detected: bool, x: float, y:float, a: float):
        nt.put_number("x", x)
        nt.put_number("y", y)
        nt.put_number("a", a)
        nt.put_boolean("detected", detected)

    try:
        while True:
            result = camera.detection_result
            if result == None:
                await websocket.send_json({"error": True, "detected": False, "x": 0, "y": 0, "a": 0})
                if nt.is_connected:
                    put_nt_object_data(False, 0, 0, 0)
            else:
                await websocket.send_json({"error": False, **result.model_dump()})
                if nt.is_connected:
                    put_nt_object_data(result.detected, result.x, result.y, result.a)
            await asyncio.sleep(0.1)

    except WebSocketDisconnect:
        print("Client disconnected from /get_object")
    except Exception as e:
        print("Error in /get_object:", e)
    
@router.websocket("/get_frame")
async def get_frame(websocket: WebSocket, camera: Camera = Depends(get_camera)):
    await websocket.accept()
    try:
        while True:
            try:
                image = camera.get_corrected_frame_base64()
                if image is None:
                    await websocket.send_json({"error": True, "image": None})
                else:
                    await websocket.send_json({"error": False, "image": image})
            except Exception as e:
                print("Error getting frame:", e)
                await websocket.send_json({"error": True, "image": None})

            await asyncio.sleep(0.01)

    except WebSocketDisconnect:
        print("Client disconnected from /get_frame")
    except Exception as e:
        print("Error in /get_frame:", e)
