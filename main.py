import sys
from io import BytesIO
import requests
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt
from PyQt5 import uic
from PIL import Image


class MapMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.map_api_worker = MapAPIWorker()
        self.initUI()

    def initUI(self):
        uic.loadUi("design.ui", self)
        self.update_image()

    def update_image(self):
        binary_image = self.map_api_worker.get_image()
        self.image_container.setPixmap(QPixmap.fromImage(QImage.fromData(binary_image, "png")))

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_PageUp:
            delta = self.map_api_worker.get_delta()
            if delta < 72:
                delta *= 1.25
                self.map_api_worker.set_delta(delta)
                self.update_image()
        elif event.key() == Qt.Key_PageDown:
            delta = self.map_api_worker.get_delta()
            if delta > .0005:
                delta /= 1.25
                self.map_api_worker.set_delta(delta)
                self.update_image()


class MapAPIWorker:
    def __init__(self):
        self.longitude = 139.753882
        self.latitude = 35.6817
        self.delta = .4

    def get_delta(self):
        return self.delta

    def set_delta(self, value):
        self.delta = value

    def get_image(self):
        map_api_server = "http://static-maps.yandex.ru/1.x/"
        map_params = {
            "ll": f"{self.longitude},{self.latitude}",
            "spn": f"{self.delta},{self.delta}",
            "l": "map"
        }
        response = requests.get(map_api_server, params=map_params)
        if not response:
            print("Error")
            print(f"{response.status_code} ({response.reason})")
            exit()
        return response.content


def excepthook(cls, value, traceback):
    sys.__excepthook__(cls, value, traceback)


if __name__ == '__main__':
    sys.excepthook = excepthook
    app = QApplication(sys.argv)
    ex = MapMainWindow()
    ex.show()
    sys.exit(app.exec())
