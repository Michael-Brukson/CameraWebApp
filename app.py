from flask import Flask, render_template
from __init__ import create_app, socketio, init_dependencies
from dotenv import load_dotenv
from Camera import Camera
import numpy as np
import util
import os
import logging

logger: logging.Logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

init_dependencies()
app: Flask = create_app()

cam: Camera = Camera()

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
def on_video_frame(data):
    options: dict = data.get('options')
    frame_rate = int(data.get('frameRate', 24))
    frame: np.ndarray = cam.to_ndarray(data['image'])

    if not cam.exists() or not cam.same_shape(frame):
        cam.close_cam()
        cam.open_cam(frame=frame, frame_rate=frame_rate)

    cam.send(frame, options)
    return {'ok': True}

@util.log_func
def main() -> None:
    load_dotenv()
    host = os.getenv("HOST", "0.0.0.0")
    port = os.getenv("PORT", "443")
    util.generate_qr(host=host, port=port)

    try: socketio.run(app, host=host, port=int(port), ssl_context=('cert.pem', 'key.pem')) 
    except Exception as e: logger.info(e)
    finally: on_disconnect()

if __name__ == '__main__':
    main()