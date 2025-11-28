import pyvirtualcam as pvc
import numpy as np

class Camera():
    def __init__(self):
        self.__cam: pvc.Camera = None

    def close_cam(self) -> None:
        if self.__cam is not None:
            self.__cam.close()
            self.__cam = None
            print("closed camera!")


    def open_cam(self, frame: np.ndarray, frame_rate: int) -> None: 
        try:
            # TODO: add support for different backends
            self.__cam = pvc.Camera(width=frame.shape[1], height=frame.shape[0], 
                                fps=frame_rate, fmt=pvc.PixelFormat.BGR, backend='obs')
            print("initialized camera!")
        except RuntimeError as e:
            print(e)
            exit(-1)


    def exists(self) -> bool:
        return not self.__cam is None
    
    def same_shape(self, frame: np.ndarray) -> bool:
        return not (self.__cam.width != frame.shape[1] or self.__cam.height != frame.shape[0])
    
    @property
    def cam(self) -> pvc.Camera:
        return self.__cam