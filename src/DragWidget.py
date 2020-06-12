from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


# Allows to drag widget
class DragWidget(QWidget):
    def __init__(self, *args):
        super(DragWidget, self).__init__(*args)
        self.__mousePressPos = None
        self.__mouseMovePos = None

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            self.__mousePressPos = event.globalPos()
            self.__mouseMovePos = event.globalPos()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if event.buttons() == Qt.LeftButton:
            # adjust offset from clicked point to origin of widget
            curr_pos = self.mapToGlobal(self.pos())
            global_pos = event.globalPos()
            if self.__mouseMovePos:
                diff = global_pos - self.__mouseMovePos
                new_pos = self.mapFromGlobal(curr_pos + diff)
                if new_pos.y() < 0:
                    new_pos.setY(0)
                self.move(new_pos)
                self.__mouseMovePos = global_pos

