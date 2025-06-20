# no part of project
from PySide6.QtWidgets import (QApplication, QWidget, QLabel,
                              QLineEdit, QPushButton, QVBoxLayout)

app = QApplication([])

window = QWidget()
window.setWindowTitle("Мое первое приложение")
window.setGeometry(100, 100, 400, 300)
layout = QVBoxLayout()

label = QLabel("Введите ваше имя:")
layout.addWidget(label)

input_field = QLineEdit()
layout.addWidget(input_field)

button = QPushButton("Приветствовать")
layout.addWidget(button)

output_label = QLabel("")
layout.addWidget(output_label)

def greet():
    name = input_field.text()
    output_label.setText(f"Привет, {name}!")

button.clicked.connect(greet)

window.setLayout(layout)
window.show()

app.exec()