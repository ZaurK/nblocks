# blocks/base_block.py
from PySide6.QtWidgets import QGraphicsRectItem, QGraphicsTextItem
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPen, QBrush


class BaseBlock(QGraphicsRectItem):
    def __init__(self, title, width=150, height=100):
        super().__init__(0, 0, width, height)
        self.setFlags(QGraphicsRectItem.ItemIsMovable |
                      QGraphicsRectItem.ItemIsSelectable)

        self.setBrush(QBrush(QColor(173, 216, 230)))
        self.setPen(QPen(Qt.darkBlue, 2))

        self.title = QGraphicsTextItem(title, self)
        self.title.setPos(10, 5)

        self.input_ports = []
        self.output_ports = []

    def add_input_port(self, name):
        port = QGraphicsRectItem(0, 30 + len(self.input_ports) * 25, 16, 16, self)
        port.setBrush(QBrush(Qt.red))
        port.setPos(-8, 30 + len(self.input_ports) * 25)  # Явное позиционирование
        self.input_ports.append({"name": name, "item": port})

    def add_output_port(self, name):
        port = QGraphicsRectItem(0, 30 + len(self.output_ports) * 25, 16, 16, self)
        port.setBrush(QBrush(Qt.green))
        port.setPos(self.rect().width() - 8, 30 + len(self.output_ports) * 25)
        self.output_ports.append({"name": name, "item": port})