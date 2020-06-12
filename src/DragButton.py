from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


# Allows to drag parent widget when holding pushbutton
# To use it you need to set screen_geometry in your QWidget first
class DragButton(QPushButton):
    def __init__(self, parent: QWidget, constant_x0: bool):
        super(DragButton, self).__init__()
        self.parent = parent
        self.__mousePressPos = None
        self.__mouseMovePos = None
        self.constantX0 = constant_x0  # left edge of screen
        self.posY = 0

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            self.__mousePressPos = event.globalPos()
            self.__mouseMovePos = event.globalPos()
        super(DragButton, self).mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if event.buttons() == Qt.LeftButton:
            # adjust offset from clicked point to origin of widget
            curr_pos = self.parent.mapToGlobal(self.parent.pos())
            global_pos = event.globalPos()
            diff = global_pos - self.__mouseMovePos
            new_pos = self.parent.mapFromGlobal(curr_pos + diff)
            if self.constantX0:
                new_pos.setX(0)
            if new_pos.y() < 0:
                new_pos.setY(0)
            if new_pos.y() > self.parent.screen_geometry.bottom() - self.parent.height():
                new_pos.setY(self.parent.screen_geometry.bottom() - self.parent.height())
            self.parent.move(new_pos)
            self.__mouseMovePos = global_pos
        super(DragButton, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if self.__mousePressPos is not None:
            moved = event.globalPos() - self.__mousePressPos
            if moved.manhattanLength() > 3:
                event.ignore()
                # print("Menu Y: %d" % self.parent.mapToGlobal(self.parent.pos()).y())
                self.posY = self.parent.mapToGlobal(self.parent.pos()).y()
            elif hasattr(self.parent, "show_hide_buttons"):
                #  Since this class is used in MainWidget AND NetWidget need to check which one is calling
                # and hide parents buttons only if it has method for that.
                #  Cannot use isinstance() because importing MainWidget would cause circular import.
                show_hide_buttons = getattr(self.parent, "show_hide_buttons")
                if hasattr(show_hide_buttons, "__call__"):
                    show_hide_buttons()

            if hasattr(self.parent, "update_pos_size"):
                update_pos_size = getattr(self.parent, "update_pos_size")
                if hasattr(update_pos_size, "__call__"):
                    update_pos_size()

        else:
            super(DragButton, self).mouseReleaseEvent(event)
