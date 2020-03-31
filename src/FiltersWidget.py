from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QTreeView, QPushButton
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import QPoint, Qt
import xml.etree.ElementTree as ElementTree
from src.utils import log_method_name
from src.Constants import FILTERS_PATH
import os

NUM_OF_COLUMNS = 2


class ModValueUI(object):

    def __init__(self):
        self.tree = None
        self.root = None
        self.treeView = None
        self.model = None

    def setup_ui(self, Widget):
        log_method_name()
        QWidget.__init__(self)
        self.setWindowFlags( Qt.WindowStaysOnTopHint)
        self.setStyleSheet("""
        .QWidget, QWidget {
            background-color: #565352;
        }
        QHeaderView::section{
            Background-color:#908C8A;
            border-radius:1;
        }

        QScrollBar:vertical {
            Background-color:#908C8A;
        }
        QTreeView{
            background-color:#908C8A;
        }
        QTreeView::item:open {
            background-color: #565352;
        }

        QPushButton{
            border-style: solid;
            border-width: 2px;
            border-color: #3E3E3E;
            border-radius: 5px;
            background-color: #908C8A;
            height: 15%;
        }            

        """)

        self.tree = ElementTree.parse(FILTERS_PATH)
        self.root = self.tree.getroot()
        self.treeView = QTreeView()
        self.btn_close = QPushButton("Close")
        self.btn_add = QPushButton("Add")
        self.btn_remove = QPushButton("Remove")
        self.model = QStandardItemModel()
        #self.model.itemChanged.connect(self._item_changed)
        self.model.setColumnCount(NUM_OF_COLUMNS)
        self.add_filters(self.model, self.root)
        self.treeView.setModel(self.model)
        self.model.setHorizontalHeaderLabels([self.tr("Name"), self.tr("Value")])
        layoutTree = QVBoxLayout()
        layoutBtn = QVBoxLayout()
        layoutMain = QHBoxLayout()
        layoutTree.addWidget(self.treeView)
        layoutTree.addWidget(self.btn_close)
        layoutBtn.addWidget(self.btn_add)
        layoutBtn.addWidget(self.btn_remove)
        layoutMain.addLayout(layoutTree)
        layoutMain.addLayout(layoutBtn)
        self.treeView.setColumnWidth(0, 250)
        self.treeView.setColumnWidth(1, 50)
        self.setLayout(layoutMain)

    def add_filters(self, parent, filters):
        log_method_name()
        # add items from xml to UI on app startup

        for filter in filters:
            have_child = True if len(list(filter)) > 0 else False
            name = None

            name = QStandardItem(filter.attrib['name'])
            name.setEditable(False)
            type = QStandardItem(filter.attrib['type'])
            type.setEditable(False)
            # takes only tags with item type and adds it to the tree
            for element in filter:
                if element.tag == "item":
                    item = QStandardItem(element.text)
                    item.setEditable(False)
                    parent.appendRow([name, item])

    def close_btn(self):
        log_method_name()
        self.show_hide()


class FiltersWidget(QWidget, ModValueUI):
    """ Mod values main class """

    def __init__(self, parent=None):
        log_method_name()
        super(FiltersWidget, self).__init__(parent)
        self.setup_ui(self)
        self.clicked = False
        self.btn_close.clicked.connect(self.close_btn)
        self.setWindowTitle('PoETis - mod values')
        self.setGeometry(200, 200, 390, 300)
        self.gui_state = False

    def show_hide(self):
        self.hide()

    def keyPressEvent(self, qkeyevent):
        pass

    def keyReleaseEvent(self, qkeyevent):
        pass

    def mousePressEvent(self, event):
        pass

    def mouseMoveEvent(self, event):
        pass


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    window = FiltersWidget()
    window.show()
    sys.exit(app.exec_())
