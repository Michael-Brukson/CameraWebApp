import pyvirtualcam as pvc
import numpy as np
import cv2
import re
import base64

class Camera():
    def __init__(self):
        self.__cam: pvc.Camera = None


    def close_cam(self) -> None:
        if self.__cam is not None:
            self.__cam.close()
            self.__cam = None
            print("closed camera!")


    def open_cam(self, frame: np.ndarray, frame_rate: int) -> None: 
        # TODO: Figure out how to stop stretching frames and instead adjust camera size itself to frame
        # TODO: add support for different backends
        # TODO: the Camera class within pyvirtualcam raises a RuntimeError if the camera could not be started, but it cannot be caught at this level. Figure out a way to catch it.
        try:
            self.__cam = pvc.Camera(width=frame.shape[1], height=frame.shape[0], 
                            fps=frame_rate, fmt=pvc.PixelFormat.BGR, backend='obs')
        except RuntimeError as e:
            print(e)
            exit(-1)
        print(f"initialized camera at: ({self.__cam.width}, {self.__cam.height})!")
            

    def exists(self) -> bool:
        return not self.__cam is None
    

    def same_shape(self, frame: np.ndarray) -> bool:
        if not self.exists(): return False 
        return self.__cam.width == frame.shape[1] and self.__cam.height == frame.shape[0]
        
    def to_ndarray(self, frame: str) -> np.ndarray:
        frame: str = re.sub('^data:image/.+;base64,', '', frame) # extract base64 string
        frame: bytes = base64.b64decode(frame) # convert to bytes

        frame: np.ndarray = np.frombuffer(frame, dtype=np.uint8) # convert to np.ndarray for opencv
        frame: np.ndarray = cv2.imdecode(frame, cv2.IMREAD_COLOR)
        frame: np.ndarray = cv2.resize(frame, (frame.shape[1], frame.shape[0]), interpolation=cv2.INTER_LINEAR)
        return frame


    def send(self, frame: np.ndarray) -> None:
        self.__cam.send(frame)
        self.__cam.sleep_until_next_frame()
    

    @property
    def cam(self) -> pvc.Camera:
        return self.__cam