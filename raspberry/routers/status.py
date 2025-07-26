import asyncio
from fastapi import APIRouter, WebSocket, Depends, WebSocketDisconnect
from schemas import SettingsModel
from instances import get_camera, get_networktable
from modules import Camera, NetworkTable
from configs import CAMERA_RETRY_INTERVAL

router = APIRouter(prefix="/status", tags=["Status"])

@router.websocket("/camera_connection")
async def is_camera_connected(websocket: WebSocket, camera: Camera = Depends(get_camera)):
    await websocket.accept()
    retry_counter = 0
    try:
        while True:
            if not camera.connected:
                retry_counter += 1
                await websocket.send_json({
                    "connected": False,
                    "message": f"Can't connect to camera. (Retry again in {retry_counter} seconds)"
                })
                if retry_counter > CAMERA_RETRY_INTERVAL:
                    retry_counter = 0
            else:
                retry_counter = 0
                await websocket.send_json({"connected": True})

            await asyncio.sleep(1)
    except WebSocketDisconnect:
        print("Client disconnected from /camera_connection")

@router.websocket("/error")
async def error(websocket: WebSocket, camera: Camera = Depends(get_camera), nt: NetworkTable = Depends(get_networktable)):
    await websocket.accept()
    try:
        while True:
            camera_error = not camera.connected or not camera.corrected_frame
            networktable_error = not nt.is_connected
            any_error = camera_error or networktable_error
            messages = []
            if camera_error:
                if not camera.connected:
                    messages.append("Camera not connected.")
                elif not camera.corrected_frame:
                    messages.append("Camera has no valid frame.")
            if networktable_error:
                messages.append("NetworkTable not connected.")

            await websocket.send_json({
                "error": any_error,
                "camera_error": camera_error,
                "networktable_error": networktable_error,
                "message": " | ".join(messages) if messages else "No error."
            })
            await asyncio.sleep(0.1)

    except WebSocketDisconnect:
        print("Client disconnected from /error")
    