import sys
import subprocess

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget, QLineEdit, QScrollArea

class ScrollLabel(QScrollArea):
    def __init__(self, *args, **kwargs):
        QScrollArea.__init__(self, *args, **kwargs)

        self.setWidgetResizable(True)

        content = QWidget(self)
        self.setWidget(content)

        lay = QVBoxLayout(content)

        self.label = QLabel(content)
        self.label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.label.setWordWrap(True)
        lay.addWidget(self.label)

    def setText(self, text, autoscroll = True):
        self.label.setText(text)

        if autoscroll:
            self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())

    def text(self):
        get_text = self.label.text()
        return get_text

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("RuneEscape2")
        self.setMinimumSize(QSize(640, 400))

        button = QPushButton("Login to Account")
        button.clicked.connect(self.loginAccount)

        self.logWidget = ScrollLabel()
        self.logWidget.setStyleSheet("QScrollArea { background-color: #BBBBBB; }")

        layout = QVBoxLayout()
        layout.addWidget(button)
        layout.addWidget(self.logWidget)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.log("Booting...")

    def log(self, data):
        self.logWidget.setText(self.logWidget.text() + "\n" + data)

    # [BUG] [TODO] Verify first if that account is already open, otherwise skip or make active
    def loginAccount(self, name):
        name = "izrbuz"
        self.log(f"Logging into account {name}")

        #subprocess.run(["C:\\Program Files\\Sandboxie-Plus\\Start.exe", "/box:" + name, "C:\\Program Files (x86)\\Jagex Launcher\\JagexLauncher.exe"])
        cmd = ["C:\\Program Files\\Sandboxie-Plus\\Start.exe", "/box:" + name, "C:\\Program Files (x86)\\Jagex Launcher\\JagexLauncher.exe"]

        try:
            result = subprocess.run(cmd, capture_output = True, text = True, check = True)
            self.log("Login Success")
        except subprocess.CalledProcessError as e:
            self.log(f"Login failed with error: {e}")

app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()
