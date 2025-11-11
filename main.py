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

    def setText(self, text):
        self.label.setText(text)
        #self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())
        #self.scroll_area.verticalScrollBar().setValue(self.scroll_area.verticalScrollBar().maximum())

    def text(self):
        get_text = self.label.text()
        return get_text

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("RuneEscape2")
        self.setFixedSize(QSize(640, 400))

        button = QPushButton("Run Account")
        button.clicked.connect(self.runAccount)

        self.debug = ScrollLabel()
        text = ""
        for n in range(100):
            text += str(n) + "\n"
        self.debug.setText(text)

        layout = QVBoxLayout()
        layout.addWidget(button)
        layout.addWidget(self.debug)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    # [BUG] [TODO] Verify first if that account is already open, otherwise skip or make active
    def runAccount(self, name):
        name = "izrbuz"
        subprocess.run(["C:\\Program Files\\Sandboxie-Plus\\Start.exe", "/box:" + name, "C:\\Program Files (x86)\\Jagex Launcher\\JagexLauncher.exe"])

app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()
