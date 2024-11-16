from picamzero import Camera

cam = Camera()
cam.start_preview()
try:
    while(True):
        pass
except KeyboardInterrupt:
    cam.take_photo("/home/Zach/Desktop/image3.jpg")

    cam.stop_preview()
    exit(0)


