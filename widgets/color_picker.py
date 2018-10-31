import time
import win32api
import win32gui
from threading import Thread

from PySide2.QtCore import QEvent, Signal
from PySide2.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget
from desktopmagic.screengrab_win32 import getRectAsImage

from models.color import ColorModel, colorsys


class ColorPicker:
    def __init__(self, color_signal, mouse_signal, close_signal, size):
        self.COLOR_SIGNAL = color_signal
        self.MOUSE_SIGNAL = mouse_signal
        self.CLOSE_SIGNAL = close_signal
        self.size = size

    def screen_shot(self, rect=None):
        return getRectAsImage(rect)

    def get_rgb(self, im, x, y):
        rgb_im = im.convert('RGB')
        r, g, b = rgb_im.getpixel((x, y))
        h, s, v = colorsys.rgb_to_hsv(r, g, b)
        return ColorModel(r, g, b, h, s, v)

    def get_position(self):
        flags, hcursor, x_y = win32gui.GetCursorInfo()
        return x_y[0], x_y[1]

    def get_screen_rgb(self):
        try:
            x, y = self.get_position()
            self.MOUSE_SIGNAL.emit(x, y)
            rect = (x, y, x + self.size, y + self.size)
            im = self.screen_shot(rect)
            color_selection = []
            for y in range(0, self.size):
                for x in range(0, self.size):
                    color_selection.append(self.get_rgb(im, x, y))
            self.COLOR_SIGNAL.emit(color_selection)
        except:
            print('fail')

    def start(self):
        state_left = win32api.GetKeyState(0x01)  # Left button down = 0 or 1. Button up = -127 or -128
        state_right = win32api.GetKeyState(0x02)  # Right button down = 0 or 1. Button up = -127 or -128
        state = None
        while True:
            a = win32api.GetKeyState(0x01)
            b = win32api.GetKeyState(0x02)
            if state_right == b and a == state_left:
                self.get_screen_rgb()
            else:
                if a == -127 or a == -128:
                    self.get_screen_rgb()
                    state = True
                elif b == -127 or b == -128:
                    state = False
                break
            time.sleep(0.005)
        self.CLOSE_SIGNAL.emit(state)
        time.sleep(5)


class ColorMouseWidget(QWidget):
    COLOR_SIGNAL = Signal(list)
    CLOSE_SIGNAL = Signal(bool)
    MOUSE_POSITION = Signal(int, int)

    def __init__(self, size=5, paint_signal=None):
        QWidget.__init__(self)
        self.setFixedSize(75, 75)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.label_list = []
        self.setLayout(QVBoxLayout())
        self.layout().setSpacing(0)
        self.layout().setMargin(0)
        self.setup_ui(size)
        self.PAINT_FATHER_SIGNAL = paint_signal
        self.setup_signals()
        self.setMouseTracking(True)
        self.get_color(size)
        # self.setColor()

    def setup_ui(self, size):
        optionContentLayout = QHBoxLayout()
        optionContentLayout.setMargin(0)
        optionContentLayout.setSpacing(0)

        colorLabelLayout = QVBoxLayout()
        colorLabelLayout.setMargin(0)
        colorLabelLayout.setSpacing(0)

        for y in range(size):
            layout = QHBoxLayout()
            layout.setMargin(0)
            layout.setSpacing(0)
            for x in range(size):
                self.label_list.append(QLabel(''))
                layout.addWidget(self.label_list[len(self.label_list) - 1])
            colorLabelLayout.addLayout(layout)

        optionContentLayout.addLayout(colorLabelLayout)
        self.layout().addLayout(optionContentLayout)

    def reset(self):
        self.slider.setValue(int(self.default_value))

    def setup_signals(self):
        self.MOUSE_POSITION.connect(self.location_on_the_screen)
        self.COLOR_SIGNAL.connect(self.colorize)
        self.CLOSE_SIGNAL.connect(self.pick_color)

    def eventFilter(self, source, event):
        if event.type() == QEvent.Wheel:
            return True
        return super(ColorMouseWidget, self).eventFilter(source, event)

    def colorize(self, colors):
        i = 0
        self.colors = colors
        for color in colors:
            self.label_list[i].setStyleSheet(
                f'margin:-1px;background:rgb({color.red},{color.green},{color.blue});{"border:3px solid white;" if int((len(colors)-1)/2) == i  else "border:2px solid black"}')
            i += 1

    def pick_color(self, btn_clicked):
        if btn_clicked:
            # return colors for the father widget
            # self.PAINT_FATHER_SIGNAL.emit(self.colors)
            print('Color was selected with success.')
        else:
            print('Color picker was canceled')
        self.close()

    def get_color(self, size):
        Thread(target=lambda: ColorPicker(self.COLOR_SIGNAL, self.MOUSE_POSITION, self.CLOSE_SIGNAL, size).start(), daemon=True).start()

    def location_on_the_screen(self, x, y):
        self.move(x + 10, y + 10)


import sys

from PySide2.QtCore import Qt
from PySide2.QtWidgets import QApplication

if __name__ == '__main__':
    app = QApplication(sys.argv)
    dialog_1 = ColorMouseWidget()
    dialog_1.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
    dialog_1.show()

    app.exec_()
