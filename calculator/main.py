from PySide6.QtWidgets import (QApplication, QMainWindow, QGraphicsView,
                               QGraphicsScene, QGraphicsRectItem, QGraphicsTextItem,
                               QGraphicsLineItem, QGraphicsEllipseItem)
from PySide6.QtCore import Qt, QPointF, QLineF, QTimer
from PySide6.QtGui import QBrush, QPen, QColor


class Connection(QGraphicsLineItem):
    def __init__(self, start_connector, end_connector):
        super().__init__()
        self.start_connector = start_connector
        self.end_connector = end_connector
        self.update_position()
        self.setPen(QPen(Qt.black, 2))
        self.setAcceptHoverEvents(True)
        self.setFlag(QGraphicsLineItem.ItemIsSelectable)

    def update_position(self):
        self.setLine(QLineF(
            self.start_connector.scenePos(),
            self.end_connector.scenePos()
        ))

    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            self.delete_connection()
        else:
            super().mousePressEvent(event)

    def delete_connection(self):
        # Удаляем ссылку на соединение у коннекторов
        if self in self.start_connector.connections:
            self.start_connector.connections.remove(self)
        if self in self.end_connector.connections:
            self.end_connector.connections.remove(self)

        # Удаляем линию со сцены
        scene = self.scene()
        if scene:
            scene.removeItem(self)


class Connector(QGraphicsEllipseItem):
    def __init__(self, x, y, parent_block):
        super().__init__(-5, -5, 10, 10, parent_block)
        self.setPos(x, y)
        self.setBrush(QBrush(Qt.red))
        self.setPen(QPen(Qt.black, 1))
        self.setAcceptHoverEvents(True)
        self.connections = []
        self.parent_block = parent_block

    def add_connection(self, connection):
        self.connections.append(connection)

    def update_connections(self):
        for connection in self.connections:
            connection.update_position()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.scene().start_connector = self
            self.scene().temp_line = QGraphicsLineItem(QLineF(self.scenePos(), self.scenePos()))
            self.scene().temp_line.setPen(QPen(Qt.black, 2, Qt.DashLine))
            self.scene().addItem(self.scene().temp_line)
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if hasattr(self.scene(), 'temp_line'):
            mouse_pos = self.mapToScene(event.pos())
            self.scene().temp_line.setLine(QLineF(
                self.scene().start_connector.scenePos(),
                mouse_pos
            ))

            # Подсветка ближайших коннекторов
            for item in self.scene().items():
                if isinstance(item, Connector) and item != self.scene().start_connector:
                    dist = QLineF(mouse_pos, item.scenePos()).length()
                    item.setBrush(QBrush(Qt.yellow if dist < 30 else Qt.red))

    def mouseReleaseEvent(self, event):
        if event.button() != Qt.LeftButton:
            return

        scene = self.scene()
        if hasattr(scene, 'temp_line'):
            scene.removeItem(scene.temp_line)
            mouse_pos = event.scenePos()

            # Поиск ближайшего коннектора
            nearest = None
            min_dist = 30  # Радиус примагничивания

            for item in scene.items(mouse_pos):
                if isinstance(item, Connector) and item != scene.start_connector:
                    dist = QLineF(mouse_pos, item.scenePos()).length()
                    if dist < min_dist:
                        min_dist = dist
                        nearest = item

            if nearest:
                # Создание соединения
                connection = Connection(scene.start_connector, nearest)
                scene.addItem(connection)

                # Визуальная обратная связь
                nearest.setBrush(QBrush(Qt.green))
                QTimer.singleShot(300, lambda: nearest.setBrush(QBrush(Qt.red)))

                # Добавляем соединение к обоим коннекторам
                scene.start_connector.add_connection(connection)
                nearest.add_connection(connection)

            # Восстанавливаем цвет всех коннекторов
            for item in scene.items():
                if isinstance(item, Connector):
                    item.setBrush(QBrush(Qt.red))

            del scene.temp_line
            del scene.start_connector


class Block(QGraphicsRectItem):
    def __init__(self, x, y, text):
        super().__init__(0, 0, 100, 60)
        self.setPos(x, y)
        self.setBrush(QBrush(QColor(200, 230, 255)))
        self.setPen(QPen(Qt.black, 2))
        self.setFlag(QGraphicsRectItem.ItemIsMovable)
        self.setFlag(QGraphicsRectItem.ItemSendsScenePositionChanges)

        self.text_item = QGraphicsTextItem(text, self)
        self.text_item.setPos(10, 10)

        self.output_connector = Connector(100, 30, self)
        self.input_connector = Connector(0, 30, self)

    def itemChange(self, change, value):
        if change == QGraphicsRectItem.ItemPositionHasChanged:
            self.output_connector.update_connections()
            self.input_connector.update_connections()
        return super().itemChange(change, value)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Блоки с удалением соединений")
        self.setGeometry(100, 100, 600, 400)

        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.setCentralWidget(self.view)

        self.block1 = Block(50, 100, "Блок 1")
        self.block2 = Block(300, 100, "Блок 2")
        self.block3 = Block(175, 200, "Блок 3")

        self.scene.addItem(self.block1)
        self.scene.addItem(self.block2)
        self.scene.addItem(self.block3)


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()