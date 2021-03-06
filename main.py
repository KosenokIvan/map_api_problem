import sys
from io import BytesIO
import requests
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt
from PyQt5 import uic
from PIL import Image
from get_toponym_size import get_toponym_size


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
        self.find_btn.clicked.connect(self.find_object)
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

    def find_object(self):
        toponym_to_find = self.find_input.text()
        if not toponym_to_find:
            return
        try:
            self.map_api_worker.find_object(toponym_to_find)
        except IndexError:
            pass
        else:
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
        self.tag_coords = None

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
        if self.tag_coords is not None:
            map_params["pt"] = f"{self.tag_coords},comma"
        response = requests.get(map_api_server, params=map_params)
        if not response:
            print("Error")
            print(response.text)
            print(f"{response.status_code} ({response.reason})")
            exit()
        return response.content

    def find_object(self, toponym_to_find):
        geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"
        geocoder_params = {
            "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
            "geocode": toponym_to_find,
            "format": "json"}
        response = requests.get(geocoder_api_server, params=geocoder_params)
        if not response:
            print("Error!")
            print(response.text)
            print(f"{response.status_code} ({response.reason})")
            exit()
        json_response = response.json()
        toponym = json_response["response"]["GeoObjectCollection"][
            "featureMember"][0]["GeoObject"]
        toponym_coordinates = toponym["Point"]["pos"]
        self.longitude, self.latitude = map(float, toponym_coordinates.split(" "))
        self.tag_coords = f"{self.longitude},{self.latitude}"
        self.delta = min(max(get_toponym_size(toponym)), 90)


def excepthook(cls, value, traceback):
    sys.__excepthook__(cls, value, traceback)


if __name__ == '__main__':
    sys.excepthook = excepthook
    app = QApplication(sys.argv)
    ex = MapMainWindow()
    ex.show()
    sys.exit(app.exec())
