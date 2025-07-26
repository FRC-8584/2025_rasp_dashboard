import uvicorn
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from configs import HOST, PORT, ALLOWED_ORIGINS
from contextlib import asynccontextmanager
from instances import get_camera, get_networktable
from routers import camera_router, settings_router, status_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    camera = get_camera()
    nt = get_networktable()

    async def run():
        def put_nt_object_data(detected: bool, x: float, y: float, a: float):
            nt.put_number("x", x)
            nt.put_number("y", y)
            nt.put_number("a", a)
            nt.put_boolean("detected", detected)

        running = True
        while running:
            result = camera.process()
            if nt.is_connected:
                if result is None:
                    put_nt_object_data(False, 0, 0, 0)
                else:
                    put_nt_object_data(result.detected, result.x, result.y, result.a)
            await asyncio.sleep(0.1)

    task = asyncio.create_task(run())

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
async def root():
    return {"message": "Running ヽ(･∀･)ﾉ"}

if __name__ == "__main__":
    uvicorn.run(app="main:app", host=HOST, port=PORT, reload=True)