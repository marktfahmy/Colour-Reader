from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from scipy.spatial import KDTree
import webcolors


class PhotoLabel(QLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setAlignment(Qt.AlignCenter)
        self.setText("\nPlease Select an Image\n")
        self.setStyleSheet("QLabel { border: 4px dashed #aaa; }")

    def setPixmap(self, *args, **kwargs):
        super().setPixmap(*args, **kwargs)
        self.setStyleSheet("QLabel { border: 2px solid black; }")


class Template(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.photo = PhotoLabel()
        bttn = QPushButton("Browse for Image")
        bttn.clicked.connect(self.open_image)

        self.hexCode = QLabel("HEXCODE HERE")
        self.regionColor = QLabel("Waiting for Input!")
        self.RGB = QLabel("RGB HERE")

        self.grid = QGridLayout(self)
        self.grid.addWidget(bttn, 0, 0, 1, 3, Qt.AlignHCenter)
        self.grid.addWidget(self.hexCode, 1, 0, Qt.AlignHCenter)
        self.grid.addWidget(self.regionColor, 1, 1, Qt.AlignHCenter)
        self.grid.addWidget(self.RGB, 1, 2, Qt.AlignHCenter)
        self.grid.addWidget(self.photo, 2, 0, 3, 3)
        self.grid.setVerticalSpacing(10)
        self.resize(400, 200)
        self.setMouseTracking(True)
        self.disp_img = None
        self.rect_drawn = False

    def open_image(self, filename):
        if not filename:
            filename, _ = QFileDialog.getOpenFileName(self, 'Select Photo', QDir.currentPath(), 'Images (*.png *.jpg)')
            if not filename:
                return
        self.photo.setPixmap(QPixmap(filename).scaledToWidth(500))
        self.disp_img = QPixmap(filename).scaledToWidth(500).toImage()
        self.photo.mousePressEvent = self.get_pixel

    def get_pixel(self, event):
        x = event.pos().x()
        y = event.pos().y()
        c = self.disp_img.pixel(x, y)
        c_rgb = QColor(c).getRgb()
        self.hexCode.setText(f"{str(hex(c))[4:]}")
        self.RGB.setText(f"{c_rgb[0]}, {c_rgb[1]}, {c_rgb[2]}")
        self.regionColor.setText(self.get_colour((c_rgb[0], c_rgb[1], c_rgb[2])))
        self.hexCode.setStyleSheet(
            "QLabel { background-color: rgb(" + f"{c_rgb[0]}, {c_rgb[1]}, {c_rgb[2]}" + "); font: bold 16px; }")
        self.RGB.setStyleSheet(
            "QLabel { background-color: rgb(" + f"{c_rgb[0]}, {c_rgb[1]}, {c_rgb[2]}" + "); font: bold 16px; }")
        self.regionColor.setStyleSheet(
            "QLabel { background-color: rgb(" + f"{c_rgb[0]}, {c_rgb[1]}, {c_rgb[2]}" + "); font: bold 20px; }")

        if not self.rect_drawn:
            self.painter = QPainter(self.photo.pixmap())
            self.painter.setPen(QPen(Qt.red, 3))
            self.painter.drawRect(x - 5, y - 5, 10, 10)
            self.rect_drawn = [x - 5, y - 5, 10, 10]
        else:
            self.painter.setCompositionMode(QPainter.CompositionMode_Source)
            self.painter.drawRect(self.disp_img.rect())
            self.painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
            self.painter.drawRect(x - 5, y - 5, 10, 10)
            self.rect_drawn = [x - 5, y - 5, 10, 10]

    def get_colour(self, RGBinput):
        hexnames = webcolors.CSS3_HEX_TO_NAMES
        names = [n for n in hexnames.values()]
        positions = [webcolors.hex_to_rgb(p) for p in list(hexnames.keys())]
        spacedb = KDTree(positions)
        dist, index = spacedb.query(RGBinput)
        return names[index]


if __name__ == "__main__":
    app = QApplication([])
    app.setStyle("Fusion")
    window = Template()
    window.show()
    app.exec()
