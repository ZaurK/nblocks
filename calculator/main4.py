import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QGraphicsView, QGraphicsScene,
    QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QLabel,
    QGraphicsRectItem, QGraphicsTextItem, QGraphicsEllipseItem, QGraphicsLineItem
)
from PySide6.QtGui import QPainter, QPen, QColor, QBrush, QPainterPath
from PySide6.QtCore import Qt, QPointF, QLineF, QTimer, QRectF


class Connection(QGraphicsLineItem):
    def __init__(self, start_connector, end_connector=None):
        super().__init__()
        self.start_connector = start_connector
        self.end_connector = end_connector
        self.setPen(QPen(Qt.black, 2))
        self.setAcceptHoverEvents(True)
        self.setFlag(QGraphicsLineItem.ItemIsSelectable)
        self.setFlag(QGraphicsLineItem.ItemIsFocusable)

        if end_connector:
            self.update_position()
        else:
            self.setLine(QLineF(start_connector.scenePos(), start_connector.scenePos()))

    def paint(self, painter, option, widget=None):
        if self.isSelected():
            painter.setPen(QPen(Qt.red, 3, Qt.DashLine))
        else:
            painter.setPen(QPen(Qt.black, 2))
        painter.drawLine(self.line())

    def update_position(self):
        if self.start_connector and self.end_connector:
            self.setLine(QLineF(
                self.start_connector.scenePos(),
                self.end_connector.scenePos()
            ))
        elif self.start_connector:
            start_pos = self.start_connector.scenePos()
            self.setLine(QLineF(start_pos, start_pos))

    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            self.delete_connection()
        else:
            super().mousePressEvent(event)

    def delete_connection(self):
        try:
            if hasattr(self, 'start_connector') and self.start_connector:
                self.start_connector.connections.remove(self)
            if hasattr(self, 'end_connector') and self.end_connector:
                self.end_connector.connections.remove(self)

            if self.scene():
                self.scene().removeItem(self)
        except Exception as e:
            print(f"Error deleting connection: {str(e)}")


class Connector(QGraphicsEllipseItem):
    def __init__(self, x, y, parent_block, is_output=True):
        super().__init__(-5, -5, 10, 10, parent_block)
        self.setPos(x, y)
        self.setBrush(QBrush(Qt.red))
        self.setPen(QPen(Qt.black, 1))
        self.setAcceptHoverEvents(True)
        self.setFlag(QGraphicsEllipseItem.ItemSendsScenePositionChanges)
        self.connections = []
        self.parent_block = parent_block
        self.is_output = is_output

    def add_connection(self, connection):
        self.connections.append(connection)

    def update_connections(self):
        for connection in self.connections:
            connection.update_position()

    def itemChange(self, change, value):
        if change == QGraphicsEllipseItem.ItemPositionHasChanged:
            self.update_connections()
        return super().itemChange(change, value)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            scene = self.scene()
            scene.start_connector = self
            scene.temp_connection = Connection(self)
            scene.addItem(scene.temp_connection)
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        scene = self.scene()
        if hasattr(scene, 'temp_connection'):
            mouse_pos = self.mapToScene(event.pos())
            line = scene.temp_connection.line()
            line.setP2(mouse_pos)
            scene.temp_connection.setLine(line)

            for item in scene.items(mouse_pos):
                if isinstance(item, Connector) and item != scene.start_connector:
                    if (item.is_output != scene.start_connector.is_output and
                            item.parent_block != scene.start_connector.parent_block):
                        dist = QLineF(mouse_pos, item.scenePos()).length()
                        item.setBrush(QBrush(Qt.yellow if dist < 30 else Qt.red))

    def mouseReleaseEvent(self, event):
        if event.button() != Qt.LeftButton:
            return

        scene = self.scene()
        if not hasattr(scene, 'temp_connection'):
            return

        mouse_pos = event.scenePos()
        nearest = None
        min_dist = 30

        for item in scene.items(mouse_pos):
            if (isinstance(item, Connector) and item != scene.start_connector and
                    item.is_output != scene.start_connector.is_output and
                    item.parent_block != scene.start_connector.parent_block):

                dist = QLineF(mouse_pos, item.scenePos()).length()
                if dist < min_dist:
                    min_dist = dist
                    nearest = item

        if nearest:
            scene.removeItem(scene.temp_connection)
            connection = Connection(scene.start_connector, nearest)
            scene.addItem(connection)
            scene.start_connector.add_connection(connection)
            nearest.add_connection(connection)
            nearest.setBrush(QBrush(Qt.green))
            QTimer.singleShot(300, lambda: nearest.setBrush(QBrush(Qt.red)))
        else:
            scene.removeItem(scene.temp_connection)

        for item in scene.items():
            if isinstance(item, Connector):
                item.setBrush(QBrush(Qt.red))

        del scene.temp_connection
        del scene.start_connector


