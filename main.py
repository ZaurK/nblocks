import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QGraphicsView, QGraphicsScene,
    QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QLabel,
    QGraphicsRectItem, QGraphicsPathItem
)
from PySide6.QtGui import QPainter, QPen, QColor, QBrush, QPainterPath
from PySide6.QtCore import Qt, QPointF  # Добавлен QPointF
from blocks.camera_block import CameraBlock
from blocks.grayscale_block import GrayscaleBlock
from blocks.display_block import DisplayBlock
from connections import Connection


class BlockEditor(QMainWindow):
    # Главное окно приложения
    def __init__(self): # конструктор главного окна
        super().__init__()
        # self.statusBar().showMessage("Press 'D' for debug info", 3000)  # для визуального подтверждения:
        self.setWindowTitle("OpenCV Block Editor")
        self.setGeometry(100, 100, 1000, 700)

        # Инициализация сцены и представления
        self.scene = QGraphicsScene(self)
        self.scene.setSceneRect(0, 0, 900, 600)

        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)

        # Панель инструментов
        self.tool_panel = QWidget()
        self.tool_layout = QVBoxLayout()

        # Кнопки для добавления блоков
        self.btn_add_camera = QPushButton("Add Camera")
        self.btn_add_grayscale = QPushButton("Add Grayscale")
        self.btn_add_display = QPushButton("Add Display")
        self.btn_run = QPushButton("Run Pipeline")
        self.btn_clear = QPushButton("Clear All")

        # Добавление кнопок на панель
        self.tool_layout.addWidget(QLabel("Blocks:"))
        self.tool_layout.addWidget(self.btn_add_camera)
        self.tool_layout.addWidget(self.btn_add_grayscale)
        self.tool_layout.addWidget(self.btn_add_display)
        self.tool_layout.addStretch()
        self.tool_layout.addWidget(self.btn_run)
        self.tool_layout.addWidget(self.btn_clear)
        self.tool_panel.setLayout(self.tool_layout)
        self.tool_panel.setFixedWidth(150)

        # Основной лейаут
        main_widget = QWidget()
        main_layout = QHBoxLayout()
        main_layout.addWidget(self.tool_panel)
        main_layout.addWidget(self.view)
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # Настройка состояния редактора
        self.current_connection = None
        self.connections = []
        self.blocks = []

        # Подключение сигналов
        self.btn_add_camera.clicked.connect(self.add_camera_block)
        self.btn_add_grayscale.clicked.connect(self.add_grayscale_block)
        self.btn_add_display.clicked.connect(self.add_display_block)
        self.btn_run.clicked.connect(self.execute_pipeline)
        self.btn_clear.clicked.connect(self.clear_scene)

        # Статус бар
        self.statusBar().showMessage("Ready")

        # Настройка сетки сцены
        self.setup_scene_grid()

    # Добавьте этот метод в класс BlockEditor (можно перед mousePressEvent)
    def keyPressEvent(self, event):
        """Обработка горячих клавиш для отладки"""
        try:
            if event.key() == Qt.Key_D:  # Основная отладка
                self._debug_print_connections()
                self._debug_print_blocks_info()


            elif event.key() == Qt.Key_P:
                # Для клавиатурных событий позиция не нужна
                print("Отладочная информация активирована")

            elif event.key() == Qt.Key_H:  # Помощь
                self._debug_show_help()

        except Exception as e:
            print(f"Ошибка отладки: {str(e)}")

        super().keyPressEvent(event)

    def _debug_print_connections(self):
        """Выводит информацию о соединениях"""
        print("\n=== СОЕДИНЕНИЯ ===")
        for i, conn in enumerate(self.connections):
            start = self._find_block_by_port(conn.start_port)
            end = self._find_block_by_port(conn.end_port) if conn.end_port else None
            print(f"{i}: {start.title.toPlainText() if start else '???'} -> "
                  f"{end.title.toPlainText() if end else '???'}")

    def _debug_print_blocks_info(self):
        """Выводит информацию о блоках"""
        print("\n=== БЛОКИ ===")
        for i, block in enumerate(self.blocks):
            print(f"{i}: {block.title.toPlainText()} "
                  f"(x={block.x():.1f}, y={block.y():.1f})")
            print(f"   Входы: {[p['name'] for p in block.input_ports]}")
            print(f"   Выходы: {[p['name'] for p in block.output_ports]}")

    def _debug_print_positions(self, event):
        """Отлаживает позиции элементов"""
        mouse_pos = event.position().toPoint()
        scene_pos = self.view.mapToScene(mouse_pos)
        item = self.view.itemAt(mouse_pos)

        print("\n=== ПОЗИЦИИ ===")
        print(f"Курсор: экран({mouse_pos.x()},{mouse_pos.y()}) "
              f"сцена({scene_pos.x():.1f},{scene_pos.y():.1f})")

        if item:
            print(f"Элемент: {type(item).__name__} "
                  f"сцена({item.scenePos().x():.1f},{item.scenePos().y():.1f})")
            if hasattr(item, 'title'):
                print(f"   Название: {item.title.toPlainText()}")
        else:
            print("Нет элемента под курсором")

    def _debug_show_help(self):
        """Показывает справку"""
        help_text = """
        === ОТЛАДКА ===
        D - информация о соединениях и блоках
        P - позиция курсора и элементы
        H - эта справка
        """
        print(help_text)
        self.statusBar().showMessage("Справка выведена в консоль", 3000)

    def _find_block_by_port(self, port_item):
        """Находит блок по элементу порта"""
        for block in self.blocks:
            for port in block.input_ports + block.output_ports:
                if port['item'] == port_item:
                    return block
        return None

    def setup_scene_grid(self):
        """Добавляет сетку на сцену для удобства позиционирования"""
        pen = QPen(QColor(220, 220, 220), 1, Qt.DotLine)
        for x in range(0, 901, 50):
            self.scene.addLine(x, 0, x, 600, pen)
        for y in range(0, 601, 50):
            self.scene.addLine(0, y, 900, y, pen)

    def add_camera_block(self):
        """Добавляет блок камеры на сцену"""
        block = CameraBlock()
        block.setPos(100, 100)
        self.scene.addItem(block)
        self.blocks.append(block)
        self.statusBar().showMessage("Added Camera Block", 2000)

    def add_grayscale_block(self):
        """Добавляет ч/б блок на сцену"""
        block = GrayscaleBlock()
        block.setPos(300, 100)
        self.scene.addItem(block)
        self.blocks.append(block)
        self.statusBar().showMessage("Added Grayscale Block", 2000)

    def add_display_block(self):
        """Добавляет блок отображения на сцену"""
        block = DisplayBlock()
        block.setPos(500, 100)
        self.scene.addItem(block)
        self.blocks.append(block)
        self.statusBar().showMessage("Added Display Block", 2000)

    def clear_scene(self):
        """Очищает сцену"""
        self.scene.clear()
        self.connections.clear()
        self.blocks.clear()
        self.setup_scene_grid()
        self.statusBar().showMessage("Scene cleared", 2000)

    def execute_pipeline(self):
        """Выполняет цепочку обработки"""
        # Находим стартовый блок (камера)
        camera_block = None
        for block in self.blocks:
            if isinstance(block, CameraBlock):
                camera_block = block
                break

        if not camera_block:
            self.statusBar().showMessage("Error: No Camera Block found!", 3000)
            return

        # Получаем кадр с камеры
        frame = camera_block.execute()
        if frame is None:
            self.statusBar().showMessage("Error: Failed to capture frame", 3000)
            return

        # Обрабатываем соединенные блоки
        self.process_connected_blocks(camera_block, frame)

    def process_connected_blocks(self, start_block, input_data):
        """Обрабатывает соединенные блоки рекурсивно"""
        current_block = start_block
        current_data = input_data

        while True:
            # Находим следуюший блок
            next_block = self.find_connected_block(current_block)
            if not next_block:
                break

            # Обрабатываем данные
            try:
                current_data = next_block.execute(current_data)
                current_block = next_block
            except Exception as e:
                self.statusBar().showMessage(f"Error: {str(e)}", 3000)
                return

        self.statusBar().showMessage("Pipeline executed successfully", 2000)

    def find_connected_block(self, block):
        """Находит блок, соединенный с выходом текущего блока"""
        for conn in self.connections:
            for port in block.output_ports:
                if conn.start_port == port["item"]:
                    for target_block in self.blocks:
                        for in_port in target_block.input_ports:
                            if conn.end_port == in_port["item"]:
                                return target_block
        return None

    def _get_event_pos(self, event):
        """Возвращает позицию события для любой версии Qt"""
        if hasattr(event, 'position'):  # Для Qt6
            return event.position().toPoint()
        return event.pos()  # Для Qt5

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            pos = self._get_event_pos(event)
            item = self.view.itemAt(pos)
            if item:  # Проверяем все возможные порты
                for block in self.blocks:
                    for port in block.output_ports + block.input_ports:
                        if port["item"] == item:
                            self.current_connection = Connection(item)
                            self.scene.addItem(self.current_connection)
                            return
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        pos = self._get_event_pos(event)
        if self.current_connection:
            self.current_connection.end_port = self.view.mapToScene(pos)
            self.current_connection.update_path()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        pos = self._get_event_pos(event)
        item = self.view.itemAt(pos)
        if self.current_connection and event.button() == Qt.LeftButton:
            item = self.view.itemAt(event.position().toPoint())
            valid_connection = False

            if item:
                # Ищем блок с входным портом
                for block in self.blocks:
                    for port in block.input_ports:
                        if port["item"] == item:
                            # Проверяем, что соединяем выход с входом
                            for start_block in self.blocks:
                                for out_port in start_block.output_ports:
                                    if out_port["item"] == self.current_connection.start_port:
                                        valid_connection = True
                                        break
                            if valid_connection:
                                self.current_connection.end_port = item
                                self.connections.append(self.current_connection)
                                self.current_connection.update_path()
                                return

            # Если соединение невалидно - удаляем
            self.scene.removeItem(self.current_connection)
            self.current_connection = None
        super().mouseReleaseEvent(event)

    def print_connections(self):
        print("\nCurrent connections:")
        for conn in self.connections:
            start_block = None
            end_block = None
            for block in self.blocks:
                for port in block.output_ports:
                    if port["item"] == conn.start_port:
                        start_block = block
                for port in block.input_ports:
                    if port["item"] == conn.end_port:
                        end_block = block
            if start_block and end_block:
                print(f"{start_block.title.toPlainText()} -> {end_block.title.toPlainText()}")

    def _get_event_pos(self, event):
        """Универсальное получение позиции для разных версий PySide6"""
        if hasattr(event, 'position'):  # Новые версии PySide6
            return event.position().toPoint()
        elif hasattr(event, 'pos'):  # Старые версии PySide6/PyQt5
            return event.pos()
        else:
            return event.globalPos()  # Запасной вариант

if __name__ == "__main__":
    app = QApplication(sys.argv)
    editor = BlockEditor()
    editor.show()
    sys.exit(app.exec())