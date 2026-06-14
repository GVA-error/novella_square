from configparser import ConfigParser

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QPushButton,
    QLineEdit,
    QColorDialog, QGridLayout, QLabel, QSpinBox, QLayout,
)

from sources.capture_button import KeyCaptureButton
from sources.settings import save_settings


class SettingsDialog(QDialog):
    def __init__(self, parent, settings):
        super().__init__(parent=parent)
        self.parent = parent
        self.settings = settings

        self.capture_edit = KeyCaptureButton(
            settings.capture_hotkey
        )
        self.exit_edit = KeyCaptureButton(
            settings.exit_hotkey
        )
        self.color_button = QPushButton(
            settings.border_color
        )

        self.color_button.clicked.connect(
            self.select_color
        )
        self.border_width = QSpinBox()
        self.border_width.setMinimum(1)
        self.border_width.setMaximum(200)
        self.border_width.setValue(settings.border_width)

        layout = QGridLayout(self)

        layout.addWidget(QLabel("Capture button"), 0, 0)
        layout.addWidget(self.capture_edit, 0, 1)

        layout.addWidget(QLabel("Exit button"), 1, 0)
        layout.addWidget(self.exit_edit, 1, 1)

        layout.addWidget(QLabel("Border width"), 3, 0)
        layout.addWidget(self.border_width, 3, 1)

        layout.addWidget(QLabel("Border color"), 2, 0)
        layout.addWidget(self.color_button, 2, 1)

        self.capture_edit.key_changed.connect(self.update_settings_value)
        self.exit_edit.key_changed.connect(self.update_settings_value)

        self.capture_edit.start_capturing.connect(self.exit_edit.undo_capturing)
        self.exit_edit.start_capturing.connect(self.capture_edit.undo_capturing)

        self.border_width.valueChanged.connect(self.update_settings_value)

        self.setWindowTitle("Config")
        self.update_color_button()

        layout.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)


    def update_settings_value(self):
        self.settings.capture_hotkey = self.capture_edit.key_name
        self.settings.exit_hotkey = self.exit_edit.key_name
        self.settings.border_width = self.border_width.value()
        save_settings(self.settings)
        self.parent.update()

    def select_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.settings.border_color = color.name()
            self.update_color_button()
            self.update_settings_value()

    def update_color_button(self):
        self.color_button.setStyleSheet(f"background-color: {self.settings.border_color}; color: {self.settings.border_color}; border-radius: 4px;")

    def save_settings(self):
        config = ConfigParser()

        config["hotkeys"] = {
            "capture": self.settings.capture_hotkey,
            "exit": self.settings.exit_hotkey,
        }

        config["ocr"] = {
            "language": self.settings.language,
        }

        config["app"] = {
            "start_hidden": str(self.settings.start_hidden),
        }

        config["overlay"] = {
            "border_color": self.settings.border_color,
            "border_width": str(self.settings.border_width),
        }

        with open("config.ini", "w") as f:
            config.write(f)