from flask import render_template, request
import base64
import numpy as np
import cv2
import re
from dotenv import load_dotenv
import os
from __init__ import create_app, socketio
import util
from Camera import Camera

app = create_app()

cam = Camera()

# Default route, serves client HTML page, returns str of html.
@app.route('/')
def index() -> str:
    return render_template('client.html')

# Socketio event when client device disconnects (reloads/closes/etc.) to remove their feed. Returns None.
@socketio.on('stop_feed')
def on_disconnect() -> None:
    cam.close_cam()


# Socketio event when a client device transmits a single frame of video feed. Returns None.
@socketio.on('video_frame')
def on_video_frame(data) -> None:
    frame_rate = data['frameRate']

    frame: str = data['image'] # frame data 
    frame: str = re.sub('^data:image/.+;base64,', '', frame) # extract base64 string
    frame: bytes = base64.b64decode(frame) # convert to bytes

    frame: np.ndarray = np.frombuffer(frame, dtype=np.uint8) # convert to np.ndarray for opencv
    frame: np.ndarray = cv2.imdecode(frame, cv2.IMREAD_COLOR)

    # with pvc.Camera(width=frame.shape[0], height=frame.shape[1], fps=20, fmt=pvc.PixelFormat.BGR) as cam:
    #     cam.send(frame)
    #     cam.sleep_until_next_frame()

    # create camera if doesnt exist or has wrong/no shape
    if not cam.exists() or not cam.same_shape(frame):
        cam.close_cam()
        cam.open_cam(frame=frame, frame_rate=frame_rate)

    cam.get_cam().send(frame)
    # cam.sleep_until_next_frame()

    data['sid'] = request.sid


if __name__ == '__main__':
    load_dotenv()
    host, port = os.getenv("HOST"), os.getenv("PORT")
    util.generate_qr(port=port)

    try: socketio.run(app, host=host, port=port, ssl_context=('cert.pem', 'key.pem')) 
    finally: cam.close_cam()