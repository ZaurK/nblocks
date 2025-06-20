# blocks/grayscale_block.py
from .base_block import BaseBlock
import cv2


class GrayscaleBlock(BaseBlock):
    def __init__(self):
        super().__init__("Grayscale")
        self.add_input_port("Image In")
        self.add_output_port("Image Out")

    def execute(self, input_frame):
        return cv2.cvtColor(input_frame, cv2.COLOR_BGR2GRAY)