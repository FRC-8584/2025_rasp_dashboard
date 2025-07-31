import json
import asyncio
from fastapi import APIRouter, WebSocket, Depends, WebSocketDisconnect
from schemas import SettingsModel
from modules import Camera
from dependencies import get_camera

router = APIRouter(prefix="/settings", tags=["Settings"])

@router.websocket("/update_settings")
async def update_settings(websocket: WebSocket, camera: Camera = Depends(get_camera)):
    await websocket.accept()
    try:
        while True:
            try:
                data_str = await websocket.receive_text()
                if data_str != None:
                    data_dict = json.loads(data_str)
                    settings = SettingsModel(**data_dict)
                    camera.update_settings(settings)
                    await websocket.send_json({"error": False})
            except Exception as e:
                await websocket.send_json({"error": True})
    except WebSocketDisconnect:
        print("Client disconnected from /update_settings")