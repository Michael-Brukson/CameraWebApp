from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room
import pyvirtualcam as pvc
import base64
import numpy as np
import cv2
import re

app = Flask(__name__)
socketio = SocketIO(app)

SERVER: str = 'server'
cam = None

@app.route('/')
def index() -> str:
    return render_template('client.html')

@app.route('/server')
def server() -> str:
    return render_template('server.html')

@socketio.on('join_server')
def on_join_server() -> None:
    join_room(SERVER)

@socketio.on('disconnect')
def on_disconnect() -> None:
    emit('user_disconnected', {'sid': request.sid}, room=SERVER)

@socketio.on('video_frame')
def on_video_frame(data) -> None:
    global cam

    frame = data['image']
    frame = re.sub('^data:image/.+;base64,', '', frame) # str
    frame = base64.b64decode(frame) # convert to bytes

    frame = np.frombuffer(frame, dtype=np.uint8) # convert to np.ndarray
    frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)

    if cam is None:
        cam = pvc.Camera(width=frame.shape[1], height=frame.shape[0], fps=20, fmt=pvc.PixelFormat.BGR)

    cam.send(frame)

    data['sid'] = request.sid
    emit('local_frame', data, room=request.sid)
    emit('server_frame', data, room=SERVER) 

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=443, ssl_context=('cert.pem', 'key.pem'))