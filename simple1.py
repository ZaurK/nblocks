# no part of project
import sys
from PySide6.QtWidgets import QApplication, QLabel, QWidget

app = QApplication(sys.argv)

window = QWidget()
window.setWindowTitle("Мое первое приложение")
window.setGeometry(100, 100, 400, 300)

label = QLabel("Привет, мир!", parent=window)
label.move(150, 130)

window.show()
sys.exit(app.exec())