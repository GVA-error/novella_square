import os
import threading
import cv2
import keyboard
import numpy as np
import pyperclip
from PIL import Image
from PyQt6.QtCore import Qt, QTimer, pyqtSlot, QRect, QThread, pyqtSignal
from PyQt6.QtGui import QPainter, QPen
from PyQt6.QtWidgets import QApplication, QWidget

from huggingface_hub import login
# from manga_ocr import MangaOcr
from paddleocr import PaddleOCR

import sys

BORDER = 20
PEN_BORDER = 30
os.environ["FLAGS_use_mkldnn"] = "0"

class Overlay(QWidget):
    def __init__(self):
        super().__init__()
        self._resizing = False
        self._resize_edges = None
        self._start_pos = None
        self._start_geometry = None
        self._handling = False
        self.worker = None

        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.FramelessWindowHint
        )

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.resize(400, 300)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.make_screen)
        # self.timer.start(1000)  # 1000 мс = 1 секунда
        # self.mocr = MangaOcr()
        self.ocr = PaddleOCR(
            lang="japan",  # японский язык
            device="cpu",
            use_doc_orientation_classify=False,
            use_doc_unwarping=False,
            use_textline_orientation=True,
            text_detection_model_name="PP-OCRv4_server_det",
            text_recognition_model_name="PP-OCRv4_server_rec",
        )

        keyboard.add_hotkey("f12", self.make_screen)
        # self.make_screen()

    def paintEvent(self, event):
        painter = QPainter(self)
        pen = QPen()
        pen.setWidth(PEN_BORDER)
        painter.setPen(pen)
        painter.drawRect(self.rect())

    # def keyPressEvent(self, event):
    #     if (
    #         event.key() == Qt.Key.Key_F12
    #     ):
    #         self.make_screen()
    #         return
    #
    #     super().keyPressEvent(event)

    def make_screen(self):
        if self._handling:
            return
        if self._resizing:
            return
        self._handling = True
        screen = QApplication.primaryScreen()
        pixmap = screen.grabWindow(
            0,
            self.x(),
            self.y(),
            self.width(),
            self.height()
        )
        pixmap.save("capture.png")

        img = cv2.imread("capture.png")

        # диапазон "почти белого"
        lower = np.array([200, 200, 200])
        upper = np.array([255, 255, 255])

        mask = cv2.inRange(img, lower, upper)

        result = cv2.bitwise_and(img, img, mask=mask)

        # cv2.imwrite("capture.png", result)


        result = self.ocr.predict("capture.png")
        text = []
        for line in result:
            text.append(' '.join(line["rec_texts"]))
        cb_text = '\n'.join(text)
        #clipboard = QApplication.clipboard()
        #clipboard.setText(cb_text)
        pyperclip.copy(cb_text)
        self._handling = False


    def _get_edges(self, pos):
        x = pos.x()
        y = pos.y()

        left = x <= BORDER
        right = x >= self.width() - BORDER
        top = y <= BORDER
        bottom = y >= self.height() - BORDER

        return left, right, top, bottom

    def mousePressEvent(self, event):
        if event.button() != Qt.MouseButton.LeftButton:
            return

        edges = self._get_edges(event.pos())

        if any(edges):
            self._resizing = True
            self._resize_edges = edges
            self._start_pos = event.globalPosition().toPoint()
            self._start_geometry = self.geometry()

    def mouseMoveEvent(self, event):
        if not self._resizing:
            return

        delta = event.globalPosition().toPoint() - self._start_pos

        left, right, top, bottom = self._resize_edges

        rect = QRect(self._start_geometry)

        if left:
            rect.setLeft(rect.left() + delta.x())

        if right:
            rect.setRight(rect.right() + delta.x())

        if top:
            rect.setTop(rect.top() + delta.y())

        if bottom:
            rect.setBottom(rect.bottom() + delta.y())

        min_width = 50
        min_height = 50

        if rect.width() >= min_width and rect.height() >= min_height:
            self.setGeometry(rect)

    def mouseReleaseEvent(self, event):
        self._resizing = False
        self._resize_edges = None



if __name__ == "__main__":
    # ocr = PaddleOCR(
    #     lang="japan",
    #     use_doc_orientation_classify=False,
    #     use_doc_unwarping=False,
    #     use_textline_orientation=False,
    #     device="cpu"
    # )
    # result = ocr.predict("capture.png")
    # text = []
    # for line in result:
    #     text.append(' '.join(line["rec_texts"]))
    # print("|".join(text))
    # result = ocr.predict("capture.png")

    app = QApplication(sys.argv)
    overlay = Overlay()
    overlay.show()
    sys.exit(app.exec())