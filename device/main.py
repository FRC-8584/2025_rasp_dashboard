from modules import Camera

camera = Camera()

while True:
    status = camera.get_current_status()
    if status.connected:
        print(status.depth)