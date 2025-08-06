import uvicorn
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from routers import camera_router
from configs import HOST, PORT, ALLOWED_ORIGINS
from modules import Camera
from dependencies import get_camera

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(camera_router)

@app.get("/")
async def root(camera: Camera = Depends(get_camera)):
    return {"message": "Running ヽ(･∀･)ﾉ, camera connection: "+str(camera.camera_connected)}

if __name__ == "__main__":
    uvicorn.run(app="main:app", host=HOST, port=PORT, reload=True)