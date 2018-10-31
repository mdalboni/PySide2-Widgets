from threading import Timer

from PySide2.QtCore import Qt
from PySide2.QtGui import QPixmap
from PySide2.QtWidgets import QApplication, QSplashScreen, QWidget, QVBoxLayout, QLabel


class Splash:
    def __init__(self):
        splash_pix = QPixmap('resources/splash.png')

        self.splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)

    def show(self):
        self.splash.show()
        self.splash.showMessage("Some message or no message", Qt.AlignTop | Qt.AlignCenter, Qt.black)

    def finish(self, form):
        self.splash.finish(form)


class WidgetBuilder:
    def __init__(self):
        self.form = None

    def build(self):
        self.form = QWidget()
        self.form.setLayout(QVBoxLayout())
        self.form.layout().addWidget(QLabel("Your App here :)"))

    def show(self):
        self.form.show()


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    splash = Splash()

    splash.show()

    builder = WidgetBuilder()

    t = Timer(5.0, builder.build)
    t.start()
    t.join()

    builder.show()
    splash.finish(builder.form)

    sys.exit(app.exec_())
