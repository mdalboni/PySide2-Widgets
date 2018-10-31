from PySide2.QtCore import QPoint, QRect, QSize, Qt
from PySide2.QtGui import QIcon, QPainter
from PySide2.QtWidgets import QApplication, QHBoxLayout, QLayout, QPushButton, QSizePolicy, QSpacerItem, QStyle, QStyleOption, QVBoxLayout, QWidget


class FatherWidget(QWidget):
    css = '''
    #panel:hover{background:rgba(0,0,0,0.3);border-radius:4px} 
    #panel{background:rgba(0,0,0,0.0);}
    '''

    def __init__(self, name=None, parent=None, image=None):
        QWidget.__init__(self, parent)
        self.image = image
        self.name = name

        # This is a good way to make reusable widgets
        self.setAccessibleName(f'WdgFather_{name}')
        self.setObjectName(f'WdgFather_{name}')

        self.setFixedSize(162, 162)
        self.setVisible(True)

        self.setup_resources()
        self.setup_ui()
        self.hideBtns()

        self.desselect()

    def setup_resources(self):
        self.share = QIcon('resources/share.png')
        self.delete = QIcon('resources/delete.png')
        self.view = QIcon('resources/view.png')

    def setup_ui(self):
        # border-image: url("") 0 0 0 0 stretch stretch; Is one way to paint the background with an image through the CSS
        self.setStyleSheet(f'''        
        #{self.accessibleName()}{{border-image: url("{self.image}") 0 0 0 0 stretch stretch;border-radius:5px}}
        QPushButton {{border:none;border-radius:2px;background:transparent}}
        QPushButton:hover{{background:rgba(102, 102, 102, 0.7)}}
        ''')
        self.setLayout(QVBoxLayout())
        self.layout().setMargin(0)

        self.widget = InnerWidget()
        self.widget.setObjectName('panel')
        self.widget.setAccessibleName('panel')
        self.widget.setLayout(QVBoxLayout())
        self.widget.layout().setMargin(10)
        self.widget.setStyleSheet(self.css)

        self.spacerH = QSpacerItem(10, 10, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.btnApply = QPushButton()
        self.btnApply.setText('')
        self.btnApply.setFixedSize(30, 30)
        self.btnApply.setIconSize(QSize(24, 24))
        self.btnApply.setIcon(self.share)
        self.btnApply.clicked.connect(self.select)

        self.btnView = QPushButton()
        self.btnView.setText('')
        self.btnView.setFixedSize(30, 30)
        self.btnView.setIcon(self.view)
        self.btnView.setIconSize(QSize(24, 24))

        self.btnRemove = QPushButton()
        self.btnRemove.setText('')
        self.btnRemove.setFixedSize(30, 30)
        self.btnRemove.setIconSize(QSize(24, 24))
        self.btnRemove.setIcon(self.delete)

        self.layoutH = QHBoxLayout(self.widget)

        self.layoutH.addItem(self.spacerH)
        self.layoutH.addWidget(self.btnApply)
        self.layoutH.addWidget(self.btnView)
        self.layoutH.addWidget(self.btnRemove)

        self.widget.layout().addLayout(self.layoutH)

        self.spacerV = QSpacerItem(10, 0, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.widget.layout().addItem(self.spacerV)

        self.layout().addWidget(self.widget)

    def hideBtns(self):
        self.btnApply.setVisible(False)
        self.btnRemove.setVisible(False)
        self.btnView.setVisible(False)

    def showBtns(self):
        self.btnApply.setVisible(True)
        self.btnRemove.setVisible(True)
        self.btnView.setVisible(True)

    def paintEvent(self, event):
        opt = QStyleOption()
        opt.init(self)
        p = QPainter(self)
        self.style().drawPrimitive(QStyle.PE_Widget, opt, p, self)

    def enterEvent(self, *args, **kwargs):
        self.showBtns()

    def leaveEvent(self, *args, **kwargs):
        self.hideBtns()

    def select(self):
        print('Button pressed')

    def desselect(self):
        self.widget.setStyleSheet(self.css)


class InnerWidget(QWidget):
    def paintEvent(self, *args, **kwargs):
        opt = QStyleOption()
        opt.init(self)
        p = QPainter(self)
        self.style().drawPrimitive(QStyle.PE_Widget, opt, p, self)


class FlowLayout(QLayout):
    def __init__(self, parent=None, margin=0, spacing=-1, spacer_fix=0):
        super(FlowLayout, self).__init__(parent)

        if parent is not None:
            self.setContentsMargins(margin, margin, margin, margin)
        self.setMargin(margin)
        self.margin_custom = margin
        self.setSpacing(spacing)
        self.spacerFix = spacer_fix

        self.itemList = []

    def __del__(self):
        item = self.takeAt(0)
        while item:
            item = self.takeAt(0)

    def addItem(self, item):
        self.itemList.append(item)

    def count(self):
        return len(self.itemList)

    def itemAt(self, index):
        if index >= 0 and index < len(self.itemList):
            return self.itemList[index]

        return None

    def takeAt(self, index):
        if index >= 0 and index < len(self.itemList):
            return self.itemList.pop(index)

        return None

    def expandingDirections(self):
        return Qt.Orientations(Qt.Orientation(0))

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        height = self.doLayout(QRect(0, 0, width, 0), True)
        return height

    def setGeometry(self, rect):
        super(FlowLayout, self).setGeometry(rect)
        self.doLayout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()

        for item in self.itemList:
            size = size.expandedTo(item.minimumSize())

        margin, _, _, _ = self.getContentsMargins()

        size += QSize(2 * margin, 2 * margin)
        return size

    def doLayout(self, rect, testOnly):
        x = rect.x()
        y = rect.y()
        lineHeight = 0

        for item in self.itemList:
            wid = item.widget()
            spaceX = self.spacing() + wid.style().layoutSpacing(QSizePolicy.PushButton, QSizePolicy.PushButton, Qt.Horizontal) - self.spacerFix
            spaceY = self.spacing() + wid.style().layoutSpacing(QSizePolicy.PushButton, QSizePolicy.PushButton, Qt.Vertical)
            nextX = x + item.sizeHint().width() + spaceX
            if nextX - spaceX > rect.right() and lineHeight > 0:
                x = rect.x()
                y = y + lineHeight + spaceY
                nextX = x + item.sizeHint().width() + spaceX
                lineHeight = 0

            if not testOnly:
                item.setGeometry(QRect(QPoint(x + self.margin_custom, y + self.margin_custom + 1), item.sizeHint()))

            x = nextX
            lineHeight = max(lineHeight, item.sizeHint().height())

        return y + lineHeight - rect.y()


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    main_wdg = QWidget()
    main_wdg.setLayout(FlowLayout())
    for i in range(1, 5):
        main_wdg.layout().addWidget(FatherWidget(image=f'resources/example_{i}.jpg'))
    main_wdg.resize(500, 550)
    main_wdg.show()
    sys.exit(app.exec_())
