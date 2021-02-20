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
        self.scheme_rb.toggled.connect(self.change_map_type)
        self.sputnik_rb.toggled.connect(self.change_map_type)
        self.hybrid_rb.toggled.connect(self.change_map_type)
        self.update_image()

    def update_image(self):
        binary_image = self.map_api_worker.get_image()
        image = QImage.fromData(binary_image,
                                ("png"
                                 if self.map_api_worker.get_map_type() == MapAPIWorker.SCHEME
                                 else "jpg"))
        self.image_container.setPixmap(QPixmap.fromImage(image))

    def change_map_type(self):
        if self.scheme_rb.isChecked():
            map_type = MapAPIWorker.SCHEME
        elif self.sputnik_rb.isChecked():
            map_type = MapAPIWorker.SPUTNIK
        elif self.hybrid_rb.isChecked():
            map_type = MapAPIWorker.HYBRID
        else:
            print(f"WHAT: {self.sender()}?")
            return
        self.map_api_worker.set_map_type(map_type)
        self.update_image()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_PageUp:
            delta = self.map_api_worker.get_delta()
            delta *= 1.5
            if delta <= 90:
                self.map_api_worker.set_delta(delta)
                self.update_image()
        elif event.key() == Qt.Key_PageDown:
            delta = self.map_api_worker.get_delta()
            delta /= 1.5
            if delta > .0005:
                self.map_api_worker.set_delta(delta)
                self.update_image()
        elif event.key() == Qt.Key_Up:
            latitude = self.map_api_worker.get_latitude()
            delta = self.map_api_worker.get_delta()
            latitude += delta
            self.map_api_worker.set_latitude(min(latitude, 85))
            self.update_image()
        elif event.key() == Qt.Key_Down:
            latitude = self.map_api_worker.get_latitude()
            delta = self.map_api_worker.get_delta()
            latitude -= delta
            self.map_api_worker.set_latitude(max(latitude, -85))
            self.update_image()
        elif event.key() == Qt.Key_Left:
            longitude = self.map_api_worker.get_longitude()
            delta = self.map_api_worker.get_delta()
            longitude -= delta
            longitude += 180
            longitude %= 360
            longitude -= 180
            self.map_api_worker.set_longitude(longitude)
            self.update_image()
        elif event.key() == Qt.Key_Right:
            longitude = self.map_api_worker.get_longitude()
            delta = self.map_api_worker.get_delta()
            longitude += delta
            longitude += 180
            longitude %= 360
            longitude -= 180
            self.map_api_worker.set_longitude(longitude)
            self.update_image()


class MapAPIWorker:
    SCHEME = "map"
    SPUTNIK = "sat"
    HYBRID = "sat,skl"

    def __init__(self):
        self.longitude = 139.753882
        self.latitude = 35.6817
        self.delta = .4
        self.map_type = self.SCHEME

    def get_delta(self):
        return self.delta

    def set_delta(self, value):
        self.delta = value

    def get_longitude(self):
        return self.longitude

    def set_longitude(self, value):
        self.longitude = value

    def get_latitude(self):
        return self.latitude

    def set_latitude(self, value):
        self.latitude = value

    def get_map_type(self):
        return self.map_type

    def set_map_type(self, value):
        self.map_type = value

    def get_image(self):
        map_api_server = "http://static-maps.yandex.ru/1.x/"
        map_params = {
            "ll": f"{self.longitude},{self.latitude}",
            "spn": f"{self.delta},{self.delta}",
            "l": self.map_type
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
