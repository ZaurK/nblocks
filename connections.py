# connections.py
from PySide6.QtWidgets import QGraphicsPathItem
from PySide6.QtGui import QPainterPath, QPen
from PySide6.QtCore import Qt, QPointF  # Работает в PyQt6 и PySide6


class Connection(QGraphicsPathItem):
    def __init__(self, start_port=None):
        super().__init__()
        self.setZValue(-1)  # Линии под блоками
        self.start_port = start_port
        self.end_port = None
        self.setPen(QPen(Qt.darkGreen, 2))

    def update_path(self):
        path = QPainterPath()
        if self.start_port:
            start_pos = self.start_port.scenePos() + QPointF(8, 8)
            path.moveTo(start_pos)
            if hasattr(self.end_port, 'scenePos'):  # Если это QGraphicsItem
                end_pos = self.end_port.scenePos() + QPointF(8, 8)
                path.lineTo(end_pos)
        self.setPath(path)