from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtGui import *
import sys


class ResizableRectItem(QGraphicsObject):

    rectChanged = Signal(QRect)

    def __init__(self, rect: QRect()):
        super().__init__()
        self.setAcceptHoverEvents(True)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self._rect = rect
        self._mousePressRect = None
        self._mousePressPos = None
        self._brush = QBrush(QColor(255, 0, 0, 50))
        self._pen = QPen(QColor(0, 0, 0, 0))
        self._moving = False
        self._origin = QPoint()

    def setBrush(self, brush: QBrush):
        """Set current Brush
        
        Args:
            brush (QBrush)
        """
        self._brush = brush
        self.update()

    def setPen(self, pen: QPen):
        """Set current pen 
        
        Args:
            pen (QPen)
        """
        self._pen = pen
        self.update()

    def setRect(self, rect: QRect):
        self._rect = rect
        self.update()

    def corner_rect(self) -> QRect:
        """Return resizer handler
        
        Returns:
            QRect: return coordinate 
        """
        return QRect(self._rect.right() - 10, self._rect.bottom() - 10, 10, 10)

    def boundingRect(self) -> QRectF:
        """ Override boundingRect from QGraphicsItem """
        return self._rect.adjusted(-10, -10, 10, 10)

    def paint(self, painter, option, widget=None):
        """ OVerride paint from QGraphicsItem  """

        painter.setBrush(self._brush)
        painter.drawRect(self._rect)

        if self.isSelected():
            # Draw corner
            painter.setPen(Qt.NoPen)
            painter.drawRect(self.corner_rect())

            # Draw selection
            pen = QPen(QColor(Qt.green))
            pen.setWidth(2)
            pen.setColor(Qt.lightGray)
            pen.setStyle(Qt.DotLine)
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)
            painter.drawRect(self._rect)

        self.update()

    def hoverMoveEvent(self, event: QMouseEvent):
        """ Override hover move Event : Display cursor """

        pos = event.pos()

        if self.isSelected() & self.corner_rect().contains(event.pos().toPoint()):
            self.setCursor(Qt.SizeFDiagCursor)
        else:
            self.setCursor(Qt.ArrowCursor)

        super().hoverMoveEvent(event)

    def mousePressEvent(self, event: QMouseEvent):
        """ override mouse Press Event """
        if self.isSelected() & self.corner_rect().contains(
            QPoint(event.pos().toPoint())
        ):
            self._moving = True
            self._origin = self._rect.topLeft()
        else:
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        """ Override mouse release event """
        self._moving = False
        self.rectChanged.emit(self._rect)
        super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        """ Override mouse move event """
        if self._moving:
            # If _moving is set from mousePressEvent , change geometry
            self.prepareGeometryChange()

            pos = event.pos().toPoint()

            if pos.x() >= self._origin.x():
                self._rect.setRight(pos.x())
            else:
                self._rect.setLeft(pos.x())

            if pos.y() >= self._origin.y():
                self._rect.setBottom(pos.y())
            else:
                self._rect.setTop(pos.y())
            self._rect = self._rect.normalized()
            self.update()
            return
        else:
            super().mouseMoveEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    view = QGraphicsView()
    scene = QGraphicsScene()

    view.setScene(scene)
    view.resize(800, 600)
    scene.addItem(QGraphicsPixmapItem("resources/example_3.jpg"))
    scene.addItem(ResizableRectItem(QRect(0, 0, 50, 50)))
    scene.addItem(ResizableRectItem(QRect(100, 100, 100, 100)))

    view.show()

    app.exec_()
