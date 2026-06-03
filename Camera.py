import pyvirtualcam as pvc
import numpy as np
import cv2
import re
import base64
import logging
from typing import Optional

logger: logging.Logger = logging.getLogger(__name__)

class Camera():
    def __init__(self):
        self.cam: Optional[pvc.Camera] = None


    # Function to close camera, only if it exists
    def close_cam(self) -> None:
        if self.exists():
            self.cam.close()
            self.cam = None
            print("closed camera!")


    # TODO: add support for different backends
    # TODO: the Camera class within pyvirtualcam raises a RuntimeError if the camera could not be started, but it cannot be caught at this level. Figure out a way to catch it.
    # Function to create a camera with a given frame and frame rate
    def open_cam(self, frame: np.ndarray, frame_rate: int) -> None: 
        try:
            self.cam = pvc.Camera(width=frame.shape[1], height=frame.shape[0], 
                            fps=frame_rate, fmt=pvc.PixelFormat.BGR, backend='obs', print_fps=False)
            
        except RuntimeError as e:
            print(e)
            exit(-1)
        logger.info(f"initialized camera at: ({self.cam.width}, {self.cam.height})!")
            

    # Function to return if camera has been initialized
    def exists(self) -> bool:
        return not self.cam is None


    # Function to check if cameras current shape is equal to that of the frame.
    def same_shape(self, frame: np.ndarray) -> bool:
        if not self.exists(): return False 
        # only compare width and height, ignore depth of ndarray
        return self.shape == frame.shape[0:2]
        

    # Function to convert frame base64 string data into ndarray.
    def to_ndarray(self, frame: str) -> np.ndarray:
        frame = re.sub('^data:image/.+;base64,', '', frame) # extract base64 string
        frame: bytes = base64.b64decode(frame) # convert to bytes

        frame: np.ndarray = np.frombuffer(frame, dtype=np.uint8) # convert to np.ndarray for opencv
        frame: np.ndarray = cv2.imdecode(frame, cv2.IMREAD_COLOR)
        # frame: np.ndarray = cv2.resize(frame, (frame.shape[1], frame.shape[0]), interpolation=cv2.INTER_LINEAR)
        return frame


    # Function to send frame to camera, with options.
    def send(self, frame: np.ndarray, options: dict) -> None:
        if not self.exists(): pass
        # TODO: Make setting on phone/computer to show fps counter
        # TODO: add other statistics settings to show
        # TODO: add settings for phone
        if options['showFPS']:
            cv2.putText(frame, f'FPS: {self.cam.current_fps:.2f}', (50,50), cv2.FONT_HERSHEY_COMPLEX, 1, (0,255,0), 2)
        # frame = cv2.flip(frame, 1)
        self.cam.send(frame)
        self.cam.sleep_until_next_frame()


    # Property to access current shape of camera
    @property
    def shape(self) -> tuple[int, int] | None:
        if not self.exists(): return None
        return (self.cam.height, self.cam.width)
            