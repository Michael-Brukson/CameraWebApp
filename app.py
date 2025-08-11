from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room
import pyvirtualcam as pvc
import base64
import numpy as np
import cv2
import re


app = Flask(__name__)
socketio = SocketIO(app)

cam: pvc.Camera = None # pyvirtualcam instance


# Default route, serves client HTML page, returns str of html.
@app.route('/')
def index() -> str:
    return render_template('client.html')


# Socketio event when client device disconnects (reloads/closes/etc.) to remove their feed. Returns None.
@socketio.on('disconnect')
def on_disconnect() -> None:
    # emits 'user_disconnected' and passes socket id of disconnected client
    emit('user_disconnected', {'sid': request.sid})
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

    frame = data['image'] # frame data 
    frame = re.sub('^data:image/.+;base64,', '', frame) # extract base64 string
    frame = base64.b64decode(frame) # convert to bytes

    frame = np.frombuffer(frame, dtype=np.uint8) # convert to np.ndarray for opencv
    frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)

    if cam is None or cam.width != frame.shape[1]:
        cam = pvc.Camera(width=frame.shape[0], height=frame.shape[1], fps=20, fmt=pvc.PixelFormat.BGR)

    # send frame to camera
    cam.send(frame)

    data['sid'] = request.sid
    emit('frame', data, room=request.sid)


if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=443, ssl_context=('cert.pem', 'key.pem'))