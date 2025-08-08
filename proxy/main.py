from fastapi import FastAPI, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import websockets
import asyncio
import json
import uvicorn
from modules import Processor
from schemas import FrameMessage
from dependencies import get_processor
from configs import HOST, PORT, ALLOWED_ORIGINS

async def websocket_task():
    uri = "ws://127.0.0.1:7000/camera/get_frame"
    processor = get_processor()

    while True:
        try:
            print(f"Trying to connect to {uri} ...")
            async with websockets.connect(uri) as websocket:
                print("WebSocket /camera/get_frame connected.")
                while True:
                    try:
                        message = await websocket.recv()
                        await websocket.send(json.dumps({"message": "pong"}))
                        data = json.loads(message)
                        frame_msg = FrameMessage.model_validate_json(data)
                        processor.update_status(frame_msg.message, frame_msg.latency)

                        if not frame_msg.error and frame_msg.image:
                            processor.process(frame_msg.image)
                        else:
                            raise Exception("Error from server:", frame_msg.message)

                    except websockets.ConnectionClosed:
                        print("WebSocket connection closed by server.")
                        break 
                    except Exception as e:
                        print("Error during message handling:", e)
                        await asyncio.sleep(1)

        except Exception as e:
            print(f"Connection failed: {e}")
            await asyncio.sleep(3) 

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/test/image")
def get_image_base64(processor: Processor = Depends(get_processor)):
    b64_string = processor.get_corrected_frame_base64()
    return JSONResponse(content={"image": b64_string})

@app.get("/")
async def root():
    return {"message": "You got wrong way ヽ(･∀･)ﾉ"}

def start():
    loop = asyncio.get_event_loop()

    loop.create_task(websocket_task())

    config = uvicorn.Config(app, host="0.0.0.0", port=8000, reload=False)
    server = uvicorn.Server(config)

    loop.run_until_complete(server.serve())

if __name__ == "__main__":
    start()