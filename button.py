from PySide6.QtWidgets import QApplication, QPushButton, QVBoxLayout, QWidget

def on_button_click():
    print("Кнопка нажата!")

app = QApplication([])

window = QWidget()
window.setWindowTitle("Мое первое приложение")
window.setGeometry(100, 100, 400, 300)
layout = QVBoxLayout()

button = QPushButton("Нажми меня")
button.clicked.connect(on_button_click)

layout.addWidget(button)
window.setLayout(layout)
window.show()

app.exec()