class Block(QGraphicsRectItem):
    def __init__(self, title, block_type):
        super().__init__(0, 0, 120, 80)
        self.setBrush(QBrush(QColor(200, 230, 255)))
        self.setPen(QPen(Qt.black, 2))
        self.setFlag(QGraphicsRectItem.ItemIsMovable)
        self.setFlag(QGraphicsRectItem.ItemIsSelectable)  # Добавляем возможность выделения
        self.setFlag(QGraphicsRectItem.ItemSendsScenePositionChanges)

        self.title = QGraphicsTextItem(title, self)
        self.title.setPos(10, 10)
        self.block_type = block_type

        self.input_connectors = []
        self.output_connectors = []

        if block_type == "camera":
            self.output_connectors.append(Connector(120, 40, self, is_output=True))
        elif block_type == "grayscale":
            self.input_connectors.append(Connector(0, 30, self, is_output=False))
            self.output_connectors.append(Connector(120, 30, self, is_output=True))
        elif block_type == "display":
            self.input_connectors.append(Connector(0, 40, self, is_output=False))

    def paint(self, painter, option, widget=None):
        # Изменяем цвет рамки при выделении
        if self.isSelected():
            painter.setPen(QPen(Qt.red, 3))
        else:
            painter.setPen(QPen(Qt.black, 2))
        painter.setBrush(self.brush())
        painter.drawRect(self.rect())

    def itemChange(self, change, value):
        if change == QGraphicsRectItem.ItemPositionHasChanged:
            for connector in self.input_connectors + self.output_connectors:
                connector.update_connections()
        return super().itemChange(change, value)

    def delete_block(self):
        # Собираем все соединения, связанные с этим блоком
        all_connections = []
        for connector in self.input_connectors + self.output_connectors:
            all_connections.extend(connector.connections.copy())

        # Удаляем все соединения
        for connection in all_connections:
            connection.delete_connection()

        # Удаляем сам блок со сцены
        if self.scene():
            self.scene().removeItem(self)


class BlockEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Advanced Block Editor")
        self.setGeometry(100, 100, 1000, 700)

        self.scene = QGraphicsScene(self)
        self.scene.setSceneRect(0, 0, 900, 600)

        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)

        self.tool_panel = QWidget()
        self.tool_layout = QVBoxLayout()

        self.btn_add_camera = QPushButton("Add Camera")
        self.btn_add_grayscale = QPushButton("Add Grayscale")
        self.btn_add_display = QPushButton("Add Display")
        self.btn_run = QPushButton("Run Pipeline")
        self.btn_clear = QPushButton("Clear All")

        self.tool_layout.addWidget(QLabel("Blocks:"))
        self.tool_layout.addWidget(self.btn_add_camera)
        self.tool_layout.addWidget(self.btn_add_grayscale)
        self.tool_layout.addWidget(self.btn_add_display)
        self.tool_layout.addStretch()
        self.tool_layout.addWidget(self.btn_run)
        self.tool_layout.addWidget(self.btn_clear)
        self.tool_panel.setLayout(self.tool_layout)
        self.tool_panel.setFixedWidth(150)

        main_widget = QWidget()
        main_layout = QHBoxLayout()
        main_layout.addWidget(self.tool_panel)
        main_layout.addWidget(self.view)
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        self.blocks = []

        self.btn_add_camera.clicked.connect(self.add_camera_block)
        self.btn_add_grayscale.clicked.connect(self.add_grayscale_block)
        self.btn_add_display.clicked.connect(self.add_display_block)
        self.btn_run.clicked.connect(self.execute_pipeline)
        self.btn_clear.clicked.connect(self.clear_scene)

        self.statusBar().showMessage("Ready")
        self.setup_scene_grid()

    def setup_scene_grid(self):
        pen = QPen(QColor(220, 220, 220), 1, Qt.DotLine)
        for x in range(0, 901, 50):
            self.scene.addLine(x, 0, x, 600, pen)
        for y in range(0, 601, 50):
            self.scene.addLine(0, y, 900, y, pen)

    def add_camera_block(self):
        block = Block("Camera", "camera")
        block.setPos(100, 100)
        self.scene.addItem(block)
        self.blocks.append(block)
        self.statusBar().showMessage("Added Camera Block", 2000)

    def add_grayscale_block(self):
        block = Block("Grayscale", "grayscale")
        block.setPos(300, 100)
        self.scene.addItem(block)
        self.blocks.append(block)
        self.statusBar().showMessage("Added Grayscale Block", 2000)

    def add_display_block(self):
        block = Block("Display", "display")
        block.setPos(500, 100)
        self.scene.addItem(block)
        self.blocks.append(block)
        self.statusBar().showMessage("Added Display Block", 2000)

    def clear_scene(self):
        self.scene.clear()
        self.blocks = []
        self.setup_scene_grid()
        self.statusBar().showMessage("Scene cleared", 2000)

    def execute_pipeline(self):
        camera_block = next((b for b in self.blocks if b.block_type == "camera"), None)

        if not camera_block:
            self.statusBar().showMessage("Error: No Camera Block found!", 3000)
            return

        connected_blocks = self.find_connected_blocks(camera_block)
        if connected_blocks:
            chain = " -> ".join([b.block_type for b in connected_blocks])
            self.statusBar().showMessage(f"Executing: camera -> {chain}", 3000)
        else:
            self.statusBar().showMessage("Camera block is not connected", 3000)

    def find_connected_blocks(self, start_block):
        visited = set()
        result = []
        current_block = start_block

        while current_block:
            next_block = None
            for connector in current_block.output_connectors:
                for connection in connector.connections:
                    if connection.end_connector and connection.end_connector.parent_block not in visited:
                        next_block = connection.end_connector.parent_block
                        break
                if next_block:
                    break

            if next_block and next_block not in visited:
                visited.add(next_block)
                result.append(next_block)
                current_block = next_block
            else:
                current_block = None

        return result

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            self.delete_selected_items()
        else:
            super().keyPressEvent(event)

    def delete_selected_items(self):
        # Сначала собираем все выделенные элементы
        selected_items = self.scene.selectedItems()

        for item in selected_items:
            if isinstance(item, Block):
                item.delete_block()
                if item in self.blocks:
                    self.blocks.remove(item)
            elif isinstance(item, Connection):
                item.delete_connection()

        if selected_items:
            self.statusBar().showMessage("Deleted selected items", 2000)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    editor = BlockEditor()
    editor.show()
    sys.exit(app.exec())