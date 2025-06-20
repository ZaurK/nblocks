# blocks/display_block.py
from .base_block import BaseBlock
import cv2


class DisplayBlock(BaseBlock):
    def __init__(self):
        super().__init__("Display")
        self.add_input_port("Image In")

    def execute(self, input_frame):
        cv2.imshow("Processed Image", input_frame)
        cv2.waitKey(1)
        return input_frame