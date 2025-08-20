from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from networktables import NetworkTables
import uvicorn
import json
import asyncio

from modules import Gemini
from configs import ALLOWED_ORIGINS, HOST, PORT

Gemini()
NetworkTables.initialize(server='10.0.0.5')
table = NetworkTables.getTable('gemini')

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/")
def root():
    return {"message": "device server working normally", "gemini_status": Gemini().get_current_status().model_dump_json()}

@app.get("/gemini/get_status")
async def get_status(websocket: WebSocket):
    try:
        websocket.accept()
        print("websocket /gemini/get_status connected")
        while True:
            status = Gemini().get_current_status()
            websocket.send_text(json.dumps(status.model_dump_json()))
            asyncio.wait(0.01)
    except WebSocketDisconnect:
        print("disconnected from /gemini/get_status")
    except Exception as e:
        print(str(e))

if __name__ == "__main__":
    uvicorn.run(app="main:app", host=HOST, port=PORT, reload=False)