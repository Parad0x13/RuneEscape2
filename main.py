import os
import sys
import time
import subprocess

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget, QLineEdit, QScrollArea, QComboBox

#import pyautogui
import pygetwindow

import pynput
import pyautogui

# Setup the event listener to kill the software entirely
def on_exit_hotkey(): os._exit(0)    # Nice way to kill this thread and all unrelated threads
def for_canonical(f):
    return lambda k: f(exitListener.canonical(k))

hotkey = pynput.keyboard.HotKey(pynput.keyboard.HotKey.parse("<esc>"), on_exit_hotkey)    # "<ctrl>+<alt>+h" or something like that
exitListener = pynput.keyboard.Listener(on_press = for_canonical(hotkey.press), on_release = for_canonical(hotkey.release))
exitListener.start()
# End exit event listener setup

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

class RSManager():
    def __init__(self):
        print("Creating RuneScape Manager")

    def discover(self):
        self.launchers = pygetwindow.getWindowsWithTitle("Jagex Launcher")
        self.clients = pygetwindow.getWindowsWithTitle("RuneScape")

    def activateWindow(self, name):
        print(f"Attempting to activate {name}")

        window = None

        for launcher in self.launchers:
            if launcher.title == name:
                window = launcher
        for client in self.clients:
            if client.title == name:
                window = client

        try:
            if window:
                window.restore()
                window.activate()
                window.maximize()    # [TODO] Should only maximized if it was already maximized
        except:    # [TODO] Probably window was removed at some point, they will need to be purged
            pass

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("RuneEscape2")
        self.setMinimumSize(QSize(640, 400))

        self.accounts = QComboBox()
        self.accounts.setPlaceholderText("Refresh for latest Launchers and Clients")
        self.accounts.currentIndexChanged.connect(self.selectWindow)

        rediscover = QPushButton("Scan for Launchers/Clients")
        rediscover.clicked.connect(self.discover)

        login = QPushButton("Login to Account")
        login.clicked.connect(self.loginAccount)

        self.logWidget = ScrollLabel()
        self.logWidget.setStyleSheet("QScrollArea { background-color: #BBBBBB; }")

        somethingButton = QPushButton("Mine")
        somethingButton.clicked.connect(self.doSomething)

        layout = QVBoxLayout()
        layout.addWidget(self.accounts)
        layout.addWidget(rediscover)
        layout.addWidget(login)
        layout.addWidget(somethingButton)
        layout.addWidget(self.logWidget)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.log("Booting...")

        self.rsManager = RSManager()
        self.discover()

    def selectWindow(self):
        a = self.accounts.currentText()
        self.rsManager.activateWindow(a)

    def log(self, data):
        self.logWidget.setText(self.logWidget.text() + "\n" + data)

    def discover(self):
        self.log("Scanning for RuneScape Launcher and Clients...")
        self.accounts.clear()
        self.rsManager.discover()
        for launcher in self.rsManager.launchers:
            self.accounts.addItem(launcher.title)
        for client in self.rsManager.clients:
            self.accounts.addItem(client.title)

    # [BUG] [TODO] Verify first if that account is already open, otherwise skip or make active
    def loginAccount(self, name):
        name = "izrbuz"
        self.log(f"Logging into account {name}")

        cmd = ["C:\\Program Files\\Sandboxie-Plus\\Start.exe", "/box:" + name, "C:\\Program Files (x86)\\Jagex Launcher\\JagexLauncher.exe"]

        try:
            result = subprocess.run(cmd, capture_output = True, text = True, check = True)
            self.log("Login Success")
        except subprocess.CalledProcessError as e:
            self.log(f"Login failed with error: {e}")

    # This is a TEMP function, a TEMP one! It's supposed to be for tesing purposes only
    def doSomething(self):
        self.rsManager.activateWindow("[#] [izrbuz] RuneScape [#]")
        time.sleep(3.0)    # Give time to move mouse to mining position
        pos = pyautogui.position()
        while True:
            for n in range(10):
                pyautogui.leftClick(pos)
                time.sleep(3.5)
            pyautogui.write("=")

app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()
