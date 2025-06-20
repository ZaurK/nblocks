# blocks/camera_block.py
from .base_block import BaseBlock
import cv2


class CameraBlock(BaseBlock):
    def __init__(self):
        super().__init__("Camera")
        self.add_output_port("Video Out")

    def execute(self):
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        cap.release()
        return frame if ret else None