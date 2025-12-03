from flask import render_template, request
from dotenv import load_dotenv
import os
import numpy as np
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
    frame: np.ndarray = cam.to_ndarray(data['image'])

    if not cam.exists() or not cam.same_shape(frame):
        cam.close_cam()
        cam.open_cam(frame=frame, frame_rate=frame_rate)

    cam.send(frame)
    data['sid'] = request.sid


if __name__ == '__main__':
    load_dotenv()
    host, port = os.getenv("HOST"), os.getenv("PORT")
    util.generate_qr(port=port)

    try: socketio.run(app, host=host, port=port, ssl_context=('cert.pem', 'key.pem')) 
    except Exception as e: print(e)
    finally: on_disconnect()