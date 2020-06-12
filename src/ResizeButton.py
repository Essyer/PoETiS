from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

minimum_w_h = 200


# Allows to resize parent widget when holding pushbutton
# To use it you need to set screen_geometry in your QWidget first
class ResizeButton(QPushButton):
    def __init__(self, parent: QWidget):
        super(ResizeButton, self).__init__()
        self.parent = parent
        self.__mousePressPos = None
        self.__mouseMovePos = None

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            self.__mousePressPos = event.globalPos()
            self.__mouseMovePos = event.globalPos()
        super(ResizeButton, self).mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if event.buttons() == Qt.LeftButton:
            # adjust offset from clicked point to origin of widget
            curr_height = self.parent.height()
            curr_width = self.parent.width()
            global_pos = event.globalPos()
            diff = global_pos - self.__mouseMovePos

            new_height = curr_height + diff.y()
            new_width = curr_width + diff.x()
            if new_height < minimum_w_h:
                new_height = minimum_w_h
            if new_width < minimum_w_h:
                new_width = minimum_w_h

            self.parent.setFixedHeight(new_height)
            self.parent.setFixedWidth(new_width)

            self.__mouseMovePos = global_pos
        super(ResizeButton, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if self.__mousePressPos is not None:
            event.ignore()
            if hasattr(self.parent, "update_pos_size"):
                update_pos_size = getattr(self.parent, "update_pos_size")
                if hasattr(update_pos_size, "__call__"):
                    update_pos_size()

        else:
            super(ResizeButton, self).mouseReleaseEvent(event)
