import os
import sys

from PySide2.QtCore import QPoint, QRectF, Qt, Signal
from PySide2.QtGui import QBrush, QColor, QPixmap
from PySide2.QtWidgets import QApplication, QFrame, QGraphicsPixmapItem, QGraphicsScene, QGraphicsView, QHBoxLayout, QPushButton, QVBoxLayout, QWidget


class ImageViewer(QWidget):
    def __init__(self, path=None, list=[], index=0):
        super(ImageViewer, self).__init__()
        self.path = path
        self.index = index
        self.list = list
        self.viewer = PhotoViewer(self)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)

        self.viewer.photoClicked.connect(self.photoClicked)

        VBlayout = QVBoxLayout(self)
        VBlayout.addWidget(self.viewer)
        VBlayout.setMargin(0)

        if len(list) > 1:
            btn_layout = QHBoxLayout()
            self.btnBack = QPushButton('<')
            self.btnBack.clicked.connect(self.lastImage)

            self.btnFoward = QPushButton('>')
            self.btnFoward.clicked.connect(self.nextImage)

            btn_layout.addWidget(self.btnBack)
            btn_layout.addWidget(self.btnFoward)

            self.layout().addLayout(btn_layout)

        self.showNormal()
        self.resize(500, 500)

    def nextImage(self):
        if self.index < len(self.list) - 1:
            self.index += 1
        else:
            self.index = 0
        self.loadImage()

    def lastImage(self):
        if self.index > 0:
            self.index -= 1
        else:
            self.index = len(self.list) - 1
        self.loadImage()

    def loadImage(self):
        path = os.path.join(self.path, self.list[self.index]).replace("\\", "/")
        self.viewer.setPhoto(QPixmap(path))

    def pixInfo(self):
        self.viewer.toggleDragMode()

    def photoClicked(self, pos):
        if self.viewer.dragMode() == QGraphicsView.NoDrag:
            pass


class PhotoViewer(QGraphicsView):
    photoClicked = Signal(QPoint)

    def __init__(self, parent):
        super(PhotoViewer, self).__init__(parent)
        self._zoom = 0
        self._empty = True
        self._scene = QGraphicsScene(self)
        self._photo = QGraphicsPixmapItem()
        self._scene.addItem(self._photo)
        self.setScene(self._scene)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setBackgroundBrush(QBrush(QColor(30, 30, 30)))
        self.setFrameShape(QFrame.NoFrame)

    def hasPhoto(self):
        return not self._empty

    def fitInView(self, scale=True):
        rect = QRectF(self._photo.pixmap().rect())
        if not rect.isNull():
            self.setSceneRect(rect)
            if self.hasPhoto():
                unity = self.transform().mapRect(QRectF(0, 0, 1, 1))
                self.scale(1 / unity.width(), 1 / unity.height())
                viewrect = self.viewport().rect()
                scenerect = self.transform().mapRect(rect)
                factor = min(viewrect.width() / scenerect.width(),
                             viewrect.height() / scenerect.height())
                self.scale(factor, factor)
            self._zoom = 0

    def setPhoto(self, pixmap=None):
        self._zoom = 0
        if pixmap and not pixmap.isNull():
            self._empty = False
            self.setDragMode(QGraphicsView.ScrollHandDrag)
            self._photo.setPixmap(pixmap)
        else:
            self._empty = True
            self.setDragMode(QGraphicsView.NoDrag)
            self._photo.setPixmap(QPixmap())
        self.fitInView()

    def wheelEvent(self, event):
        if self.hasPhoto():
            if event.angleDelta().y() > 0:
                factor = 1.05
                self._zoom += 1
            else:
                factor = 0.95
                self._zoom -= 1
            if self._zoom > 0:
                self.scale(factor, factor)
            elif self._zoom == 0:
                self.fitInView()
            else:
                if self._zoom > -10:
                    self.scale(factor, factor)
                else:
                    self._zoom = -10

    def toggleDragMode(self):
        if self.dragMode() == QGraphicsView.ScrollHandDrag:
            self.setDragMode(QGraphicsView.NoDrag)
        elif not self._photo.pixmap().isNull():
            self.setDragMode(QGraphicsView.ScrollHandDrag)

    def mousePressEvent(self, event):
        if self._photo.isUnderMouse():
            self.photoClicked.emit(QPoint(event.pos()))
        super(PhotoViewer, self).mousePressEvent(event)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = ImageViewer(path='resources/', list=['example_1.jpg', 'example_2.jpg', 'example_3.jpg', 'example_4.jpg', ])
    main.loadImage()
    main.resize(500, 500)
    main.show()
    sys.exit(app.exec_())
