from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room
import pyvirtualcam as pvc
import base64
import numpy as np
import cv2
import re
import os
import util

app = Flask(__name__)
socketio = SocketIO(app)

cam: pvc.Camera = None # pyvirtualcam instance


# Default route, serves client HTML page, returns str of html.
@app.route('/')
def index() -> str:
    return render_template('client.html')


# Socketio event when client device disconnects (reloads/closes/etc.) to remove their feed. Returns None.
@socketio.on('stop_feed')
def on_disconnect() -> None:
    close_cam()
 

def close_cam() -> None:
    global cam
    if cam is not None:
        cam.close()
        cam = None


# Socketio event when a client device transmits a single frame of video feed. Returns None.
@socketio.on('video_frame')
def on_video_frame(data) -> None:
    global cam

    frame_rate = data['frameRate']

    frame: str = data['image'] # frame data 
    frame: str = re.sub('^data:image/.+;base64,', '', frame) # extract base64 string
    frame: bytes = base64.b64decode(frame) # convert to bytes

    frame: np.ndarray = np.frombuffer(frame, dtype=np.uint8) # convert to np.ndarray for opencv
    frame: np.ndarray = cv2.imdecode(frame, cv2.IMREAD_COLOR)

    # with pvc.Camera(width=frame.shape[0], height=frame.shape[1], fps=20, fmt=pvc.PixelFormat.BGR) as cam:
    #     cam.send(frame)
    #     cam.sleep_until_next_frame()

    # create camera if doesnt exist or has no shape
    if cam is None or cam.width != frame.shape[1] or cam.height != frame.shape[0]:
        close_cam()
        try:
            # TODO: add support for different backends
            cam = pvc.Camera(width=frame.shape[1], height=frame.shape[0], 
                             fps=frame_rate, fmt=pvc.PixelFormat.BGR, backend='obs')
            print("initialized camera!")
        except RuntimeError as e:
            print(e)
            exit(-1)

    cam.send(frame)
    # cam.sleep_until_next_frame()

    data['sid'] = request.sid


if __name__ == '__main__':
    host, port = "0.0.0.0", 443
    if not os.path.exists("key.pem") or not os.path.exists("cert.pem"):
        print("no self certification found, generating now...")
        util.generate_key_cert_pem()

    try: socketio.run(app, host=host, port=port, ssl_context=('cert.pem', 'key.pem')) 
    finally: close_cam()