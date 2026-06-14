from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QKeySequence
from PyQt6.QtWidgets import QPushButton


class KeyCaptureButton(QPushButton):
    key_changed = pyqtSignal()
    start_capturing = pyqtSignal()

    def __init__(self, key_name=""):
        super().__init__(key_name)

        self._capturing = False

        self.key_name = key_name

        self.clicked.connect(self.start_capture)

    def undo_capturing(self):
        self._capturing = False
        self.setText(self.key_name)

    def start_capture(self):
        self._capturing = True
        self.setText("Press key...")
        self.start_capturing.emit()

    def keyPressEvent(self, event):
        if not self._capturing:
            return super().keyPressEvent(event)

        key = event.key()

        if key == Qt.Key.Key_unknown:
            return

        self.key_name = QKeySequence(key).toString()
        self.setText(self.key_name)

        self._capturing = False
        self.key_changed.emit()