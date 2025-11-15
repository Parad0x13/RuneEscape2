import os
import sys
import time
import subprocess
import threading

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget, QLineEdit, QScrollArea, QComboBox

import pygetwindow

import pynput
import pyautogui
import pywinauto

import win32gui
import win32con
import win32api
import win32ui

from win11toast import toast, notify

TICK = 0.6    # A standard RuneScape 'tick' is exactly 0.6 seconds long

# Setup the event listener to kill the software entirely
def on_exit_hotkey(): os._exit(0)    # Nice way to kill this thread and all unrelated threads
def for_canonical(f):
    return lambda k: f(exitListener.canonical(k))

#hotkey = pynput.keyboard.HotKey(pynput.keyboard.HotKey.parse("<esc>"), on_exit_hotkey)    # "<ctrl>+<alt>+r" or something like that
hotkey = pynput.keyboard.HotKey(pynput.keyboard.HotKey.parse("<ctrl>+<alt>+r"), on_exit_hotkey)    # ctrl+alt+r emulates the QoL.ahk reset
exitListener = pynput.keyboard.Listener(on_press = for_canonical(hotkey.press), on_release = for_canonical(hotkey.release))
exitListener.start()
# End exit event listener setup

def list_window_names():
    def winEnumHandler(hwnd, ctx):
        if win32gui.IsWindowVisible(hwnd):
            print(hex(hwnd), win32gui.GetWindowText(hwnd))
    win32gui.EnumWindows(winEnumHandler, None)

def list_inner_windows(whnd1):
    def callback(hwnd, hwnds):
        if win32gui.IsWindowVisible(hwnd) and win32gui.IsWindowEnabled(hwnd):
            hwnds[win32gui.GetClassName(hwnd)] = hwnd
        return True
    hwnds = {}
    win32gui.EnumChildWindows(whnd1, callback, hwnds)
    return hwnds

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

    # [BUG] Will grab any window that has RuneScape in it including YouTube videos lol
    def discover(self):
        self.launchers = pygetwindow.getWindowsWithTitle("Jagex Launcher")
        self.clients = pygetwindow.getWindowsWithTitle("RuneScape")

    def activateWindow(self, name) -> bool:
        window = None

        for launcher in self.launchers:
            if launcher.title == name:
                window = launcher
        for client in self.clients:
            if client.title == name:
                window = client

        try:
            if window:
                #window.restore()
                window.activate()
                #window.maximize()    # [TODO] Should only maximized if it was already maximized
                return True
        except:    # [TODO] Probably window was removed at some point, they will need to be purged
            print(f"Attempted to activate a window that does not exist {name}")

        return False

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("RuneEscape2")
        self.setMinimumSize(QSize(640, 400))
        #self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)

        self.accounts = QComboBox()
        setattr(self.accounts, "allItems", lambda: [self.accounts.itemText(i) for i in range(self.accounts.count())])    # IMO this shouldn't need to be done...
        self.accounts.setPlaceholderText("Select a RuneScape Window")

        focus = QPushButton("Focus Window")
        focus.clicked.connect(self.selectWindow)

        self.knownAccounts = QComboBox()
        for account in ["nsydoa", "qpldek", "tviyet", "yjargo", "izrbuz"]:
            self.knownAccounts.addItem(account)

        login = QPushButton("Login to Account")
        login.clicked.connect(self.loginAccount)

        self.logWidget = ScrollLabel()
        self.logWidget.setStyleSheet("QScrollArea { background-color: #BBBBBB; }")

        mineButton = QPushButton("Mine")
        mineButton.clicked.connect(self.doMining)

        combatButton = QPushButton("Combat")
        combatButton.clicked.connect(self.doCombat)

        layout = QVBoxLayout()
        layout.addWidget(self.accounts)
        layout.addWidget(focus)
        layout.addWidget(self.knownAccounts)
        layout.addWidget(login)
        layout.addWidget(mineButton)
        layout.addWidget(combatButton)
        layout.addWidget(self.logWidget)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.log("Booting...")

        self.rsManager = RSManager()

        # [TODO] Make sure to destroy this thread when this class is destroyed
        self.discoverThread = threading.Thread(target = self.poll_discover)
        self.discoverThread.daemon = True
        self.discoverThread.start()
        #self.discover()

    def selectWindow(self):
        a = self.accounts.currentText()
        self.rsManager.activateWindow(a)

    def log(self, data):
        self.logWidget.setText(self.logWidget.text() + "\n" + data)

    # [BUG] There is a possiblity this won't work when there are duplicate windows with the same name
    # [NOTE] I do NOT like doing this as a poll... but listening to win32's win_create/destroy seems overkill
    def poll_discover(self):    # Should be running as it's own thread
        prev = self.accounts.allItems()
        #currSelection = self.accounts.currentText()

        curr = []
        self.rsManager.discover()
        for launcher in self.rsManager.launchers:
            curr.append(launcher.title)
        for client in self.rsManager.clients:
            curr.append(client.title)

        # [TODO] Find a more elegant way to do this... this is ugly
        for item in prev:
            if item not in curr:
                i = None
                for n in range(self.accounts.count()):
                    if self.accounts.itemText(n) == item:
                        i = n
                self.accounts.removeItem(n)
    
        for item in curr:
            if item not in prev:
                self.accounts.addItem(item)

        time.sleep(1.0)
        self.poll_discover()

    # [BUG] [TODO] Verify first if that account is already open, otherwise skip or make active
    def loginAccount(self):
        name = self.knownAccounts.currentText()
        self.log(f"Logging into account {name}")

        cmd = ["C:\\Program Files\\Sandboxie-Plus\\Start.exe", "/box:" + name, "C:\\Program Files (x86)\\Jagex Launcher\\JagexLauncher.exe"]

        try:
            result = subprocess.run(cmd, capture_output = True, text = True, check = True)
            self.log("Login Success")
        except subprocess.CalledProcessError as e:
            self.log(f"Login failed with error: {e}")

    # This is a TEMP function, a TEMP one! It's supposed to be for tesing purposes only
    def doMining(self):
        window_title = self.accounts.currentText()

        if self.rsManager.activateWindow(window_title):
            notify("Starting Mining\nHover cursor over node", audio = {"silent": "true"})
            time.sleep(3.0)    # Give time to move mouse to mining position
            pos = pyautogui.position()
            while True:
                for n in range(10):
                    pyautogui.leftClick(pos)
                    time.sleep(TICK * 4)
                pyautogui.write("=")
        else:
            notify("No RuneScape client selected", audio = {"silent": "true"}, duration = "short")

    def doCombat(self):
        shouldToggleAll = True
        windows = [self.accounts.currentText()]
        if shouldToggleAll: windows = self.accounts.allItems()
        notify(f"Starting Combat for windows: {windows}", audio = {"silent": "true"})

        while True:
            for window in windows:
                if self.rsManager.activateWindow(window):
                    if window == "RuneScape": continue
                    #time.sleep(1.0)    # Generic get-ready wait

                    pyautogui.press("c")
                    #time.sleep(0.1)

                    pyautogui.press("space")
                    #time.sleep(0.5)
                    pyautogui.press("-")
                    #time.sleep(0.1)

                    pyautogui.press("`")
                    #time.sleep(0.1)
                    pyautogui.press("subtract")
                    #time.sleep(0.5)
                else:
                    notify("No RuneScape client selected", audio = {"silent": "true"}, duration = "short")

            self.rsManager.activateWindow("RuneScape")
            pyautogui.press("space")
            time.sleep(6.0)    # Prepare to cycle again
            #break

app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()
