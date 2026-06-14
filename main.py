import sys
from PyQt6.QtWidgets import QApplication

from sources.capture import Overlay


if __name__ == "__main__":
    app = QApplication(sys.argv)
    overlay = Overlay()
    overlay.show()
    sys.exit(app.exec())