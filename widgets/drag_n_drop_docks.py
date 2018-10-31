import sys

from PySide2.QtCore import QMimeData, Qt
from PySide2.QtGui import QDrag, QPainter, QPixmap
from PySide2.QtWidgets import QApplication, QDockWidget, QLabel, QMainWindow, QSizePolicy, QStyle, QStyleOption, QVBoxLayout


class DragFromWidget(QDockWidget):

    def __init__(self, parent=None):
        super(DragFromWidget, self).__init__(parent=parent)
        self.setLayout(QVBoxLayout())
        label = QLabel("This is a label.")
        label.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        label.setFixedSize(150, 150)
        self.layout().addWidget(label)
        self.setFixedSize(150, 150)

    def dragEnterEvent(self, event):
        print("dragEnterEvent")

    def mousePressEvent(self, event):
        label = self.childAt(event.pos())
        if not label:
            return
        hot_spot = event.pos() - label.pos()
        mime_data = QMimeData()
        mime_data.setText(label.text())
        mime_data.setData("application/x-hotspot", str(hot_spot.x()))
        pixmap = QPixmap(label.size())
        label.render(pixmap)

        drag = QDrag(self)
        drag.setMimeData(mime_data)
        drag.setPixmap(pixmap)
        drag.setHotSpot(hot_spot)

        dropAction = drag.exec_(Qt.CopyAction | Qt.MoveAction, Qt.CopyAction)
        if dropAction == Qt.MoveAction:
            label.close()

    # overide paint event and do your stuff here if needed
    # in this case I am just messing things up hahahaha
    def paintEvent(self, *args, **kwargs):
        opt = QStyleOption()
        opt.init(self)
        p = QPainter(self)
        self.style().drawPrimitive(QStyle.PE_Widget, opt, p, self)


class DragToWidget(QDockWidget):

    def __init__(self, parent=None):
        super(DragToWidget, self).__init__(parent=parent)
        self.setAcceptDrops(True)
        self.setFixedSize(150, 150)

    def dragEnterEvent(self, event):
        event.accept()

    def dropEvent(self, event):
        print(f"{event} was dropped onto me.")


class DockWidgetApp(QApplication):

    def __init__(self, *args, **kwargs):
        QApplication.__init__(self, *args)
        self.mainwindow = MainWindow()
        self.mainwindow.show()


class MainWindow(QMainWindow):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent=parent)
        self.setDockOptions(QMainWindow.AllowNestedDocks | QMainWindow.AnimatedDocks)
        self.addDockWidget(Qt.LeftDockWidgetArea, DragFromWidget())
        self.addDockWidget(Qt.RightDockWidgetArea, DragToWidget())


if __name__ == "__main__":
    app = DockWidgetApp(sys.argv)
    sys.exit(app.exec_())
