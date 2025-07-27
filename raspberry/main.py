import uvicorn
import asyncio
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from configs import HOST, PORT, ALLOWED_ORIGINS
from contextlib import asynccontextmanager
from dependencies import get_camera, get_networktable
from routers import camera_router, settings_router, status_router
from modules import Camera, NetworkTable

async def background_process(camera: Camera, nt: NetworkTable):
    def put_nt_object_data(detected: bool, x: float, y: float, a: float):
        nt.put_number("x", x)
        nt.put_number("y", y)
        nt.put_number("a", a)
        nt.put_boolean("detected", detected)

    while True:
        result = await asyncio.to_thread(camera.process)
        if nt.is_connected:
            if result is None:
                put_nt_object_data(False, 0, 0, 0)
            else:
                put_nt_object_data(result.detected, result.x, result.y, result.a)
        await asyncio.sleep(0.01)

@asynccontextmanager
async def lifespan(app: FastAPI):
    camera = get_camera()
    nt = get_networktable()
    
    task = asyncio.create_task(background_process(camera, nt))
    yield
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass

app = FastAPI(lifespan=lifespan)

app.include_router(camera_router)
app.include_router(settings_router)
app.include_router(status_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root(camera: Camera = Depends(get_camera), nt: NetworkTable = Depends(get_networktable)):
    return {"message": "Running ヽ(･∀･)ﾉ, camera connection: "+str(camera.connected)+", nt connection: "+ str(nt.is_connected)}

if __name__ == "__main__":
    uvicorn.run(app="main:app", host=HOST, port=PORT, reload=True)