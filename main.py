from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from networktables import NetworkTables
import uvicorn
import json
import asyncio
from contextlib import asynccontextmanager
from modules import Gemini
from configs import ALLOWED_ORIGINS, HOST, PORT

Gemini()
NetworkTables.initialize(server='10.0.0.5')
table = NetworkTables.getTable('gemini')

@asynccontextmanager
async def lifespan(app: FastAPI):
    gemini = Gemini()
    
    stop_event = asyncio.Event()

    async def update_table():
        while not stop_event.is_set():
            status = gemini.get_current_status()
            table.putNumber('x', status.t_x)
            table.putNumber('y', status.t_y)
            await asyncio.sleep(0.01)

    task = asyncio.create_task(update_table())
    yield 

    stop_event.set()
    await task

app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/")
def root():
    gemini = Gemini()
    return {"message": "device server working normally", "gemini_status": gemini.get_current_status().model_dump_json()}

@app.get("/gemini/get_status")
async def get_status(websocket: WebSocket):
    try:
        websocket.accept()
        print("websocket /gemini/get_status connected")
        gemini = Gemini()
        while True:
            status = gemini.get_current_status()
            websocket.send_text(json.dumps(status.model_dump_json()))
            asyncio.wait(0.01)
    except WebSocketDisconnect:
        print("disconnected from /gemini/get_status")
    except Exception as e:
        print(str(e))

if __name__ == "__main__":
    uvicorn.run(app="main:app", host=HOST, port=PORT, reload=False)